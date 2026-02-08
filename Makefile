.PHONY: install lint format format-check test check build clean \
        bump-patch bump-minor bump-major

install:
	uv sync --extra dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check

test:
	uv run pytest -vv

check: lint format-check test
	@echo "✅ All checks passed!"

build:
	uv build

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
