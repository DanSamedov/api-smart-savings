# app/db/session.py
import os

from dotenv import load_dotenv
from sqlmodel import create_engine, Session, text
from sqlalchemy import event

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Build connection URL
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL, echo=True)


@event.listens_for(engine, "connect")
def set_utc_timezone(dbapi_connection, connection_record):
    with dbapi_connection.cursor() as cursor:
        cursor.execute("SET TIMEZONE TO 'UTC';")


def get_session():
    with Session(engine) as session:
        yield session
