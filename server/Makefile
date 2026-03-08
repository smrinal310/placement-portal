.PHONY: run lint format install celery-worker celery-beat

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
