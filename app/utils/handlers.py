# app/utils/handlers.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.util import get_remote_address

from app.core.logging import log_rate_limit_exceeded, logger
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


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Return original response for api docs authentication
    if (
        exc.status_code == 401
        and exc.headers is not None
        and "WWW-Authenticate" in exc.headers
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    # Otherwise
    return JSONResponse(
        status_code=exc.status_code,
        content=standard_response(
            status="error",
            message=exc.detail,
        ),
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


async def generic_exception_handler(request: Request, exc: Exception):
    """500 Internal Server Error"""
    logger.error("An unexpected error occurred", exc_info=exc)

    return JSONResponse(
        content=standard_response(
            status="error",
            message="An unexpected error occurred. Please contact support if the issue persists."
        ),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
