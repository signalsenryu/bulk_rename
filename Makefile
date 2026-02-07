.PHONY: install lint test build clean

install:
	uv sync --all-extras

lint:
	uv run ruff check .

test:
	uv run pytest -vv

build:
	uv build

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
