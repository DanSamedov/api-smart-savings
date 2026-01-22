from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.config import settings
from app.modules.shared.enums import ConsentStatus, ConsentType

app_name = settings.APP_NAME
app_version = settings.APP_VERSION


class ConsentCreate(BaseModel):
    consent_type: ConsentType = ConsentType.SAVEBUDDY_AI
    version: str = "1.0"


class ConsentResponse(BaseModel):
    id: UUID
    user_id: UUID
    consent_type: ConsentType
    consent_status: ConsentStatus
    version: str
    granted_at: datetime
    revoked_at: Optional[datetime] = None


class GdprBaseResponse(BaseModel):
    """Base GDPR response schema with common fields."""

    info: str = f"{app_name} API - {app_version}"
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: str = "success"
    message: str = "Request successful."


class ConsentActionResponse(GdprBaseResponse):
    data: ConsentResponse


class ConsentCheckData(BaseModel):
    is_active: bool
    consent_id: Optional[UUID] = None


class ConsentCheckResponse(GdprBaseResponse):
    data: ConsentCheckData


class GdprSimpleResponse(GdprBaseResponse):
    data: Optional[Any] = None
