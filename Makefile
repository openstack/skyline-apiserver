PYTHON ?= python3
LIBS := $(shell \ls libs)
LIB_PATHS := $(addprefix libs/,$(LIBS))
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


.PHONY: all
all: install fmt lint test package


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
	@echo "  package             Build package from source code."
	@echo "  build               Build container image."
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
	if [ ! -e "libs/skyline-console/.git" ]; then git submodule update --init; fi
	poetry env use $(PYTHON)


.PHONY: install $(INSTALL_LIBS)
INSTALL_LIBS := $(addsuffix .install,$(LIB_PATHS))
install: venv $(INSTALL_LIBS)
	poetry run pip install -U pip setuptools
	poetry install -vvv
$(INSTALL_LIBS):
	$(MAKE) -C $(basename $@) install


.PHONY: package $(PACKAGE_LIBS)
PACKAGE_LIBS := $(addsuffix .package,$(LIB_PATHS))
package: $(PACKAGE_LIBS)
	poetry build -f wheel
$(PACKAGE_LIBS):
	$(MAKE) -C $(basename $@) package


.PHONY: fmt $(FMT_LIBS)
FMT_LIBS := $(addsuffix .fmt,$(LIB_PATHS))
fmt: $(FMT_LIBS)
$(FMT_LIBS):
	$(MAKE) -C $(basename $@) fmt


.PHONY: lint $(LINT_LIBS)
LINT_LIBS := $(addsuffix .lint,$(LIB_PATHS))
lint: $(LINT_LIBS)
$(LINT_LIBS):
	$(MAKE) -C $(basename $@) lint


.PHONY: test $(TEST_LIBS)
TEST_LIBS := $(addsuffix .test,$(LIB_PATHS))
test: $(TEST_LIBS)
$(TEST_LIBS):
	$(MAKE) -C $(basename $@) test


.PHONY: clean $(CLEAN_LIBS)
CLEAN_LIBS := $(addsuffix .clean,$(LIB_PATHS))
clean: $(CLEAN_LIBS)
	rm -rf .venv dist
$(CLEAN_LIBS):
	$(MAKE) -C $(basename $@) clean


.PHONY: build
BUILD_ENGINE ?= docker
BUILD_CONTEXT ?= .
DOCKER_FILE ?= container/Dockerfile
IMAGE ?= skyline
IMAGE_TAG ?= latest
ifeq ($(BUILD_ENGINE), docker)
    build_cmd = docker build
else ifeq ($(BUILD_ENGINE), buildah)
    build_cmd = buildah bud
else
    $(error Unsupported build engine $(BUILD_ENGINE))
endif
build:
	if [ ! -e "libs/skyline-console/.git" ]; then git submodule update --init; fi
	$(build_cmd) --no-cache --pull --force-rm --build-arg RELEASE_VERSION=$(RELEASE_VERSION) --build-arg GIT_BRANCH=$(GIT_BRANCH) --build-arg GIT_COMMIT=$(GIT_COMMIT) $(BUILD_ARGS) -f $(DOCKER_FILE) -t $(IMAGE):$(IMAGE_TAG) $(BUILD_CONTEXT) 


.PHONY: swagger
swagger:
	poetry run swagger-generator -o $(ROOT_DIR)/docs/api/swagger.json


.PHONY: genconfig
genconfig:
	poetry run config-sample-generator -o $(ROOT_DIR)/etc/skyline.yaml.sample


# Find python files without "type annotations"
future_check:
	@find src ! -size 0 -type f -name *.py -exec grep -L 'from __future__ import annotations' {} \;
