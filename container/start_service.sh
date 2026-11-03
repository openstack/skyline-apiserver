#!/usr/bin/env bash
set -ex

CMD=(/usr/local/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app)

# kolla_extend_start
if [[ "${!KOLLA_BOOTSTRAP[*]}" ]]; then
    cd /opt/skyline_apiserver/
    make db_sync
    exit 0
fi

# Generate nginx config under /tmp so both root and arbitrary non-root UIDs
# (e.g. OpenShift) can write it. Pid/temp paths are also under /tmp for the
# same reason. Host/systemd installs should call skyline-nginx-generator
# without --pid-file/--temp-path-prefix to keep distro defaults.
#
# Assumptions for non-root: skyline.yaml is mounted read-only under
# /etc/skyline; /var/log/skyline, /var/lib/skyline and /tmp are writable.
# Bind ports <1024 need extra capabilities; prefer LISTEN_ADDRESS with a
# high port behind a Route/Ingress when running without root.
NGINX_CONFIG_FILE=/tmp/skyline-nginx.conf
NGINX_PID_FILE=/tmp/skyline-nginx.pid
NGINX_TEMP_PATH_PREFIX=/tmp/skyline-nginx

# nginx only creates the leaf temp directories, not parents. An empty /tmp
# bind-mount (e.g. -v /tmp/skyline:/tmp) therefore needs these created from
# the same prefix passed to --temp-path-prefix.
mkdir -p \
    "${NGINX_TEMP_PATH_PREFIX}/client-body" \
    "${NGINX_TEMP_PATH_PREFIX}/proxy" \
    "${NGINX_TEMP_PATH_PREFIX}/fastcgi" \
    "${NGINX_TEMP_PATH_PREFIX}/uwsgi" \
    "${NGINX_TEMP_PATH_PREFIX}/scgi"

GENERATOR_ARGS=(
    --output-file "${NGINX_CONFIG_FILE}"
    --pid-file "${NGINX_PID_FILE}"
    --temp-path-prefix "${NGINX_TEMP_PATH_PREFIX}"
)
if [[ -n "${LISTEN_ADDRESS}" ]]; then
    GENERATOR_ARGS+=(--listen-address "${LISTEN_ADDRESS}")
fi
if [[ -n "${SSL_CERTFILE}" ]] && [[ -n "${SSL_KEYFILE}" ]]; then
    GENERATOR_ARGS+=(--ssl-certfile "${SSL_CERTFILE}" --ssl-keyfile "${SSL_KEYFILE}")
fi
skyline-nginx-generator "${GENERATOR_ARGS[@]}"

nginx -c "${NGINX_CONFIG_FILE}"

echo "Running command: ${CMD[*]}"
exec "${CMD[@]}"
