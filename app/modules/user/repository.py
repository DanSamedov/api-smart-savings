# app/modules/user/repository.py

from typing import Optional

from sqlmodel import Session, select

from app.modules.user.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: str) -> Optional[User]:
        """Helper method to retrieve a User from database with User.id"""
        stmt = select(User).where(User.id == id)
        user: Optional[User] = self.db.exec(stmt).one()
        return user
    
    def get_by_email(self, email: str) -> User:
        """Helper method to retrieve a User from database with User.email"""
        stmt = select(User).where(User.email == email)
        user: User = self.db.exec(stmt).one()
        return user
    
    def get_by_email_or_none(self, email: str) -> Optional[User]:
        """Helper method to retrieve a User from database with User.email or return None if not found."""
        stmt = select(User).where(User.email == email)
        user: Optional[User] = self.db.exec(stmt).one_or_none()
        return user
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, updates: dict) -> User:
        for key, value in updates.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user