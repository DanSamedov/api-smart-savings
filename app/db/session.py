# app/db/session.py
import os

from sqlmodel import create_engine, Session
from alchemy import event


DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, echo=True)


@event.listens_for(engine, "connect")
def set_utc_timezone(dbapi_connection, connection_record):
    with dbapi_connection.cursor() as cursor:
        cursor.execute("SET TIMEZONE TO 'UTC';")


def get_session():
    with Session(engine) as session:
        yield session
