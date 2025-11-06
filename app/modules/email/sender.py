# app/modules/email/sender.py

from app.modules.email.service import EmailService, EmailType
from app.core.utils.helpers import get_location_from_ip


class EmailSender:
    @staticmethod
    async def send_account_disabled_email(email_to: str):
        await EmailService.send_templated_email(
            email_type=EmailType.ACCOUNT_DISABLED,
            email_to=[email_to]
        )


    @staticmethod
    async def send_account_locked_email(email_to: str, ip: str, time: str):
        location = await get_location_from_ip(ip)
        await EmailService.send_templated_email(
            email_type=EmailType.ACCOUNT_LOCKED,
            email_to=[email_to],
            ip=ip,
            time=time,
            location=location,
        )
        
            
    @staticmethod
    async def send_login_notification_email(email_to: str, ip: str, time: str):
        location = await get_location_from_ip(ip)
        await EmailService.send_templated_email(
            email_type=EmailType.LOGIN_NOTIFICATION,
            email_to=[email_to],
            ip=ip,
            time=time,
            location=location,
        )
