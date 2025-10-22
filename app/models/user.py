from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import SQLModel, Field


class Role(str, Enum):
    """Enumeration of user roles with increasing privileges."""
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class UserBase(SQLModel, table=True):
    """Base user model containing core authentication and identity fields."""

    __tablename__ = "app_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True)
    full_name: Optional[str] = Field(default=None)
    password_hash: str = Field(nullable=False)
    role: Role = Field(default=Role.USER)
    is_verified: bool = Field(default=False)
    is_enabled: bool = Field(default=True)
    is_deleted: bool = Field(default=False)


class User(UserBase):
    """Extended user model with additional profile, status, and audit fields."""

    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )
    last_login_at: Optional[datetime] = None
    profile_image: Optional[str] = None
    language_preference: Optional[str] = None
    status: Optional[str] = None
    failed_login_attempts: int = Field(default=0)
    last_failed_login_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
