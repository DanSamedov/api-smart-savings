# app/main.py

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
from app.core.cron.jobs import hard_delete_expired_users
from app.core.middleware.logging import LoggingMiddleware, cleanup_old_logs
from app.core.middleware.rate_limiter import limiter
from app.infra.database.session import set_utc_timezone
from app.infra.database.init_db import delete_test_accounts, init_test_accounts
from app.core.utils import error_handlers
from app.core.utils.response import standard_response


# =======================================
# LIFESPAN EVENTS
# =======================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    print(f"[STARTUP INFO] (i) Environment: {settings.APP_ENV}\n", flush=True)
    if settings.APP_ENV == "development":
        await init_test_accounts()
    cleanup_old_logs() # Cleanup old log files

    await set_utc_timezone() # Set DB server to UTC
    
    # Initialize and start the scheduler for cron jobs
    scheduler = AsyncIOScheduler()
    cron_interval_hours = settings.HARD_DELETE_CRON_INTERVAL_HOURS
    
    scheduler.add_job(
        hard_delete_expired_users,
        "interval",
        hours=cron_interval_hours,
        id="hard_delete_expired_users",
        replace_existing=True,
    )
    scheduler.start()
    print(f"[STARTUP INFO] (i) Hard delete cron job scheduled to run every {cron_interval_hours} hour(s)\n", flush=True)

    yield  # App Runs

    # Shutdown Events
    scheduler.shutdown()


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

    Returns:
        Dict[str, Any]: Standard response containing API status
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
