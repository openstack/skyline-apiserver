PYTHON ?= python3
PY_FILES := $(shell git ls-files -- *.py | xargs)


.PHONY: all
all: install fmt lint test package


.PHONY: venv
venv:
	poetry env use $(PYTHON)


.PHONY: install
install: venv
	poetry run pip install -U pip setuptools'<58.0.0'
	poetry install -vvv


.PHONY: package
package:
	poetry build -f wheel
	poetry build -f sdist


.PHONY: fmt
fmt:
	poetry run isort $(PY_FILES)
	poetry run black --config ../../pyproject.toml $(PY_FILES)
	poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed $(PY_FILES)


.PHONY: lint
lint:
	poetry run mypy --strict --config-file=../../mypy.ini $(PY_FILES)
	poetry run isort --check-only --diff $(PY_FILES)
	poetry run black --check --diff --color --config ../../pyproject.toml $(PY_FILES)
	poetry run flake8 --config ../../.flake8 $(PY_FILES)


.PHONY: test
test:
	poetry run pytest


.PHONY: clean
clean:
	rm -rf .venv dist htmlcov .coverage
