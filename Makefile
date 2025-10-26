# Makefile for Alembic + Docker FastAPI

# Run migrations
migrate:
	docker compose exec api alembic upgrade head

# Create a new migration
makemigration:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

# View current DB revision
current:
	docker compose exec api alembic current

# Downgrade DB by one migration
downgrade:
	docker compose exec api alembic downgrade -1
