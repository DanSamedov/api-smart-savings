# app/db/init_db.py

import os
from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlmodel import select

from app.db.session import get_session
from app.models.user_model import User, Role
from app.core.security import hash_password


test_emails_str = os.getenv("TEST_EMAIL_ACCOUNTS")

def init_test_accounts():
    """Initialize test accounts if they don't already exist."""
    if not test_emails_str:
        print("\n[DB INIT] (w) TEST_EMAIL_ACCOUNTS not set — skipping test account creation.", flush=True)
        return

    test_emails = [email.strip() for email in test_emails_str.split(",") if email.strip()]
    if not test_emails:
        print("\n[DB INIT] (w) No valid test emails found in TEST_EMAIL_ACCOUNTS.", flush=True)
        return

    hashed_password = hash_password("Test@123")

    with next(get_session()) as session:
        for i, email in enumerate(test_emails):
            stmt = select(User).where(User.email == email)
            existing_user = session.exec(stmt).first()

            if existing_user:
                print(f"[DB INIT] (i) Test user {email} already exists.", flush=True)
                continue

            user = User(
                email=email,
                full_name=f"Test User {i+1}",
                password_hash=hashed_password,
                is_verified=True,
                role=Role.ADMIN if i == 0 else Role.USER,
                            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_deleted=False
            )
            session.add(user)
            session.commit()
            print(f"[DB INIT] (i) Created test account: {email}", flush=True)
        

def delete_test_accounts():
    """Delete test accounts defined in TEST_EMAIL_ACCOUNTS."""
    if not test_emails_str:
        return

    test_emails = [email.strip() for email in test_emails_str.split(",") if email.strip()]
    if not test_emails:
        return

    with next(get_session()) as session:
        for email in test_emails:
            stmt = select(User).where(User.email == email)
            user = session.exec(stmt).first()
            if user:
                session.delete(user)
        session.commit()
        print(f"[DB INIT - SHUTDOWN] (i) Deleted test accounts: {', '.join(test_emails)}", flush=True)
        print()
