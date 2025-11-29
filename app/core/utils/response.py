# app/core/utils/response.py

from typing import Optional, Any, List
from datetime import datetime, timezone

from pydantic import BaseModel, Field, ConfigDict

from app.core.config import settings
from app.modules.shared.enums import Role, Currency

app_name = settings.APP_NAME
app_version = settings.APP_VERSION

class BaseResponse(BaseModel):
    """Base response schema with common fields."""
    info: str = f"{app_name} API - {app_version}"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "success"
    message: str = "Request successful."

class LoginData(BaseModel):
    access_token: str
    token_type: str
    expires_at: str

class LoginResponse(BaseResponse):
    """Schema for login response."""
    data: LoginData
    message: str = "Login successful."

def standard_response(message: Optional[str], status: str = "success", data: Any = None) -> dict[str, Any]:
    return {
        "info": f"{app_name} API - {app_version}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "message": message,
        "data": data,
    }

# Admin / RBAC Responses

class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    email: str
    stag: Optional[str]
    full_name: Optional[str]
    is_enabled: bool
    is_verified: bool
    is_deleted: bool
    deleted_at: Optional[datetime]
    last_failed_login_at: Optional[datetime]
    last_login_at: Optional[datetime]
    failed_login_attempts: int
    role: Role
    preferred_currency: Currency
    preferred_language: Optional[str]
    created_at: datetime

class PaginatedUsersData(BaseModel):
    items: List[UserData]
    total: int
    page: int
    size: int
    pages: int

class PaginatedUsersResponse(BaseResponse):
    data: PaginatedUsersData

class AppMetricsData(BaseModel):
    transaction_count: int
    total_balance_sum: float
    user_count: int

class AppMetricsResponse(BaseResponse):
    data: AppMetricsData