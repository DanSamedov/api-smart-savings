# app/infra/database/init_db.py

import os
from datetime import datetime, timezone

from sqlmodel import select

from app.core.security.hashing import hash_password
from app.infra.database.session import AsyncSessionLocal
from app.modules.user.models import Role, User

test_emails_str = os.getenv("TEST_EMAIL_ACCOUNTS")


async def init_test_accounts():
    """Initialize test accounts if they don't already exist."""
    if not test_emails_str:
        print(
            "\n[DB INIT] (w) TEST_EMAIL_ACCOUNTS not set — skipping test account creation.",
            flush=True,
        )
        return

    test_emails = [
        email.strip() for email in test_emails_str.split(",") if email.strip()
    ]
    if not test_emails:
        print(
            "\n[DB INIT] (w) No valid test emails found in TEST_EMAIL_ACCOUNTS.",
            flush=True,
        )
        return

    hashed_password = hash_password("Test@123")

    async with AsyncSessionLocal() as session:
        for i, email in enumerate(test_emails):
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"[DB INIT] (i) Test user {email} already exists.", flush=True)
                continue
            now = datetime.now(timezone.utc)
            
            user = User(
                email=email,
                full_name=f"Test User {i+1}",
                password_hash=hashed_password,
                is_verified=True,
                role=Role.ADMIN if i == 0 else Role.USER,
                created_at=now,
                updated_at=now,
                is_deleted=False,
            )
            session.add(user)
        await session.commit()
        print(f"[DB INIT] (i) Created test accounts: {', '.join(test_emails)}", flush=True)


async def delete_test_accounts():
    """Delete test accounts defined in TEST_EMAIL_ACCOUNTS."""
    if not test_emails_str:
        return

    test_emails = [
        email.strip() for email in test_emails_str.split(",") if email.strip()
    ]
    if not test_emails:
        return

    async with AsyncSessionLocal() as session:
        for email in test_emails:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                await session.delete(user)
        await session.commit()
        print(
            f"[DB INIT - SHUTDOWN] (i) Deleted test accounts: {', '.join(test_emails)}",
            flush=True,
        )
        print()


# # Optional helper to run outside FastAPI
# if __name__ == "__main__":
#     asyncio.run(init_test_accounts())
