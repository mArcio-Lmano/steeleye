lint:
	poetry run ruff check src/

format:
	poetry run ruff format src/

test:
	poetry run pytest tests/
