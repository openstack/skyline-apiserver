PYTHON ?= python3


.PHONY: all
all: install fmt lint test package


.PHONY: venv
venv:
	poetry env use $(PYTHON)


.PHONY: install
install: venv
	poetry run pip install -U pip setuptools'<58.0.0'
	poetry install -vvv
	tools/post_install.sh


.PHONY: package
package:
	poetry build -f wheel
	poetry build -f sdist


.PHONY: fmt
fmt:
	poetry run isort $$(git ls-files -- **/*.py)
	poetry run black --config ../../pyproject.toml $$(git ls-files -- **/*.py)
	poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed $$(git ls-files -- **/*.py)


.PHONY: lint
lint:
	poetry run mypy --config-file=../../mypy.ini $$(git ls-files -- **/*.py)
	poetry run isort --check-only --diff $$(git ls-files -- **/*.py)
	poetry run black --check --diff --color --config ../../pyproject.toml $$(git ls-files -- **/*.py)
	poetry run flake8 $$(git ls-files -- **/*.py)


.PHONY: test
test:
	echo TODO


.PHONY: clean
clean:
	rm -rf .venv dist
