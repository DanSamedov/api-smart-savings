# app/api/dependencies.py

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import (HTTPBasic, HTTPBasicCredentials,
                              OAuth2PasswordBearer)
from sqlmodel import Session, select

from app.core.config import settings
from app.core.jwt import decode_token
from app.db.session import get_session
from app.models.user_model import User
from app.utils.db_helpers import get_user_by_email
from app.utils.exceptions import CustomException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


security = HTTPBasic()

USERNAME = settings.DOCS_USERNAME
PASSWORD = settings.DOCS_PASSWORD


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticate credentials for the API-Docs URL.
    """
    if USERNAME is None or PASSWORD is None:
        CustomException._500_internal_server_error("Configuration error, please contact the development team.")

    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Retrieve the current authenticated user from a JWT token.
    Performs token validation, version check, and account status checks.
    """

    try:
        payload = decode_token(token)
        user_email = payload.get("sub")
        token_version = payload.get("ver")

        if not user_email:
            CustomException._401_unauthorized("Invalid authentication credentials.")

        user = get_user_by_email(email=user_email, db=session)
        if not user:
            CustomException._401_unauthorized("No account found with this email.")

        # Token version check comes immediately after fetching user
        if token_version != user.token_version:
            CustomException._401_unauthorized("Token has been invalidated. Please log in again.")

        # Account status checks
        if not user.is_verified:
            CustomException._403_forbidden("Your account is not verified.")

        if user.is_deleted:
            CustomException._403_forbidden("Your account is scheduled for deletion.")

        return user

    except HTTPException:
        raise
    except Exception:
        return CustomException._401_unauthorized("Could not validate credentials.")
