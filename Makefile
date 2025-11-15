# Makefile for Alembic + Docker FastAPI
.PHONY: build down downv makemigration migrate current downgrade test-v test-q check format all


# Build image and run containers
build:
	docker compose up --build

# Stop containers
down:
	docker compose down

# Stop containers and cleanup volumes (DB data)
downv:
	docker compose down -v

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

# Run all tests (Verbose mode)
test-v:
	docker compose exec api pytest -v

# # Run all tests (Quiet mode)
test-q:
	docker compose exec api bash -c "pytest -q"

check:
	@echo "Skipping local format checks; handled in CI."

# # Automatically fix formatting and sort imports
format:
	docker compose exec api bash -c "black . && isort ."

# Shortcut to run everything: tests + check
all: test-q check format
