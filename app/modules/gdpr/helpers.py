# app/modules/gdpr/helpers.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.user.models import User


async def snapshot_gdpr_for_anonymization(db: AsyncSession, user: User):
    """
    Store snapshot of user's PII in GDPRRequest before anonymization.
    Should be called right before scrubbing PII.
    Assumes user.gdpr_requests are eagerly loaded.
    """
    for req in user.gdpr_requests:
        req.user_email_snapshot = user.email
        req.user_full_name_snapshot = user.full_name
        db.add(req)

    await db.flush()
