# app/core/config.py

from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings
from fastapi_mail import ConnectionConfig
from fastapi.templating import Jinja2Templates

# Template loader
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "templates" / "email")
)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


class Settings(BaseSettings):
    APP_NAME: Optional[str] = None
    APP_ENV: Optional[str] = None

    DOCS_USERNAME: Optional[str] = None
    DOCS_PASSWORD: Optional[str] = None

    ALLOWED_ORIGINS: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    JWT_SECRET_KEY: Optional[str] = None
    JWT_EXPIRATION_TIME: Optional[int] = None
    JWT_SIGNING_ALGORITHM: Optional[str] = None

    IP_HASH_SALT: Optional[str] = None
    LOG_RETENTION_DAYS: Optional[int] = None

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()


def get_mail_config():
    return ConnectionConfig(
        MAIL_USERNAME=settings.SMTP_USERNAME,
        MAIL_PASSWORD=settings.SMTP_PASSWORD,
        MAIL_FROM=settings.APP_NAME,
        MAIL_PORT=settings.SMTP_PORT,
        MAIL_SERVER=settings.SMTP_HOST,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        TEMPLATE_FOLDER=TEMPLATES_DIR,
    )
