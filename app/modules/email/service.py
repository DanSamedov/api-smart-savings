# app/modules/email/service.py

from typing import Optional
from enum import StrEnum

from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Template

from app.core.config import TEMPLATES_DIR, get_mail_config, settings
from app.core.middleware.logging import logger
from app.core.utils.helpers import mask_email

mail_config = get_mail_config()
fm = FastMail(mail_config)

app_name = settings.APP_NAME


class EmailType(StrEnum):
    """Enum for valid email types"""

    # Auth
    WELCOME = "welcome"
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    LOGIN_NOTIFICATION = "login_notification"
    # Account
    ACCOUNT_DELETION_REQUEST = "account_deletion_request"
    ACCOUNT_DELETION_SCHEDULED = "account_deletion_scheduled"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_DISABLED = "account_disabled"
    PASSWORD_RESET_NOTIFICATION = "password_reset_notification"
    PASSWORD_CHANGE_NOTIFICATION = "password_change_notification"


class EmailService:
    @staticmethod
    async def _send_email(
        email_to: list[str],
        subject_template: str,
        template_rel_path: str,
        context: Optional[dict] = None,
    ):
        """
        Internal helper to render and send HTML emails with templated subjects.
        :param email_to: Recipient email
        :param subject_template: Subject line (can contain template variables, e.g. "{code} is your code")
        :param template_rel_path: Path relative to TEMPLATES_DIR
        :param context: Dict of template variables
        """
        context = context or {}

        try:
            # Render subject and body using same context
            subject = Template(subject_template).render(context)

            template_path = TEMPLATES_DIR / template_rel_path
            template_str = template_path.read_text()
            body = Template(template_str).render(context)

            message = MessageSchema(
                subject=subject,
                recipients=email_to,
                body=body,
                subtype=MessageType.html,
            )

            await fm.send_message(message=message)

        except Exception:
            logger.exception(
                msg=f"Failed to send email '{subject_template}' to {mask_email(email_to[0])}"
            )

    @staticmethod
    async def send_templated_email(
        email_type: EmailType,
        email_to: list[str],
        reset_token: Optional[str] = None,
        time: Optional[str] = None,
        verification_code: Optional[str] = None,
        ip: Optional[str] = None,
        location: Optional[str] = None
    ):
        try:
            email_type = EmailType(email_type)  # ensures it's a valid enum instance
        except ValueError:
            logger.exception(f"Invalid email type '{email_type}'")
            return  # or raise an exception

        if email_type == EmailType.VERIFICATION and verification_code:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] { verification_code } is your code",
                template_rel_path="auth/email-verification.html",
                context={"verification_code": verification_code},
            )
        elif email_type == EmailType.WELCOME:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] Welcome aboard!",
                template_rel_path="account/welcome.html",
            )
        elif email_type == EmailType.LOGIN_NOTIFICATION:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] Login detected",
                template_rel_path="account/notify-login.html",
                context={
                    "ip": ip,
                    "time": time,
                    "location": location
                    },
            )
        elif email_type == EmailType.PASSWORD_RESET and reset_token:
            frontend_url = "---"
            reset_link = f"{frontend_url}/u/reset-password?token={reset_token}"
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] You requested a Password Reset",
                template_rel_path="auth/password-reset.html",
                context={"reset_link": reset_link},
            )
        elif email_type == EmailType.PASSWORD_RESET_NOTIFICATION and time:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] Account Password Modified",
                template_rel_path="auth/notify-password-reset.html",
                context={"reset_time": time},
            )
        elif email_type == EmailType.PASSWORD_CHANGE_NOTIFICATION:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] Account Password Modified",
                template_rel_path="account/notify-password-change.html"
            )
        elif email_type == EmailType.ACCOUNT_DELETION_REQUEST and verification_code:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] { verification_code } is your code",
                template_rel_path="account/account-deletion.html",
                context={"verification_code": verification_code},
            )
        elif email_type == EmailType.ACCOUNT_DELETION_SCHEDULED:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}] Account Scheduled for Deletion",
                template_rel_path="account/notify-scheduled-deletion.html",
            )
        elif email_type == EmailType.ACCOUNT_LOCKED:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}][Action Required] Account Locked",
                template_rel_path="account/account-locked.html",
                context={
                    "ip": ip,
                    "time": time,
                    "location": location
                },
            )
        elif email_type == EmailType.ACCOUNT_DISABLED:
            await EmailService._send_email(
                email_to=email_to,
                subject_template=f"[{app_name}][Action Required] Account Disabled",
                template_rel_path="account/account-disabled.html"
            )
