# app/api/routes/auth_routes.py

from typing import Any

from fastapi import Request, APIRouter, Depends, status, BackgroundTasks
from sqlmodel import Session

from db.session import get_session
from models.user_model import User
from core.rate_limiter import limiter
from utils.response import standard_response
from services.auth_service import AuthService
from schemas.auth_schemas import RegisterRequest, VerifyEmailRequest


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def register(
    request: Request,
    register_request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Register a new user account.

    Accepts user registration details including email and password.
    Returns a success message prompting the user to verify their email.

    Args:
        register_request (RegisterRequest): User registration details.

    Returns:
        dict(str, Any): Success message instructing the user to check their email.

    Raises:
        HTTPException: 409 Conflict if the email is already registered.
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """

    await AuthService.register_new_user(register_request=register_request, db=db)

    return standard_response(
        status="success",
        message="Account created successfully. Please check your email to proceed.",
    )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def verify_email(
    request: Request,
    verify_email_request: VerifyEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Endpoint to verify a user's email address.

    Accepts the user's email and verification code, verifies the code,
    and activates the user account. Returns a success message upon completion.

    Args:
        verify_email_request (VerifyEmailRequest): User's email and verification code.
        db (Session): SQLModel session injected by dependency.

    Returns:
        dict(str, Any): Success message confirming email verification.

    Raises:
        HTTPException: 404 Not Found if the user account does not exist.
        HTTPException: 409 Conflict if the account is already verified.
        HTTPException: 400 Bad Request if the verification code is invalid or expired.
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await AuthService.verify_user_email(verify_email_request=verify_email_request, db=db)

    return standard_response(status="success", message="Your email has been verified successfully.")
