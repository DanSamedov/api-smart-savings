# app/modules/auth/schemas.py

from pydantic import BaseModel, EmailStr, field_validator, SecretStr

from app.modules.shared.helpers import validate_password_strength


class RegisterRequest(BaseModel):
    """Schema for user registration with password validation."""

    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        validate_password_strength(v.get_secret_value())
        return v


class LoginRequest(BaseModel):
    """Schema for user login requests."""

    email: EmailStr
    password: SecretStr


class VerifyEmailRequest(BaseModel):
    """Schema for email verification requests."""

    email: EmailStr
    verification_code: str


class EmailOnlyRequest(BaseModel):
    """Schema for email-only requests like resending verification codes."""

    email: EmailStr

class VerificationCodeOnlyRequest(BaseModel):
    """Schema for otp-only requests like confirming account deletion."""

    verification_code: str


class ResetPasswordRequest(BaseModel):
    """Schema for password reset requests with token and new password validation."""
    reset_token: str
    new_password: SecretStr

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        validate_password_strength(v.get_secret_value())
        return v
