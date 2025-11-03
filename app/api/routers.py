# app/api/routers.py

from fastapi import APIRouter

from app.api.v1.routes import auth_routes

main_router = APIRouter()

main_router.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
