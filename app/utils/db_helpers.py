# app/utils/db_helpers.py

from typing import Optional

from sqlmodel import Session, select

from app.models.user_model import User


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """Helper method to retrieve a User from database using (User.email)."""
    stmt = select(User).where(User.email == email)
    user: Optional[User] = db.exec(stmt).one_or_none()
    
    return user