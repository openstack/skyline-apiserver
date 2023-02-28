#!/usr/bin/env bash
set -ex

# kolla_set_configs
echo "/usr/local/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app" >/run_command

mapfile -t CMD < <(tail /run_command | xargs -n 1)

# kolla_extend_start
if [[ "${!KOLLA_BOOTSTRAP[*]}" ]]; then
    cd /opt/skyline_apiserver/
    make db_sync
    exit 0
fi

GENERATOR_ARGS="--output-file /etc/nginx/nginx.conf"
if [[ -n "${LISTEN_ADDRESS}" ]]; then
    GENERATOR_ARGS+=" --listen-address ${LISTEN_ADDRESS}"
fi
if [[ -n "${SSL_CERTFILE}" ]] && [[ -n "${SSL_KEYFILE}" ]]; then
    GENERATOR_ARGS+=" --ssl-certfile ${SSL_CERTFILE} --ssl-keyfile ${SSL_KEYFILE}"
fi
skyline-nginx-generator ${GENERATOR_ARGS}

nginx

echo "Running command: ${CMD[*]}"
exec "${CMD[@]}"
