# app/core/utils/helpers.py

from typing import Any


def mask_email(email: str) -> str:
    """
    Masks an email address for logging.

    Example:
        "johndoe@example.com" -> "joh***@example.com"
    """
    try:
        local, domain = email.split("@")
        visible = 3 if len(local) > 3 else len(local)
        masked_local = local[:visible] + "*" * (len(local) - visible)
        return f"{masked_local}@{domain}"
    except Exception:
        return "****@****"

def mask_data(data: str) -> str:
    """Mask given data (str) for logging."""
    visible = 12 if len(data) > 12 else len(data)
    return data[:visible] + "*" * (len(data) - visible)

def coerce_datetimes(updates: dict[str, Any], datetime_fields: list[str]) -> dict[str, Any]:
    from datetime import datetime
    for field in datetime_fields:
        if field in updates and isinstance(updates[field], str):
            updates[field] = datetime.fromisoformat(updates[field])
    return updates


def get_client_ip(request) -> str:
    """Get real client IP, considering proxies."""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host
