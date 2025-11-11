# app/modules/gdpr/service.py

from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone, timedelta

from fastapi import Request, BackgroundTasks

from app.core.config import settings
from app.core.middleware.logging import logger
from app.core.security.hashing import hash_ip
from app.core.utils.exceptions import CustomException
from app.core.utils.helpers import get_client_ip, generate_secure_code
from app.modules.auth.schemas import VerificationCodeOnlyRequest
from app.modules.user.models import User
from app.modules.shared.enums import NotificationType


class GDPRService:
    def __init__(self, user_repo, wallet_repo, notification_manager):
        self.user_repo = user_repo
        self.wallet_repo = wallet_repo
        self.notification_manager = notification_manager

    async def request_delete_account(
        self,
        current_user: User,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Initiate the account deletion process for the current user.

        Generates a time-limited verification code, updates the user record,
        and sends an email containing the verification code.
        """
        wallet = await self.wallet_repo.get_wallet_by_user_id(current_user.id)
        balance = Decimal(wallet.total_balance or 0)
        threshold = Decimal(settings.MIN_BALANCE_THRESHOLD or 0)
        if balance >= threshold:
            raise CustomException.e400_bad_request("Please withdraw the remaining funds in your wallet before requesting account deletion.")

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

        # Send deletion verification email
        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.ACCOUNT_DELETION_REQUEST,
            recipients=[current_user.email],
            context={"verification_code": code},
        )

    async def schedule_account_delete(
        self,
        request: Request,
        current_user: User,
        deletion_request: VerificationCodeOnlyRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Verify the account deletion code and schedule the user's account for deletion (hard delete done by tasks job).
        """
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

        if current_user.is_deleted:
            raise CustomException.e409_conflict("Account is already scheduled for deletion.")

        ver_code = deletion_request.verification_code
        expires_at = current_user.verification_code_expires_at

        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if (
            current_user.verification_code != ver_code
            or not current_user.verification_code_expires_at
            or expires_at < datetime.now(timezone.utc)
        ):
            raise CustomException.e400_bad_request("Invalid or expired verification code.")

        updates = {
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc),
            "verification_code": None,
            "verification_code_expires_at": None,
        }
        await self.user_repo.update(current_user, updates)

        # Send a scheduled deletion confirmation email
        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.ACCOUNT_DELETION_SCHEDULED,
            recipients=[current_user.email],
        )

    async def request_export_of_data(
        self,
        request: Request,
        current_user: User,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Handle GDPR data export request — logs, verifies user, and schedules data export job.
        """
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
                "email": user.email,
            },
        )

