#!/bin/bash

# ``stack.sh`` calls the entry points in this order:
#
# - install_skyline
# - configure_skyline
# - init_skyline
# - start_skyline
# - stop_skyline
# - cleanup_skyline

# Save trace setting
_XTRACE=$(set +o | grep xtrace)
set +o xtrace

function _mkdir_chown_stack {
    if [[ ! -d "$1" ]]; then
        sudo mkdir -p "$1"
    fi
    sudo chown $STACK_USER "$1"
}

function _skyline_config_set {
    local file=$1
    local old=$2
    local new=$3
    sed -i -e "s#$old#$new#g" $file
}

function _install_skyline_apiserver {
    setup_develop $SKYLINE_APISERVER_DIR
}

function _install_skyline_console {
    # nginx
    install_package nginx

    # build static
    if [[ ! -d "$DEST/skyline-console" ]]; then
        export ERROR_ON_CLONE=False
        git_clone_by_name "skyline-console"
        unset ERROR_ON_CLONE
    fi
    pushd $DEST/skyline-console
    make package
    if [[ "$GLOBAL_VENV" == "True" ]]; then
        # TODO(frickler): make this more inline with the usual devstall installation process
        $DEVSTACK_VENV/bin/pip install --force-reinstall dist/skyline_console-*.whl
    else
        sudo pip3 install --force-reinstall dist/skyline_console-*.whl
    fi
    popd
}

function _install_extra_tools {
    # install xvfb for skyline-console e2e test
    # https://docs.cypress.io/guides/continuous-integration/introduction#Dependencies
    if is_fedora; then
        install_package xorg-x11-server-Xvfb gtk2-devel gtk3-devel libnotify-devel GConf2 nss libXScrnSaver alsa-lib
    else
        install_package libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libnss3 libxss1 libxtst6 xauth xvfb
    fi
}

function _install_dependent_tools {
    # make
    install_package make

    # nvm
    NVM_INSTALL_FILE_NAME=nvm-install.sh
    if [[ ! -f "$HOME/$NVM_INSTALL_FILE_NAME" ]]; then
        wget -O $HOME/$NVM_INSTALL_FILE_NAME --tries=10 --retry-connrefused --waitretry=60 --no-dns-cache --no-cache  https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh
    fi
    bash $HOME/$NVM_INSTALL_FILE_NAME
    . $HOME/.nvm/nvm.sh

    # nodejs
    NODE_VERSION=gallium
    nvm install --lts=$NODE_VERSION
    nvm alias default lts/$NODE_VERSION
    nvm use default

    # yarn
    npm install -g yarn

    _install_extra_tools
}

# Functions
# ---------

# cleanup_skyline() - Remove residual data files, anything left over from previous
# runs that a clean run would need to clean up
function cleanup_skyline {
    sudo rm -rf $SKYLINE_CONF_DIR
    sudo rm -rf $SKYLINE_LOG_DIR
    sudo rm -rf $SKYLINE_RUN_DIR

    # remove all .venv under skyline
    sudo find $SKYLINE_APISERVER_DIR -name '.venv'|xargs rm -rf

    # uninstall nginx
    uninstall_package nginx
}

# configure_skyline() - Set config files, create data dirs, etc
function configure_skyline {
    _mkdir_chown_stack $SKYLINE_LOG_DIR
    _mkdir_chown_stack $SKYLINE_CONF_DIR
    _mkdir_chown_stack $SKYLINE_RUN_DIR

    cp $SKYLINE_APISERVER_DIR/etc/skyline.yaml.sample $SKYLINE_CONF_FILE
    cp $SKYLINE_APISERVER_DIR/etc/gunicorn.py $SKYLINE_CONF_DIR/gunicorn.py

    # skyline-apiserver Configuration
    #-------------------------

    _skyline_config_set $SKYLINE_CONF_FILE "database_url: *.*" "database_url: mysql://root:$DATABASE_PASSWORD@127.0.0.1:3306/skyline"
    _skyline_config_set $SKYLINE_CONF_FILE "keystone_url: *.*" "keystone_url: $KEYSTONE_SERVICE_URI/v3/"
    _skyline_config_set $SKYLINE_CONF_FILE "system_user_password: *.*" "system_user_password: $SERVICE_PASSWORD"
    # here use public interface instead of internal
    # devstack will not create internal interface
    # we can see more details from devstack/lib/keystone
    _skyline_config_set $SKYLINE_CONF_FILE "interface_type: *.*" "interface_type: public"
    _skyline_config_set $SKYLINE_CONF_FILE "log_dir: *.*" "log_dir: $SKYLINE_LOG_DIR"
}

# create_skyline_accounts() - Create required service accounts
function create_skyline_accounts {
    if ! is_service_enabled key; then
        return
    fi

    create_service_user "skyline" "admin"
}

# init_skyline() - Initialize databases, etc.
function init_skyline {
    recreate_database skyline

    pushd $SKYLINE_APISERVER_DIR
    make db_sync
    popd
}

# install_skyline() - Collect source and prepare
function install_skyline {
    _install_dependent_tools

    _install_skyline_apiserver

    _install_skyline_console
}

# start_skyline() - Start running processes and nginx
function start_skyline {
    # skyline-apiserver Start
    #-------------------------

    if [[ "$GLOBAL_VENV" == "True" ]]; then
        run_process "skyline" "$DEVSTACK_VENV/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app"
    else
        run_process "skyline" "/usr/local/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app"
    fi

    # skyline-console Configuration
    #-------------------------

    sudo skyline-nginx-generator -o /etc/nginx/nginx.conf

    # skyline-console Start
    #-------------------------

    sudo systemctl start nginx.service
}

# stop_skyline() - Stop running processes and nginx
function stop_skyline {
    # skyline-apiserver Stop
    #-------------------------

    stop_process skyline

    # skyline-console Stop
    #-------------------------

    sudo systemctl stop nginx.service
}

if is_service_enabled skyline; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Skyline"
        install_skyline
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Skyline"
        create_skyline_accounts
        configure_skyline
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing and Start Skyline"
        init_skyline
        start_skyline
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Shutting down Skyline"
        stop_skyline
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "Cleaning Skyline"
        cleanup_skyline
    fi
fi

# Restore xtrace
$_XTRACE

# Tell emacs to use shell-script-mode
## Local variables:
## mode: shell-script
## End:
