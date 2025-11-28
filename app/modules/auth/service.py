# app/modules/auth/service.py

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from fastapi import Request, BackgroundTasks

from app.core.config import settings
from app.core.middleware.logging import logger
from app.core.security.jwt import (
    create_access_token,
    create_password_reset_token,
    decode_token,
)
from app.core.security.hashing import hash_ip, hash_password, verify_password
from app.modules.user.models import User
from app.modules.wallet.models import Wallet
from app.modules.auth.schemas import (
    EmailOnlyRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.modules.shared.enums import NotificationType
from app.core.utils.helpers import (
    generate_secure_code,
    mask_email,
    transform_time,
    get_client_ip,
)
from app.core.utils.exceptions import CustomException
from app.core.utils.helpers import get_location_from_ip


class AuthService:
    def __init__(self, user_repo, wallet_repo, notification_manager):
        self.user_repo = user_repo
        self.wallet_repo = wallet_repo
        self.notification_manager = notification_manager

    async def register_new_user(
        self,
        register_request: RegisterRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        if await self.user_repo.get_by_email_or_none(str(register_request.email)):
            raise CustomException.e409_conflict(
                "An account with this email already exists. Try logging in."
            )

        verification_code = generate_secure_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        new_user = User(
            email=str(register_request.email).lower().strip(),
            password_hash=hash_password(register_request.password),
            verification_code=verification_code,
            verification_code_expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_verified=False,
            is_deleted=False,
        )  # type: ignore

        await self.user_repo.create(new_user)

        # Send verification email
        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.VERIFICATION,
            recipients=[register_request.email],
            context={"verification_code": verification_code},
        )

    async def verify_user_email(
        self,
        verify_email_request: VerifyEmailRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        user = await self.user_repo.get_by_email_or_none(str(verify_email_request.email))
        if not user:
            raise CustomException.e404_not_found("Account does not exist.")
        if user.is_verified:
            raise CustomException.e409_conflict("Account is already verified.")

        expires_at = user.verification_code_expires_at
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if (
            user.verification_code != verify_email_request.verification_code
            or not expires_at
            or expires_at < datetime.now(timezone.utc)
        ):
            raise CustomException.e400_bad_request("Verification code is invalid or expired.")

        updates = {"is_verified": True, "verification_code": None, "verification_code_expires_at": None}
        await self.user_repo.update(
            user,
            updates
        )
        wallet = Wallet(user_id=user.id, total_balance=10000, locked_amount=1500) # Dummy funds for new user - App prototype
        await self.wallet_repo.create(wallet)

        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.WELCOME,
            recipients=[user.email],
        )

    async def resend_verification_code(
        self,
        email_only_req: EmailOnlyRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        user = await self.user_repo.get_by_email_or_none(str(email_only_req.email))
        if not user:
            raise CustomException.e404_not_found("Account does not exist.")
        if user.is_verified:
            raise CustomException.e409_conflict("Account already verified.")

        verification_code = generate_secure_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        updates = {"verification_code": verification_code, "verification_code_expires_at": expires_at}
        await self.user_repo.update(
            user,
            updates
        )

        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.VERIFICATION,
            recipients=[user.email],
            context={"verification_code": verification_code},
        )

    async def login_existing_user(
        self,
        request: Request,
        login_request: LoginRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> dict[str, Any]:
        raw_ip = get_client_ip(request)
        hashed_ip = hash_ip(raw_ip)
        user = await self.user_repo.get_by_email_or_none(str(login_request.email))
        if not user:
            raise CustomException.e401_unauthorized("Invalid credentials.")

        if not verify_password(login_request.password, user.password_hash):
            await self._handle_failed_login(user, raw_ip, hashed_ip, background_tasks)

        if not user.is_enabled and user.failed_login_attempts < settings.MAX_FAILED_LOGIN_ATTEMPTS:
            await self._handle_disabled_account(user, background_tasks)

        if not user.is_verified:
            raise CustomException.e403_forbidden("Account not verified. Check your email.")

        if user.is_deleted:
            user.is_deleted = False
            user.deleted_at = None

        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRATION_TIME)
        access_token = create_access_token(data={"sub": user.email}, token_version=user.token_version)

        updates = {
            "last_login_at": datetime.now(timezone.utc),
            "failed_login_attempts": 0,
            "last_failed_login_at": None,
        }
        await self.user_repo.update(user, updates)

        # Login notification
        location = await get_location_from_ip(raw_ip)
        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.LOGIN_NOTIFICATION,
            recipients=[user.email],
            context={"ip": raw_ip, "location": location, "time": transform_time(user.last_login_at)},
        )

        return {"access_token": access_token, "token_type": "bearer", "expires_at": expire.isoformat()}

    async def _handle_failed_login(
        self, user: User, raw_ip: str, hashed_ip: str, background_tasks: Optional[BackgroundTasks]
    ) -> None:
        now = datetime.now(timezone.utc)
        user.failed_login_attempts += 1
        user.last_failed_login_at = now

        logger.warning(
            "Failed login attempt",
            extra={
                "ip_anonymized": hashed_ip,
                "email": mask_email(str(user.email)),
            },
        )

        updates = {
            "failed_login_attempts": user.failed_login_attempts,
            "last_failed_login_at": now,
        }

        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.is_enabled = False
            updates["is_enabled"] = False
            await self.user_repo.update(user, updates)

            location = await get_location_from_ip(raw_ip)
            await self.notification_manager.send(
                notification_type=NotificationType.ACCOUNT_LOCKED,
                recipients=[user.email],
                context={"ip": raw_ip, "location": location, "time": transform_time(now)},
            )

            raise CustomException.e403_forbidden(
                "Your account is locked due to repeated failed attempts. Check your email."
            )

        await self.user_repo.update(user, updates)
        raise CustomException.e401_unauthorized("Invalid login credentials.")

    async def _handle_disabled_account(
        self, user: User, background_tasks: Optional[BackgroundTasks]
    ) -> None:
        await self.notification_manager.send(
            notification_type=NotificationType.ACCOUNT_DISABLED,
            recipients=[user.email],
        )
        raise CustomException.e403_forbidden("Your account is disabled. Check your email.")

    async def request_password_reset(
        self, email_only_req: EmailOnlyRequest, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        email = str(email_only_req.email).lower().strip()
        user = await self.user_repo.get_by_email_or_none(email)
        if not user:
            logger.warning("Password reset requested for non-existent email", extra={"email": mask_email(email)})
            return

        reset_token = create_password_reset_token(email)
        await self.notification_manager.schedule(
            self.notification_manager.send,
            background_tasks=background_tasks,
            notification_type=NotificationType.PASSWORD_RESET,
            recipients=[email],
            context={"reset_token": reset_token},
        )

    async def reset_password(
        self, reset_request: ResetPasswordRequest, background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        try:
            token_data = decode_token(reset_request.reset_token)
            if token_data.get("type") != "password_reset":
                raise CustomException.e400_bad_request("Invalid reset token.")

            user = await self.user_repo.get_by_email_or_none(token_data["sub"])
            if not user:
                raise CustomException.e404_not_found("Account not found.")

            updates = {
                "password_hash": hash_password(reset_request.new_password),
                "failed_login_attempts": 0,
                "updated_at": datetime.now(timezone.utc),
                "is_enabled": True,
            }

            await self.user_repo.update(user, updates)
            await self.notification_manager.schedule(
                self.notification_manager.send,
                background_tasks=background_tasks,
                notification_type=NotificationType.PASSWORD_RESET_NOTIFICATION,
                recipients=[user.email],
                context={"time": transform_time(user.updated_at)},
            )
            logger.info("Password reset successful", extra={"email": mask_email(user.email)})

        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            raise CustomException.e400_bad_request("Invalid or expired reset token.")

    async def logout_all_devices(self, user: User) -> None:
        await self.user_repo.update(user, {"token_version": user.token_version + 1})
