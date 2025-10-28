# app/utils/handlers.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from core.logging import log_rate_limit_exceeded, logger
from .response import standard_response


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """429 Too Many Requests"""
    ip = get_remote_address(request)
    log_rate_limit_exceeded(request, ip=ip)

    return JSONResponse(
        content=standard_response(
            status="error",
            message="Rate limit exceeded. Please try again later."
        ),
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """422 Unprocessable Entity"""
    errors = [
        {
            "loc": err.get("loc", []),
            "msg": err.get("msg", ""),
            "type": err.get("type", "")
        }
        for err in exc.errors()
    ]

    return JSONResponse(
        content=standard_response(
            status="error",
            message="Validation failed. Please check your input.",
            data={"errors": errors}
        ),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def internal_server_error_handler(request: Request, exc: Exception):
    """500 Internal Server Error"""
    logger.error("An unexpected error occurred", exc_info=exc)

    return JSONResponse(
        content=standard_response(
            status="error",
            message="An unexpected error occurred. Please contact support if the issue persists."
        ),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
