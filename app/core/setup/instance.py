# app/core/setup/instance.py

from fastapi import FastAPI

from app.core.config import settings
from app.core.setup.lifespan import run_lifespan

# =======================================
# APP INSTANCE
# =======================================
application = FastAPI(
    title=f"{settings.APP_NAME} API",
    version=settings.APP_VERSION or "n/a",
    description="Backend service for a smart savings app.",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=run_lifespan,
)
