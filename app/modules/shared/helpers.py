# app/modules/shared/helpers.py
import secrets
import string
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx


def validate_password_strength(password: str):
    """
    Validate password meets security requirements.
    
    Raises:
        ValueError: If password doesn't meet requirements
    """ 
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")


def generate_secure_code(length=6):
    return "".join(secrets.choice(string.digits) for _ in range(length))


def transform_time(time: datetime) -> str:
    """Return a user-friendly time as a string."""
    local_dt = time.astimezone(ZoneInfo("Europe/Warsaw"))
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
