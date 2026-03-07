.PHONY: run lint format install

run:
	@uv run python main.py

lint:
	@uv run ruff check --fix .

format:
	@uv run ruff format .

install:
	@uv sync
