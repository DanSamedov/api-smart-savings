# app/core/utils/exceptions.py

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class CustomException(HTTPException):
    """
    Base class for custom application exceptions.
    Inherits from HTTPException to allow direct raising or use as a factory.
    """

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

    @classmethod
    def bad_request(cls, detail: str = "Bad Request."):
        return cls(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    @classmethod
    def unauthorized(cls, detail: str = "Request Unauthorized."):
        return cls(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    @classmethod
    def forbidden(cls, detail: str = "Request Forbidden."):
        return cls(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    @classmethod
    def not_found(cls, detail: str = "Resource Not Found."):
        return cls(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    @classmethod
    def conflict(cls, detail: str = "Conflict with Request."):
        return cls(status_code=status.HTTP_409_CONFLICT, detail=detail)

    @classmethod
    def internal_error(cls, detail: str = "Internal Server Error."):
        return cls(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    # -------------------------------------------------------------------------
    # Backward Compatibility Methods (Static Factory Methods)
    # These maintain the existing API: CustomException.e400_bad_request(...)
    # -------------------------------------------------------------------------

    @staticmethod
    def e400_bad_request(detail: str = "Bad Request."):
        raise CustomException.bad_request(detail)

    @staticmethod
    def e401_unauthorized(detail: str = "Request Unauthorized."):
        raise CustomException.unauthorized(detail)

    @staticmethod
    def e403_forbidden(detail: str = "Request Forbidden."):
        raise CustomException.forbidden(detail)

    @staticmethod
    def e404_not_found(detail: str = "Resource Not Found."):
        raise CustomException.not_found(detail)

    @staticmethod
    def e409_conflict(detail: str = "Conflict with Request."):
        raise CustomException.conflict(detail)

    @staticmethod
    def e500_internal_server_error(detail: str = "Internal Server Error."):
        raise CustomException.internal_error(detail)
