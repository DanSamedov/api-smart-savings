# app/modules/user/service.py

from typing import Any, Optional
from datetime import datetime, timezone, timedelta

from fastapi import Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware. logging import logger
from app.core.utils.exceptions import CustomException
from app.modules.user.models import User
from app.modules.user.schemas import UserUpdate, ChangePasswordRequest, ChangeEmailRequest
from app.modules.auth.schemas import VerificationCodeOnlyRequest
from app.modules.email.service import EmailService, EmailType
from app.core.security.hashing import hash_password, verify_password, hash_ip
from app.core.utils.helpers import generate_secure_code, get_client_ip
from app.modules.user.repository import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()

    async def get_user_details(self, current_user: User) -> dict[str, Any]:
        """
        Prepare and return profile details of the authenticated user.
        """
        user_initial = ''.join([name[0] for name in current_user.full_name.upper().split()[:2]]) if current_user.full_name is not None else current_user.email[0].upper()

        data = {
            "email": current_user.email,
            "full_name": current_user.full_name,
            "initial": user_initial,
            "role": current_user.role,
            "is_verified": current_user.is_verified,
            "preferred_language": current_user.language_preference
        }

        return data
    
    async def update_user_details(self, update_request: UserUpdate, current_user: User) -> dict[str, str]:
        """
        Partially update currently authenticated user if any changes are provided.
        """
        update_data = update_request.model_dump(exclude_unset=True)
        # Early return if nothing to update
        if not update_data:
            return {"message": "No changes provided."}
        
        # Fetch the user (exists by JWT, so no need to validate existence)
        user = await self.user_repo.get_by_email(current_user.email)
        
        # Update only fields that were provided
        await self.user_repo.update(user, update_data)
        
        return {"message": "User details updated successfully."}
        
    async def update_user_password(self, change_password_request: ChangePasswordRequest, current_user: User, background_tasks: Optional[BackgroundTasks] = None) -> None:
        """
        Update the currently authenticated user's password, verifying the current password first.
        """
        current_pass = change_password_request.current_password
        
        # Verify old password
        if not verify_password(plain_password=current_pass, hashed_password=current_user.password_hash):
            CustomException._403_forbidden("Invalid current password.")
        
        new_hashed_password = hash_password(change_password_request.new_password)
        # Update via repository
        await self.user_repo.update(
            current_user,
            {"password_hash": new_hashed_password},
        )

        # Send password change notification email
        task_args = {
            "email_type": EmailType.PASSWORD_CHANGE_NOTIFICATION,
            "email_to": [current_user.email],
        }

        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **task_args)

    async def request_delete_account(self, current_user: User, background_tasks: Optional[BackgroundTasks] = None) -> None:        
        """
        Initiate the account deletion process for the current user.

        Generates a time-limited verification code, updates the user record,
        and sends an email containing the verification code.
        """
        # Prevent multiple active deletion requests (if applicable)
        if (
            current_user.verification_code
            and current_user.verification_code_expires_at
            and current_user.verification_code_expires_at > datetime.now(timezone.utc)
        ):
            raise CustomException._400_bad_request(
                "Account deletion already requested. Please wait until the previous code expires."
            )
    
        code = generate_secure_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        await self.user_repo.update(
            current_user,
            {
                "verification_code": code,
                "verification_code_expires_at": expires_at,
            },
        )

        email_args = {
            "email_type": EmailType.ACCOUNT_DELETION_REQUEST,
            "email_to": [current_user.email],
            "verification_code": code,
        }

        # Dispatch email
        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **email_args)
             
    async def schedule_account_delete(
        self,
        request: Request,
        current_user: User,
        deletion_request: VerificationCodeOnlyRequest,
        db: AsyncSession,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """
        Verify the account deletion code and schedule the user's account for deletion.
        """
        # Log the deletion attempt
        raw_ip = get_client_ip(request)
        ip = hash_ip(raw_ip)

        logger.info(
            msg="Account Deletion Request",
            extra={
                "method": "POST",
                "path": "/v1/user/schedule-delete",
                "status_code": 202,
                "ip_anonymized": ip,
            },
        )

        # Guard: already scheduled
        if current_user.is_deleted:
            raise CustomException._409_conflict("Account is already scheduled for deletion.")

        # Validate verification code
        ver_code = deletion_request.verification_code
        expires_at = current_user.verification_code_expires_at

        # Normalize timezone
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Invalid or expired code
        if (
            current_user.verification_code != ver_code
            or not current_user.verification_code_expires_at
            or expires_at < datetime.now(timezone.utc)
        ):
            raise CustomException._400_bad_request("Invalid or expired verification code.")

        # Update user via repository
        updates = {
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc),
            "verification_code": None,
            "verification_code_expires_at": None,
        }
        await self.user_repo.update(current_user, updates)

        # Send confirmation email
        email_args = {
            "email_type": EmailType.ACCOUNT_DELETION_SCHEDULED,
            "email_to": [current_user.email],
        }

        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **email_args)

    async def get_login_history(self, current_user: User) -> dict:
        """
        Get login activity details for a user.
        """
        return {
            "last_login": current_user.last_login_at,
            "failed_attempts": current_user.failed_login_attempts,
            "last_failed_attempt": current_user.last_failed_login_at,
            "account_status": {
                "is_enabled": current_user.is_enabled,
                "is_verified": current_user.is_verified,
                "is_deleted": current_user.is_deleted
            }
        }

    async def change_user_email(
        self,
        change_email_request: ChangeEmailRequest,
        current_user: User,
        db: AsyncSession,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """
        Change the email address for the currently authenticated user.
        """
        new_email = change_email_request.new_email.lower().strip()
        old_email = current_user.email.lower().strip()

        # Prevent redundant changes
        if new_email == old_email:
            raise CustomException._400_bad_request(
                "The new email must be different from your current email."
            )

        # Prevent email duplication
        if await self.user_repo.get_by_email(new_email):
            raise CustomException._409_conflict("An account with this email already exists.")

        # Verify user password
        if not verify_password(
            plain_password=change_email_request.password,
            hashed_password=current_user.password_hash,
        ):
            raise CustomException._403_forbidden("Invalid password.")

        # Prepare verification code and expiry
        verification_code = generate_secure_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        # Update user record through repository
        updates = {
            "email": new_email,
            "is_verified": False,
            "verification_code": verification_code,
            "verification_code_expires_at": expires_at,
            "token_version": current_user.token_version + 1,  # invalidate existing tokens
        }

        await self.user_repo.update(current_user, updates)

        # Send verification email
        email_args = {
            "email_type": EmailType.VERIFICATION,
            "email_to": [new_email],
            "verification_code": verification_code,
        }

        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **email_args)


# =========== TODO ===========
    async def request_data_gdpr(self, request: Request, current_user: User, background_tasks: Optional[BackgroundTasks] = None) -> None:
        raw_ip = get_client_ip(request=request)
        ip = hash_ip(raw_ip)

        user = await self.user_repo.get_by_email(current_user.email)
        
        logger.info(
            msg="GDPR Data Request",
            extra={
                "method": "POST",
                "path": "/v1/user/gdpr-request",
                "status_code": 202,
                "ip_anonymized": ip,
                },
            )
