.PHONY: run lint format install celery-worker celery-beat populate mailhog

run:
	@uv run python main.py

lint:
	@uv run ruff check --fix .

format:
	@uv run ruff format .

install:
	@uv sync

celery-worker:
	@uv run celery -A main:celery worker --loglevel=info

celery-beat:
	@uv run celery -A main:celery beat --loglevel=info

populate:
	@uv run python scripts/seed_db.py

mailhog:
	@docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog:v1.0.1