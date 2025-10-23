# app/main.py

from fastapi import FastAPI

from .utils.response import standard_response
from .core.logging import log_requests

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