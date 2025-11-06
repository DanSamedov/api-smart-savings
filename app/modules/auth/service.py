# app/modules/auth/service.py

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Request, HTTPException, BackgroundTasks
from sqlmodel import Session

from app.core.config import settings
from app.core.security.jwt import create_access_token, create_password_reset_token, decode_token
from app.core.middleware.logging import logger
from app.core.security.hashing import hash_ip, hash_password, verify_password
from app.modules.user.models import User
from app.modules.auth.schemas import (
    EmailOnlyRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.modules.user.repository import UserRepository
from app.modules.email.service import EmailService, EmailType
from app.modules.email.sender import EmailSender
from app.core.utils.helpers import generate_secure_code, mask_email, transform_time, get_client_ip
from app.core.utils.exceptions import CustomException


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()

    async def register_new_user(
        self,
        register_request: RegisterRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Register a new user and initiate email verification.
        """
        # Check for existing user
        existing_user = self.user_repo.get_by_email_or_none(register_request.email)
        if existing_user:
            raise CustomException._409_conflict(
                "An account with this email already exists. Try logging in."
            )

        # Generate verification code
        verification_code = generate_secure_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        # Create user object
        new_user = User(
            email=register_request.email.lower().strip(),
            password_hash=hash_password(register_request.password),
            verification_code=verification_code,
            verification_code_expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_verified=False,
            is_deleted=False,
        )

        # Persist via repository
        self.user_repo.create(new_user)

        # Prepare email details
        email_args = {
            "email_type": EmailType.VERIFICATION,
            "email_to": [new_user.email],
            "verification_code": verification_code,
        }

        # Dispatch verification email
        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **email_args)
        else:
            await self.email_service.send_templated_email(**email_args)

    async def verify_user_email(
        self,
        verify_email_request: VerifyEmailRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Verify a user's email address using a verification code.
        """
        # Fetch user
        existing_user = self.user_repo.get_by_email_or_none(verify_email_request.email)
        if not existing_user:
            raise CustomException._404_not_found("Account does not exist.")

        # Guard: already verified
        if existing_user.is_verified:
            raise CustomException._409_conflict("Account is already verified.")

        # Normalize timezone for expiry check
        expires_at = existing_user.verification_code_expires_at
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Validate code
        if (
            existing_user.verification_code != verify_email_request.verification_code
            or not existing_user.verification_code_expires_at
            or expires_at < datetime.now(timezone.utc)
        ):
            raise CustomException._400_bad_request("Verification code is invalid or has expired.")

        # Update user via repository
        updates = {
            "is_verified": True,
            "verification_code": None,
            "verification_code_expires_at": None,
        }
        self.user_repo.update(existing_user, updates)

        # Send welcome email
        email_args = {
            "email_type": EmailType.WELCOME,
            "email_to": [existing_user.email],
        }

        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **email_args)
        else:
            await self.email_service.send_templated_email(**email_args)

    async def resend_verification_code(
        self,
        email_only_req: EmailOnlyRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Resend account verification code to a user's email address.
        """

        # Fetch user
        existing_user = self.user_repo.get_by_email_or_none(email_only_req.email)
        if not existing_user:
            raise CustomException._404_not_found("Account does not exist.")

        # Guard: already verified
        if existing_user.is_verified:
            raise CustomException._409_conflict("Account is already verified.")

        # Generate new verification code
        verification_code = generate_secure_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        # Update user via repository
        updates = {
            "verification_code": verification_code,
            "verification_code_expires_at": expires_at,
        }
        self.user_repo.update(existing_user, updates)

        # Send verification email
        email_args = {
            "email_type": EmailType.VERIFICATION,
            "email_to": [existing_user.email],
            "verification_code": verification_code,
        }

        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **email_args)
        else:
            await self.email_service.send_templated_email(**email_args)

    async def login_existing_user(
        self,
        request: Request,
        login_request: LoginRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> dict[str, Any]:
        """
        Authenticate an existing user and generate a JWT access token.
        """
        raw_ip = get_client_ip(request)
        hashed_ip = hash_ip(raw_ip)

        # Fetch user
        existing_user = self.user_repo.get_by_email_or_none(login_request.email)
        if not existing_user:
            raise CustomException._401_unauthorized("Invalid login credentials.")

        # Verify password
        if not verify_password(login_request.password, existing_user.password_hash):
            await self._handle_failed_login(existing_user, raw_ip, hashed_ip, background_tasks)
        
        # Guard: disabled/unverified users
        if not existing_user.is_enabled and existing_user.failed_login_attempts < settings.MAX_FAILED_LOGIN_ATTEMPTS:
            await self._handle_disabled_account(existing_user, raw_ip, background_tasks)

        if not existing_user.is_verified:
            raise CustomException._403_forbidden("Your account is unverified, kindly verify your email.")

        # Reactivate if marked deleted
        if existing_user.is_deleted:
            existing_user.is_deleted = False
            existing_user.deleted_at = None

        # Generate JWT
        expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRATION_TIME)
        access_token = create_access_token(
            data={"sub": existing_user.email}, token_version=existing_user.token_version
        )

        # Update login info & reset failed attempts
        updates = {
            "last_login_at": datetime.now(timezone.utc),
            "failed_login_attempts": 0,
            "last_failed_login_at": None,
        }
        self.user_repo.update(existing_user, updates)

        # Send login notification
        login_at = transform_time(existing_user.last_login_at)
        if background_tasks:
            background_tasks.add_task(
                asyncio.run,
                EmailSender.send_login_notification_email(
                    email_to=existing_user.email,
                    ip=raw_ip,
                    time=login_at,
                ),
            )
        else:
            await EmailSender.send_login_notification_email(
                email_to=existing_user.email,
                ip=raw_ip,
                time=login_at,
            )

        return {
            "token": access_token,
            "type": "bearer",
            "expiry": expire,
        }

    async def _handle_failed_login(
        self,
        user: User,
        raw_ip: str,
        hashed_ip: str,
        background_tasks: Optional[BackgroundTasks],
    ) -> None:
        """
        Increment failed login attempts and lock account if limit reached.
        """
        user.failed_login_attempts += 1
        user.last_failed_login_at = datetime.now(timezone.utc)

        logger.warning(
            msg="Failed login attempt",
            extra={
                "method": "POST",
                "path": "/v1/auth/login",
                "status_code": 401,
                "ip_anonymized": hashed_ip,
                "email": mask_email(user.email),
            },
        )

        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.is_enabled = False
            self.user_repo.update(user, {
                "is_enabled": user.is_enabled,
                "failed_login_attempts": user.failed_login_attempts,
                "last_failed_login_at": user.last_failed_login_at,
            })

            login_failed_at = transform_time(user.last_failed_login_at)

            # Send account locked email
            if background_tasks:
                background_tasks.add_task(
                    asyncio.run,
                    EmailSender.send_account_locked_email(
                        email_to=user.email,
                        ip=raw_ip,
                        time=login_failed_at,
                    ),
                )
            else:
                await EmailSender.send_account_locked_email(
                    email_to=user.email,
                    ip=raw_ip,
                    time=login_failed_at,
                )

            raise CustomException._403_forbidden(
                "Your account is temporarily locked due to failed login attempts. Check your email."
            )

        self.user_repo.update(user, {
            "failed_login_attempts": user.failed_login_attempts,
            "last_failed_login_at": user.last_failed_login_at,
        })
        raise CustomException._401_unauthorized("Invalid login credentials.")

    async def _handle_disabled_account(
        self,
        user: User,
        raw_ip: str,
        background_tasks: Optional[BackgroundTasks],
    ) -> None:
        """
        Send email for disabled account and raise forbidden error.
        """
        if background_tasks:
            background_tasks.add_task(
                asyncio.run,
                EmailSender.send_account_disabled_email(
                    email_to=user.email
                ),
            )
        else:
            await EmailSender.send_account_disabled_email(email_to=user.email)

        raise CustomException._403_forbidden(
            "Your account is disabled, kindly check your email."
        )

    async def request_password_reset(
        self,
        email_only_req: EmailOnlyRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Process a password reset request safely, without revealing whether the user exists.
        """
        user_email = email_only_req.email.lower().strip()

        # Lookup user
        existing_user = self.user_repo.get_by_email_or_none(user_email)

        # If user does not exist, log and return success silently
        if not existing_user:
            logger.warning(
                "Password reset requested for non-existent email",
                extra={"email": mask_email(user_email)},
            )
            return

        # Generate password reset token
        reset_token = create_password_reset_token(user_email)

        # Prepare email args
        email_args = {
            "email_type": EmailType.PASSWORD_RESET,
            "email_to": [user_email],
            "reset_token": reset_token,
        }

        # Send email via background tasks or await directly
        if background_tasks:
            background_tasks.add_task(self.email_service.send_templated_email, **email_args)
        else:
            await self.email_service.send_templated_email(**email_args)

    async def reset_password(
        self,
        reset_request: ResetPasswordRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        """
        Reset a user's password using a valid reset token.
        """
        try:
            # Decode and validate token
            token_data = decode_token(reset_request.reset_token)
            if token_data.get("type") != "password_reset":
                raise CustomException._400_bad_request("Invalid reset token.")

            # Fetch user
            existing_user = self.user_repo.get_by_email_or_none(token_data["sub"])
            if not existing_user:
                raise CustomException._404_not_found("Account not found.")

            # Update password and reset login state
            updates = {
                "password_hash": hash_password(reset_request.new_password),
                "failed_login_attempts": 0,
                "updated_at": datetime.now(timezone.utc),
            }

            if existing_user.last_failed_login_at is not None:
                updates["is_enabled"] = True

            self.user_repo.update(existing_user, updates)

            reset_time = transform_time(existing_user.updated_at)

            # Send password reset notification
            email_args = {
                "email_type": EmailType.PASSWORD_RESET_NOTIFICATION,
                "email_to": [existing_user.email],
                "reset_time": reset_time,
            }

            if background_tasks:
                background_tasks.add_task(self.email_service.send_templated_email, **email_args)
            else:
                await self.email_service.send_templated_email(**email_args)

            # Log success
            logger.info(
                "Password reset successful",
                extra={"email": mask_email(existing_user.email)},
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            raise CustomException._400_bad_request("Invalid or expired reset token.")

    async def logout_all_devices(self, user: User) -> None:
        """
        Invalidate all existing JWT tokens for a user by incrementing User.token_version.
        """
        updates = {"token_version": user.token_version + 1}
        self.user_repo.update(user, updates)
        