#!/bin/shell
set -euo pipefail

# wait for DB
echo "[START SCRIPT] (i) Waiting for database..."
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${POSTGRES_USER:-postgres}"; do
  echo "[START SCRIPT] (i) Waiting for database connection..."
  sleep 1
done

echo "[START SCRIPT] (i) Applying alembic migrations..."
alembic upgrade head

echo "[START SCRIPT] (i) Starting FastAPI (dev, reload enabled)..."
exec uvicorn app.main:main_app --host 0.0.0.0 --port 3195 --reload