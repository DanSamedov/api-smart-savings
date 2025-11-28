# app/modules/user/schemas.py

from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import Field

from app.modules.shared.helpers import validate_password_strength


class UserUpdate(BaseModel):
    """Schema for partial update of user data."""

    full_name: Optional[str] = None
    stag: Optional[str] = Field(min_length=5, max_length=9, regex=r'^(?=[a-z0-9_]{5,9}$)(?=[^_]*_?[^_]*$)(?=.*[a-z])[a-z0-9_]+$')
    preferred_currency: Optional[str] = None
    preferred_language: Optional[str] = None
    
class ChangePasswordRequest(BaseModel):
    """Schema for update of user password, requires current password."""
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class ChangeEmailRequest(BaseModel):
    """Schema for changing the user email address with password confirmation."""
    new_email: EmailStr
    password: str
