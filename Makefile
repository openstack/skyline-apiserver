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

# URL for skyline-console packages
SKYLINE_CONSOLE_PACKAGE_URL ?= "https://tarballs.opendev.org/openstack/skyline-console/skyline-console-master.tar.gz"


.PHONY: help
help:
	@echo "Skyline API server development makefile"
	@echo
	@echo "Usage: make <TARGET>"
	@echo
	@echo "Target:"
	@echo "  git_config          Initialize git configuration."
	@echo "  clean               Clean up."
	@echo "  build               Build docker image."
	@echo "  db_revision         Generate database alembic version revision with model."
	@echo "  db_sync             Sync database from alembic version revision."
	@echo "  future_check        Find python files without 'type annotations'.(Alpha)"
	@echo "  fmt                 Format code using tox -e pep8-format."
	@echo "  all                 Run all major tox checks, tests, and generators."
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


.PHONY: clean
clean:
	rm -rf .venv dist htmlcov .coverage log test_results.html build .tox skyline_apiserver.egg-info AUTHORS ChangeLog skyline_console


skyline_console:
	mkdir skyline_console

skyline_console/skyline_console.tar.gz: | skyline_console
	wget -O $@ $(SKYLINE_CONSOLE_PACKAGE_URL)

skyline_console/commit_id: skyline_console/skyline_console.tar.gz
	commit_id_file="$$(tar tzf $< | grep -P '/commit_id\.txt$$')" \
	  && tar xzf $< --directory skyline_console "$${commit_id_file}" \
	  && mv "skyline_console/$${commit_id_file}" $@

.PHONY: build devbuild
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
build: skyline_console/skyline_console.tar.gz skyline_console/commit_id
	$(build_cmd) --no-cache --pull --force-rm \
	  --build-arg GIT_CONSOLE_COMMIT=$(shell cat skyline_console/commit_id) \
	  --build-arg GIT_BRANCH=$(GIT_BRANCH) \
	  --build-arg GIT_COMMIT=$(GIT_COMMIT) \
	  --build-arg RELEASE_VERSION=$(RELEASE_VERSION) \
	  $(BUILD_ARGS) -f $(DOCKER_FILE) -t $(IMAGE):$(IMAGE_TAG) $(BUILD_CONTEXT)
devbuild: skyline_console/skyline_console.tar.gz skyline_console/commit_id
	$(build_cmd) \
	  --build-arg GIT_CONSOLE_COMMIT=$(shell cat skyline_console/commit_id) \
	  --build-arg GIT_BRANCH=devbuild \
	  --build-arg GIT_COMMIT=devbuild \
	  --build-arg RELEASE_VERSION=devbuild \
	  $(BUILD_ARGS) -f $(DOCKER_FILE) -t $(IMAGE):$(IMAGE_TAG) $(BUILD_CONTEXT)


.PHONY: db_revision
HEAD_REV ?= $(shell alembic -c skyline_apiserver/db/alembic/alembic.ini heads | awk '{print $$1}')
NEW_REV ?= $(shell python3 -c 'import sys; print(f"{int(sys.argv[1])+1:03}")' $(HEAD_REV))
REV_MEG ?=
db_revision:
	$(shell [ -z "$(REV_MEG)" ] && printf '$(red)Missing required message, use "make db_revision REV_MEG=<some message>"$(no_color)')
	alembic -c skyline_apiserver/db/alembic/alembic.ini revision --autogenerate --rev-id $(NEW_REV) -m '$(REV_MEG)'


.PHONY: db_sync
db_sync:
	alembic -c skyline_apiserver/db/alembic/alembic.ini upgrade head


# Find python files without "type annotations"
future_check:
	@find skyline_apiserver ! -size 0 -type f -name *.py -exec grep -L 'from __future__ import annotations' {} \;

.PHONY: fmt
fmt:
	tox -e pep8-format

.PHONY: all
all:
	tox -e pep8-format
	tox -e pep8
	# tox -e mypy
	tox -e docs
	tox -e genswagger
	tox -e genconfig
	# tox -e gennginx
	# tox -e releasenotes
	# tox -e pdf-docs
	# tox -e functional
	tox -e py3
