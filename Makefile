PYTHON ?= python3
SOURCES := src
LIBS := libs
TESTS := tests
TOOLS := tools
ROOT_DIR ?= $(shell git rev-parse --show-toplevel)

# Color
no_color = \033[0m
black = \033[0;30m
red = \033[0;31m
green = \033[0;32m
yellow = \033[0;33m
blue = \033[0;34m
purple = \033[0;35m
cyan = \033[0;36m
white = \033[0;37m

# Version
RELEASE_VERSION ?= $(shell git rev-parse --short HEAD)_$(shell date -u +%Y-%m-%dT%H:%M:%S%z)
GIT_BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
GIT_COMMIT ?= $(shell git rev-parse --verify HEAD)


.PHONY: help
help:
	@echo "Skyline API server development makefile"
	@echo
	@echo "Usage: make <TARGET>"
	@echo
	@echo "Target:"
	@echo "  git_config          Initialize git configuration."
	@echo "  venv                Create virtualenvs."
	@echo "  install             Installs the project dependencies."
	@echo "  build               Build source and wheel packages."
	@echo "  lint                Check python code."
	@echo "  fmt                 Format python code style."
	@echo "  test                Run unit tests."
	@echo "  db_revision         Generate database alembic version revision with model."
	@echo "  db_sync             Sync database from alembic version revision."
	@echo "  swagger             Generate swagger json file."
	@echo "  genconfig           Generate sample config file."
	@echo "  future_check        Find python files without 'type annotations'.(Alpha)"
	@echo


.PHONY: git_config
user_name = $(shell git config --get user.name)
user_email = $(shell git config --get user.email)
commit_template = $(shell git config --get commit.template)
git_config:
ifeq ($(user_name),)
	@printf "$(cyan)\n"
	@read -p "Set your git user name: " user_name; \
    git config --local user.name $$user_name; \
    printf "$(green)User name was set.\n$(cyan)"
endif
ifeq ($(user_email),)
	@printf "$(cyan)\n"
	@read -p "Set your git email address: " user_email; \
    git config --local user.email $$user_email; \
    printf "$(green)User email address was set.\n$(no_color)"
endif
ifeq ($(commit_template),)
	@git config --local commit.template $(ROOT_DIR)/tools/git_config/commit_message.txt
endif
	@printf "$(green)Project git config was successfully set.\n$(no_color)"
	@printf "${yellow}You may need to run 'pip install git-review' install git review tools.\n\n${no_color}"


.PHONY: venv
venv: git_config
	poetry env use $(PYTHON)


.PHONY: install
install: venv
	poetry run pip install -U pip
	poetry run pip install -U setuptools
	poetry install -vvv
	$(MAKE) -C $(LIBS)/skyline-policy-manager install
	$(MAKE) -C $(LIBS)/skyline-log install


.PHONY: build
build:
	$(MAKE) -C $(LIBS)/skyline-policy-manager build
	$(MAKE) -C $(LIBS)/skyline-log build
	poetry build


.PHONY: lint
lint:
	$(MAKE) -C $(LIBS)/skyline-policy-manager lint
	$(MAKE) -C $(LIBS)/skyline-log lint
	# poetry run mypy --no-incremental $(SOURCES)
	poetry run isort --check-only --diff $(SOURCES) $(TESTS) $(TOOLS)
	poetry run black --check --diff --color $(SOURCES) $(TESTS) $(TOOLS)
	poetry run flake8 $(SOURCES) $(TESTS) $(TOOLS)


.PHONY: fmt
fmt:
	$(MAKE) -C $(LIBS)/skyline-policy-manager fmt
	$(MAKE) -C $(LIBS)/skyline-log fmt
	poetry run isort $(SOURCES) $(TESTS) $(TOOLS)
	poetry run black $(SOURCES) $(TESTS) $(TOOLS)
	poetry run add-trailing-comma --py36-plus --exit-zero-even-if-changed `find $(SOURCES) $(TESTS) $(TOOLS) -name '*.py'`


.PHONY: test
test:
	echo null


.PHONY: db_revision
HEAD_REV ?= $(shell poetry run alembic heads | awk '{print $$1}')
NEW_REV ?= $(shell python3 -c 'import sys; print(f"{int(sys.argv[1])+1:03}")' $(HEAD_REV))
REV_MEG ?=
db_revision:
	$(shell [ -z "$(REV_MEG)" ] && printf '$(red)Missing required message, use "make db_revision REV_MEG=<some message>"$(no_color)')
	poetry run alembic revision --autogenerate --rev-id $(NEW_REV) -m '$(REV_MEG)'


.PHONY: db_sync
db_sync:
	poetry run alembic upgrade head


.PHONY: swagger
swagger:
	poetry run swagger-generator -o $(ROOT_DIR)/docs/api/swagger.json


.PHONY: genconfig
genconfig:
	poetry run config-sample-generator -o $(ROOT_DIR)/etc/skyline-apiserver.yaml.sample


# Find python files without "type annotations"
future_check:
	@find src ! -size 0 -type f -name *.py -exec grep -L 'from __future__ import annotations' {} \;
