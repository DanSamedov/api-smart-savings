# Makefile for Alembic + Docker FastAPI
.PHONY: build down downv makemigration migrate current downgrade tests


# Build image and run containers
build:
	docker-compose up --build

# Stop containers
down:
	docker-compose down 

# Stop containers and cleanup volumes (DB data)
downv:
	docker-compose down -v 

# Create a new migration
makemigration:
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

# Run migrations
migrate:
	docker compose exec api alembic upgrade head

# View current DB revision
current:
	docker compose exec api alembic current

# Downgrade/Rollback DB by one migration
downgrade:
	docker compose exec api alembic downgrade -1

# Run all tests (Quiet mode)
tests:
	docker compose exec api pytest -q
