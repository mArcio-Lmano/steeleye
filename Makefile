lint:
	poetry run ruff check src/

format:
	poetry run ruff format src/

test:
	poetry run pytest tests/

test-unit:
	poetry run pytest -m "not integration"

test-int:
	poetry run pytest -m "integration"

check-all: format lint test-unit
