# app/core/utils/response.py

from typing import Optional, Any
from datetime import datetime, timezone

from app.core.config import settings

app_name = settings.APP_NAME
app_version = settings.APP_VERSION


def standard_response(message: Optional[str], status: str = "success", data: Optional[dict] = None) -> dict[str, Any]:
    return {
        "info": f"{app_name} API - {app_version}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "message": message,
        "data": data,
    }
