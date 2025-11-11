# app/modules/user/service.py

from typing import Any, Optional
from datetime import datetime, timezone, timedelta

from fastapi import Request, BackgroundTasks
from app.core.utils.exceptions import CustomException
from app.modules.user.models import User
from app.modules.user.schemas import UserUpdate, ChangePasswordRequest, ChangeEmailRequest
from app.modules.shared.enums import NotificationType
from app.core.security.hashing import hash_password, verify_password
from app.core.utils.helpers import generate_secure_code


class UserService:
    def __init__(self, user_repo, notification_manager):
        self.user_repo = user_repo
        self.notification_manager = notification_manager

    @staticmethod
    async def get_user_details(current_user: User) -> dict[str, Any]:
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
            "preferred_currency": current_user.preferred_currency,
            "preferred_language": current_user.preferred_language
        }

        return data
    
    async def update_user_details(self, update_request: UserUpdate, current_user: User) -> dict[str, str]:
        """
        Partially update the currently authenticated user if any changes are provided.
        """
        update_data = update_request.model_dump(exclude_unset=True)
        # Early return if nothing to update
        if not update_data:
            return {"message": "No changes provided."}
        
        # Fetch the user (exists by JWT, so no need to validate existence)
        user = await self.user_repo.get_by_email(current_user.email)

        await self.user_repo.update(user, update_data)
        
        return {"message": "User details updated successfully."}
        
    async def update_user_password(self, change_password_request: ChangePasswordRequest, current_user: User, background_tasks: Optional[BackgroundTasks] = None) -> None:
        """
        Update the currently authenticated user's password, verifying the current password first.
        """
        current_pass = change_password_request.current_password
        
        # Verify old password
        if not verify_password(plain_password=current_pass, hashed_password=current_user.password_hash):
            CustomException.e403_forbidden("Invalid current password.")
        
        new_hashed_password = hash_password(change_password_request.new_password)
        # Update via repository
        await self.user_repo.update(
            current_user,
            {"password_hash": new_hashed_password},
        )

        # Send password change notification email
        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.PASSWORD_CHANGE_NOTIFICATION,
            recipients=[current_user.email],
        )

    @staticmethod
    async def get_login_history(current_user: User) -> dict:
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
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """
        Change the email address for the currently authenticated user.
        """
        new_email = change_email_request.new_email.lower().strip()
        old_email = current_user.email.lower().strip()

        # Prevent redundant changes
        if new_email == old_email:
            raise CustomException.e400_bad_request(
                "The new email must be different from your current email."
            )

        # Prevent email duplication
        if await self.user_repo.get_by_email(new_email):
            raise CustomException.e409_conflict("An account with this email already exists.")

        # Verify user password
        if not verify_password(
            plain_password=change_email_request.password,
            hashed_password=current_user.password_hash,
        ):
            raise CustomException.e403_forbidden("Invalid password.")

        # Prepare verification code and expiry
        verification_code = generate_secure_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        updates = {
            "email": new_email,
            "is_verified": False,
            "verification_code": verification_code,
            "verification_code_expires_at": expires_at,
            "token_version": current_user.token_version + 1,  # invalidate existing tokens
        }

        await self.user_repo.update(current_user, updates)

        # Send verification email
        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.EMAIL_CHANGE_NOTIFICATION,
            recipients=[new_email]
        )

