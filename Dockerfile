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

# ------For start script-----
# COPY ./start.sh ./start.sh
# RUN chmod +x ./scripts/start.sh
# CMD ["./scripts/start.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3195", "--reload"]
