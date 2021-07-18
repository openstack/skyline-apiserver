PYTHON ?= python3


.PHONY: all
all: install fmt lint test package


.PHONY: venv
venv:
	poetry env use $(PYTHON)


.PHONY: install
install: venv
	poetry run pip install -U pip setuptools
	poetry install -vvv


.PHONY: package
package:
	poetry build -f wheel


.PHONY: fmt
fmt:
	poetry run isort $$(git ls-files -- **/*.py)
	poetry run black --config ../../pyproject.toml $$(git ls-files -- **/*.py)
	poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed $$(git ls-files -- **/*.py)


.PHONY: lint
lint:
	poetry run mypy --no-incremental $$(git ls-files -- **/*.py)
	poetry run isort --check-only --diff  $$(git ls-files -- **/*.py)
	poetry run black --check --diff --color --config ../../pyproject.toml $$(git ls-files -- **/*.py)
	poetry run flake8  $$(git ls-files -- **/*.py)


.PHONY: test
test:
	echo TODO
