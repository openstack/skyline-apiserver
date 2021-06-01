PYTHON ?= python3
SOURCES := src
TESTS := tests


.PHONY: venv
venv:
	poetry env use $(PYTHON)


.PHONY: install
install: venv
	poetry run pip install -U pip
	poetry run pip install -U setuptools
	poetry install -vvv


.PHONY: build
build:
	poetry build


.PHONY: lint
lint:
	poetry run mypy --no-incremental $(SOURCES)
	poetry run isort --check-only --diff $(SOURCES) $(TESTS)
	poetry run black --check --diff --color $(SOURCES) $(TESTS)
	poetry run flake8 $(SOURCES) $(TESTS)


.PHONY: fmt
fmt:
	poetry run isort $(SOURCES) $(TESTS)
	poetry run black $(SOURCES) $(TESTS)
	poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed `find $(SOURCES) $(TESTS) -name '*.py'`
