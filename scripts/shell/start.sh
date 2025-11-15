#!/bin/shell

echo "[START SCRIPT] (i) Waiting for database to be ready..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER
do
  echo "[START SCRIPT] (i) Waiting for database connection..."
  sleep 2
done

echo "[START SCRIPT] (i) Running database migrations..."
alembic upgrade head

echo "[START SCRIPT] (i) Starting FastAPI application..."
uvicorn app.main:main_app --host 0.0.0.0 --port 3195 --reload