# app/core/security.py

import secrets
import string
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_secure_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)
