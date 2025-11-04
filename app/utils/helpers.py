# app/utils/helpers.py

import hashlib
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import httpx

SALT = os.getenv("IP_HASH_SALT")


def hash_ip(ip: str) -> str:
    return hashlib.sha256((ip + SALT).encode()).hexdigest()


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


def transform_time(time: datetime) -> str:
    """Return a user-friendly time as string."""
    local_dt = time.astimezone(ZoneInfo("Europe/London"))
    transformed = local_dt.strftime("%b %d, %Y %I:%M %p %Z")
    return transformed


async def get_location_from_ip(ip: str) -> str:
    """
    Async IP geolocation lookup (non-blocking).
    """
    url = f"https://ipapi.co/{ip}/json/"
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(url)
            data = resp.json()
        city = data.get("city")
        country = data.get("country_name")
        if city and country:
            return f"{city}, {country}"
        elif country:
            return country
        return "Unknown location"
    except Exception:
        return "Unknown location"
