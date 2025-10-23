# app/main.py

from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

from .utils.response import standard_response
from .core.logging import log_requests
from .api.dependencies import authenticate

app = FastAPI(
    title="SmartSave API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


# =======================================
# MIDDLEWARE
# =======================================
app.middleware("http")(log_requests)





# =======================================
# ROUTERS
# =======================================




# =======================================
# EXCEPTION HANDLERS
# =======================================






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


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui(authenticated: bool = Depends(authenticate)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_ui(authenticated: bool = Depends(authenticate)):
    return get_redoc_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(authenticated: bool = Depends(authenticate)):
    return get_openapi(title="API Docs", version="1.0.0", routes=app.routes)
