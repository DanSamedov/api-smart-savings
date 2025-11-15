# app/api/v1/routes/auth.py

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.rate_limiter import limiter
from app.infra.database.session import get_session
from app.api.dependencies import get_current_user, get_auth_service
from app.modules.auth.schemas import (EmailOnlyRequest, LoginRequest,
                                      RegisterRequest, ResetPasswordRequest,
                                      VerifyEmailRequest)
from app.modules.user.models import User
from app.modules.auth.service import AuthService
from app.core.utils.response import standard_response, LoginResponse, LoginData

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def register(
    request: Request,
    register_request: RegisterRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
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
    await auth_service.register_new_user(register_request=register_request, background_tasks=background_tasks)

    return standard_response(
        status="success",
        message="Account created successfully. Please check your email to proceed.",
    )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
@limiter.limit("4/minute")
async def verify_email(
    request: Request,
    verify_email_request: VerifyEmailRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict[str, Any]:
    """
    Endpoint to verify a user's email address.
    Accepts the user's email and verification code, verifies the code,
    activates the user account, and creates a wallet for the user. Returns a success message upon completion.

    Args:
        verify_email_request (VerifyEmailRequest): User's email and verification code.

    Returns:
        dict(str, Any): Success message confirming email verification.

    Raises:
        HTTPException: 404 Not Found if the user account does not exist.
        HTTPException: 409 Conflict if the account is already verified.
        HTTPException: 400 Bad Request if the verification code is invalid or expired.
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await auth_service.verify_user_email(
        verify_email_request=verify_email_request, background_tasks=background_tasks
    )

    return standard_response(
        status="success", message="Your email has been verified successfully."
    )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
async def resend_verification(
    request: Request,
    email_request: EmailOnlyRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict[str, Any]:
    """
    Resend verification code to a user's email address.

    Accepts a user's email, generates a new verification code, and sends it
    via email. Can be used when the original verification code has expired
    or was not received.

    Args:
        email_request (EmailOnlyRequest): User's email address.

    Returns:
        dict(str, Any): Success message confirming the code was resent.

    Raises:
        HTTPException: 404 Not Found if the user account does not exist.
        HTTPException: 409 Conflict if the account is already verified.
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await auth_service.resend_verification_code(
        email_only_req=email_request,
        background_tasks=background_tasks
    )

    return standard_response(
        status="success",
        message="A new verification code has been sent to your email.",
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def reset_password(
    request: Request,
    reset_request: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict[str, Any]:
    """
    Reset a user's password using a valid reset token.

    Takes a reset token (from the reset email) and a new password.
    Validates the token, updates the password, and sends a confirmation email.

    Args:
        reset_request (ResetPasswordRequest): Reset token and new password

    Returns:
        dict[str, Any]: Success message confirming the password was reset

    Raises:
        HTTPException: 400 Bad Request if token is invalid or expired
        HTTPException: 404 Not Found if user does not exist
        HTTPException: 429 Too Many Requests if rate limit is exceeded
    """
    await auth_service.reset_password(
        reset_request=reset_request,
        background_tasks=background_tasks
    )

    return standard_response(
        status="success",
        message="Password has been reset successfully. You can now log in with your new password.",
    )


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
async def request_password_reset(
    request: Request,
    email_request: EmailOnlyRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict[str, Any]:
    """
    Request a password reset email.

    Accepts a user's email, generates a password reset token, and sends
    a reset link via email. The reset link will be valid for a limited time.

    Args:
        email_request (EmailOnlyRequest): User's email address.

    Returns:
        dict(str, Any): Success message confirming the reset email was sent.

    Raises:
        HTTPException: 404 Not Found if the user account does not exist.
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    await auth_service.request_password_reset(
        email_only_req=email_request,
        background_tasks=background_tasks
    )

    return standard_response(
        status="success",
        message="If an account exists with this email, you will receive password reset instructions.",
    )


@router.post("/logout-all", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def logout_all_devices(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict[str, Any]:
    """
    Logout from all devices by invalidating all existing tokens.
    
    Increments the user's token version, which invalidates all existing JWT tokens
    across all devices. Requires authentication with a valid token.
    
    Returns:
        dict[str, Any]: Success message confirming logout from all devices
        
    Raises:
        HTTPException: 401 Unauthorized if not authenticated
        HTTPException: 429 Too Many Requests if rate limit exceeded
    """
    await auth_service.logout_all_devices(
        user=current_user
    )
    
    return standard_response(
        status="success",
        message="Successfully logged out from all devices."
    )


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
@limiter.limit("4/minute")
async def login(
    request: Request,
    login_request: LoginRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """
    Authenticate a user and issue an access token.

    Accepts user login credentials and returns a JWT token upon successful authentication.

    Args:
        login_request (LoginRequest): User login credentials including email and password.

    Returns:
        LoginResponse: Success message with data dict containing saccess token and token details.

    Raises:
        HTTPException: 401 Unauthorized if login credentials are invalid.
        HTTPException: 403 Forbidden if the user account is disabled (restricted or locked).
        HTTPException: 403 Forbidden if the user account is not verified.
        HTTPException: 403 Forbidden after several invalid login attempts.
        HTTPException: 429 Too Many Requests if the rate limit is exceeded.
    """
    token_data = await auth_service.login_existing_user(
            request=request, login_request=login_request, background_tasks=background_tasks
        )
    response = LoginResponse(data=LoginData(**token_data))

    return response
