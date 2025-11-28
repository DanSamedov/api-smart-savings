# app/modules/user/repository.py

from typing import Optional
from uuid import UUID

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.helpers import coerce_datetimes
from app.modules.user.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        """Add a new user to the database"""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, updates: dict) -> User:
        """
        Update fields of a user safely, handling detached instances.
        """
        # Attach the object to the current session if it's detached
        updates = coerce_datetimes(updates,
                                   ["created_at", "updated_at", "last_login_at", "verification_code_expires_at",
                                    "deleted_at"])
        await self.db.merge(user)
        for k, v in updates.items():
            setattr(user, k, v)
        await self.db.commit()
        await self.db.refresh(user)

    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Retrieve a User by ID"""
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a User by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_by_email_or_none(self, email: str) -> Optional[User]:
        """Retrieve a User by email or return None"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
