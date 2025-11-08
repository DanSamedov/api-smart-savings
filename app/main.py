# app/main.py
import asyncio
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.dependencies import authenticate
from app.api.routers import main_router
from app.core.config import settings
from app.core.tasks.cron_jobs import anonymize_soft_deleted_users
from app.core.middleware.logging import LoggingMiddleware, cleanup_old_logs
from app.core.middleware.rate_limiter import limiter
from app.infra.database.session import set_utc_timezone
from app.infra.database.init_db import init_test_accounts, soft_delete_test_users
from app.core.utils import error_handlers
from app.core.utils.response import standard_response


# =======================================
# LIFESPAN EVENTS
# =======================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context:
    - Startup: initialize test accounts (dev), soft-delete simulation, set timezone, start scheduler
    - Shutdown: stop scheduler
    """
    print(f"[STARTUP INFO] (i) Environment: {settings.APP_ENV}\n", flush=True)
    # --- Development: setup test users ---
    if settings.APP_ENV == "development":
        # 1. Initialize test accounts if missing
        await init_test_accounts()
        # 2. Soft-delete test users 14 days ago for testing anonymization
        # await soft_delete_test_users(grace_days=14)
        # 3. Run anonymization immediately to verify
        # await anonymize_soft_deleted_users()

    # --- General startup tasks ---
    cleanup_old_logs()  # Cleanup old log files
    await set_utc_timezone()  # Ensure DB session uses UTC timezone

    # --- Scheduler for production / recurring jobs ---
    scheduler = AsyncIOScheduler()
    async def run_anonymize_job():
        await anonymize_soft_deleted_users()
    scheduler.add_job(
        lambda: asyncio.create_task(run_anonymize_job()),
        trigger="interval",
        hours=settings.HARD_DELETE_CRON_INTERVAL_HOURS,
        id="anonymize_soft_deleted_users",
        replace_existing=True,
    )
    scheduler.start()
    print(
        f"[STARTUP INFO] (i) User anonymization cron job scheduled every "
        f"{settings.HARD_DELETE_CRON_INTERVAL_HOURS} hour(s)\n", flush=True
    )

    # --- Yield control to app ---
    yield

    # --- Shutdown tasks ---
    scheduler.shutdown()
    print("[SHUTDOWN INFO] Scheduler shut down\n", flush=True)


# =======================================
# APP INSTANCE
# =======================================
app_name = settings.APP_NAME
app_version = settings.APP_VERSION
app = FastAPI(
    title=f"{app_name} API",
    version=app_version or "n/a",
    description="Backend service for a smart savings app.",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)
app.state.limiter = limiter


# =======================================
# MIDDLEWARE
# =======================================
app.add_middleware(LoggingMiddleware)

if settings.ALLOWED_ORIGINS:
    if isinstance(settings.ALLOWED_ORIGINS, str):
        allowed_origins = [
            origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")
        ]
    else:
        allowed_origins = [str(origin).strip() for origin in settings.ALLOWED_ORIGINS]
else:
    allowed_origins = ["http://localhost:3195"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["authorization", "content-type", "accept", "x-requested-with"],
)


# =======================================
# ROUTERS
# =======================================
app.include_router(main_router, prefix="/v1")


# =======================================
# EXCEPTION HANDLERS
# =======================================
app.add_exception_handler(RateLimitExceeded, error_handlers.rate_limit_handler)
app.add_exception_handler(StarletteHTTPException, error_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, error_handlers.validation_exception_handler)
app.add_exception_handler(Exception, error_handlers.generic_exception_handler)


# =======================================
# BASE ROUTES
# =======================================
@app.get("/")
def root():
    """
    Base app endpoint.
    """
    return standard_response(status="success", message="API is live.")


@app.get("/docs/swagger", include_in_schema=False)
async def custom_swagger_ui(authenticated: bool = Depends(authenticate)):
    return get_swagger_ui_html(
        openapi_url="/docs/openapi.json", title=f"{app_name} API Docs"
    )


@app.get("/docs/redoc", include_in_schema=False)
async def custom_redoc_ui(authenticated: bool = Depends(authenticate)):
    return get_redoc_html(
        openapi_url="/docs/openapi.json", title=f"{app_name} API Docs"
    )


@app.get("/docs/openapi.json", include_in_schema=False)
async def openapi_json(authenticated: bool = Depends(authenticate)):
    return get_openapi(title=f"{app_name} API Docs", version=app_version or "n/a", routes=app.routes)
