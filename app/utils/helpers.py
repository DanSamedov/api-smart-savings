# app/utils/helper.py
import random


def generate_verification_code() -> str:
    """Generate a random 6-digit verification code as a string."""
    return f"{random.randint(100000, 999999)}"
