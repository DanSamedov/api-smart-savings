# app/core/utils/exceptions.py

from fastapi import HTTPException, status


class CustomException:
    @staticmethod
    def _400_bad_request(detail: str = "Bad Request."):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
    @staticmethod
    def _401_unauthorized(detail: str = "Request Unauthorized."):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )
    @staticmethod
    def _403_forbidden(detail: str = "Request Forbidden."):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
    @staticmethod
    def _404_not_found(detail: str = "Resource Not Found."):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    @staticmethod
    def _409_conflict(detail: str = "Conflict with Request."):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
    @staticmethod
    def _500_internal_server_error(detail: str = "Internal Server Error."):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )