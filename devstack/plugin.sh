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

source $SKYLINE_DIR/devstack/inc/*

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
    pushd $SKYLINE_DIR
    make install
    popd
}


function _install_skyline_console {
    # nginx
    install_package nginx

    # build static
    pushd $SKYLINE_DIR/libs/skyline-console
    yarn run build
    popd
}



function _install_dependent_tools {
    # make
    install_package make

    # python
    if is_fedora; then
        install_package python38
    else
        install_package python3.8 python-is-python3 # make sure python exists
    fi

    # poetry
    contrib_pip_install poetry!=1.1.8

    # node
    if is_fedora; then
        curl --silent --location https://rpm.nodesource.com/setup_12.x | sudo bash -
    else
        curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
    fi
    RETRY_UPDATE=True update_package_repo
    install_package nodejs
    sudo npm install -g n
    sudo n stable

    # yarn
    if is_fedora; then
        curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | sudo tee /etc/yum.repos.d/yarn.repo
    else
        curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
        echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
    fi
    RETRY_UPDATE=True update_package_repo
    install_package yarn
}


# Functions
# ---------

# cleanup_skyline() - Remove residual data files, anything left over from previous
# runs that a clean run would need to clean up
function cleanup_skyline {
    rm -rf $SKYLINE_CONF_DIR
    rm -rf $SKYLINE_LOG_DIR
    rm -rf $SKYLINE_RUN_DIR

    # remove all .venv under skyline
    find $SKYLINE_DIR -name '.venv'|xargs rm -rf

    # remove static
    rm -rf $SKYLINE_DIR/libs/skyline-console/skyline_console/static

    # uninstall nginx
    uninstall_package nginx
}

# configure_skyline() - Set config files, create data dirs, etc
function configure_skyline {
    _mkdir_chown_stack $SKYLINE_LOG_DIR
    _mkdir_chown_stack $SKYLINE_CONF_DIR
    _mkdir_chown_stack $SKYLINE_RUN_DIR

    cp $SKYLINE_DIR/etc/skyline.yaml.sample $SKYLINE_CONF_FILE
    cp $SKYLINE_DIR/etc/gunicorn.py $SKYLINE_CONF_DIR/gunicorn.py

    # skyline-apiserver Configuration
    #-------------------------

    _skyline_config_set $SKYLINE_CONF_FILE "database_url: *.*" "database_url: mysql://root:$DATABASE_PASSWORD@127.0.0.1:3306/skyline"
    _skyline_config_set $SKYLINE_CONF_FILE "keystone_url: *.*" "keystone_url: $KEYSTONE_SERVICE_URI/v3/"
    _skyline_config_set $SKYLINE_CONF_FILE "system_user_password: *.*" "system_user_password: $SERVICE_PASSWORD"
    # here use public interface instead of internal
    # devstack will not create internal interface
    # we can see more details from devstack/lib/keystone
    _skyline_config_set $SKYLINE_CONF_FILE "interface_type: *.*" "interface_type: public"
    _skyline_config_set $SKYLINE_CONF_FILE "log_dir: *.*" "log_dir: /var/log"

    # skyline-console Configuration
    #-------------------------

    sudo $SKYLINE_DIR/.venv/bin/nginx-generator -o /etc/nginx/nginx.conf
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

    pushd $SKYLINE_DIR/libs/skyline-apiserver
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

    run_process "skyline" "$SKYLINE_DIR/.venv/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app"

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
