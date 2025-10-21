# app/main.py

from fastapi import FastAPI

from .utils.response import standard_response

app = FastAPI(
    title="SmartSave API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/")
def root():
    """Base app endpoint."""
    return standard_response(status="success", message="SmartSave API is running")
