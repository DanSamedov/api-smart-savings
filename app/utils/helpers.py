# app/utils/helpers.py

import hashlib
import os

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
