# app/modules/gdpr/service.py

from typing import Optional
from datetime import datetime, timezone, timedelta

from fastapi import Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.logging import logger
from app.core.security.hashing import hash_ip
from app.core.utils.exceptions import CustomException
from app.core.utils.helpers import get_client_ip, generate_secure_code
from app.modules.auth.schemas import VerificationCodeOnlyRequest
from app.modules.email.service import EmailService, EmailType
from app.modules.user.models import User
from app.modules.user.repository import UserRepository


class GDPRService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

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
            raise CustomException.e400_bad_request(
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

        await EmailService.schedule_email(
            EmailService.send_templated_email,
            background_tasks=background_tasks,
            email_type=EmailType.ACCOUNT_DELETION_REQUEST,
            email_to=[current_user.email],
            verification_code=code
        )

    async def schedule_account_delete(
            self,
            request: Request,
            current_user: User,
            deletion_request: VerificationCodeOnlyRequest,
            background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """
        Verify the account deletion code and schedule the user's account for deletion (hard delete done by cron job).
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
            raise CustomException.e409_conflict("Account is already scheduled for deletion.")

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
            raise CustomException.e400_bad_request("Invalid or expired verification code.")

        # Update user via repository
        updates = {
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc),
            "verification_code": None,
            "verification_code_expires_at": None,
        }
        await self.user_repo.update(current_user, updates)

        # Send confirmation email
        await EmailService.schedule_email(
            EmailService.send_templated_email,
            background_tasks=background_tasks,
            email_type=EmailType.ACCOUNT_DELETION_SCHEDULED,
            email_to=[current_user.email]
        )

    # =========== TODO ===========
    async def request_data_export(self, request: Request, current_user: User,
                                background_tasks: Optional[BackgroundTasks] = None) -> None:
        raw_ip = get_client_ip(request=request)
        ip = hash_ip(raw_ip)

        user = await self.user_repo.get_by_email(str(current_user.email))

        logger.info(
            msg="GDPR Data Request",
            extra={
                "method": "POST",
                "path": "/v1/user/gdpr-request",
                "status_code": 202,
                "ip_anonymized": ip,
            },
        )
