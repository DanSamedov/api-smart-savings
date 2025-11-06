# app/infra/database/session.py

from typing import AsyncGenerator
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
POSTGRES_DB = os.getenv("POSTGRES_DB")

# URL-encode the password for parsing
encoded_password = quote_plus(POSTGRES_PASSWORD)

# Async database URL
DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
)

# Async engine
async_engine = create_async_engine(DATABASE_URL, echo=False)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
) # type: ignore

# Set UTC timezone for DB
async def set_utc_timezone():
    async with AsyncSessionLocal() as session:
        await session.execute(text("SET TIMEZONE TO 'UTC';"))
        await session.commit()

# Dependency for FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
