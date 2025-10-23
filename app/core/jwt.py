# app/core/jwt.py

from datetime import datetime, timezone, timedelta
from typing import Any, Union

from jose import JWTError, jwt
from fastapi import HTTPException, status

from .config import settings

ALGORITHM = settings.JWT_SIGNING_ALGORITHM
KEY = settings.JWT_SECRET_KEY
EXPIRY = settings.JWT_EXPIRATION_TIME

def decode_token(token: str) -> dict[str, Any]:
    """Decode JWT token."""
    try:
        payload = jwt.decode(
            token, KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token could not be validated"
        ) from e
        

def create_access_token(data: dict[str, Union[str, int]]):
    """Create login access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=EXPIRY)
    to_encode.update(
        {
            "exp": expire
        }
    )
    return jwt.encode(
        to_encode, KEY,
        algorithm=ALGORITHM
    )
    
    