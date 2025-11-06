# app/api/routers.py

from fastapi import APIRouter

from app.api.v1.routes import auth
from app.api.v1.routes import user

main_router = APIRouter()

main_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
main_router.include_router(user.router, prefix="/user", tags=["User Account"])
