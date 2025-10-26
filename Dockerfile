FROM python:3.11-slim

WORKDIR /app

# Install build tools and PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./scripts ./scripts
COPY ./migrations ./migrations
COPY ./alembic.ini .

RUN chmod +x ./scripts/start.sh ./scripts/start-dev.sh

CMD ["./scripts/start.sh"]