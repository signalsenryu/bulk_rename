.PHONY: install lint format format-check fix test check build clean

install:
	uv sync --extra dev
	uv run pre-commit install

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

fix:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest -vv -s --cov=. --cov-report=term-missing

check: fix lint format-check test
	@echo "🏁 Quality gate passed at $$(date +'%H:%M:%S')"

build:
	uv build

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true