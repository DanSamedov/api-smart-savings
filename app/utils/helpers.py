# app/utils/helpers.py


def mask_ip(ip: str) -> str:
    """
    Mask IP address for logging.
    
    Examples:
        "192.168.1.100" -> "192.168.xxx"
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334" -> "2001:0db8:85a3:0000:xxxx:xxxx"
    """
    if ":" in ip:  # IPv6
        parts = ip.split(":")
        return ":".join(parts[:4]) + ":xxxx:xxxx"
    else:  # IPv4
        parts = ip.split(".")
        return ".".join(parts[:2] + ["xxx"])


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
