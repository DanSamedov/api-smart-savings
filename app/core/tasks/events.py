# app/core/tasks/events.py

from sqlalchemy import event
from sqlalchemy.orm import Session
from app.modules.user.models import User
from app.modules.gdpr.models import GDPRRequest


@event.listens_for(User, "before_delete")
def store_gdpr_user_snapshot(mapper, connection, target: User):
    """Called automatically before a User is deleted."""
    # Convert connection -> session
    session = Session(bind=connection)

    gdpr_requests = session.query(GDPRRequest).filter_by(user_id=target.id).all()
    for req in gdpr_requests:
        req.user_email_snapshot = target.email
        req.user_full_name_snapshot = target.full_name
        req.user_role_snapshot = target.role.value

    session.flush()  # ensure changes are written before delete executes
