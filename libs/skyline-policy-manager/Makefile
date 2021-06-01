PYTHON ?= python3
SOURCES := src
TESTS := tests
TOOLS := tools


.PHONY: venv
venv:
	poetry env use $(PYTHON)


.PHONY: install
install: venv
	poetry run pip install -U pip
	poetry run pip install -U setuptools
	poetry install -vvv
	tools/post_install.sh


.PHONY: build
build:
	poetry build


.PHONY: lint
lint:
	poetry run mypy --no-incremental $(SOURCES)
	poetry run isort --check-only --diff $(SOURCES) $(TESTS) $(TOOLS)
	poetry run black --check --diff --color $(SOURCES) $(TESTS) $(TOOLS)
	poetry run flake8 $(SOURCES) $(TESTS) $(TOOLS)


.PHONY: fmt
fmt:
	poetry run isort $(SOURCES) $(TESTS) $(TOOLS)
	poetry run black $(SOURCES) $(TESTS) $(TOOLS)
	poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed `find $(SOURCES) $(TESTS) $(TOOLS) -name '*.py'`
