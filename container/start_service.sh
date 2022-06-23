#!/usr/bin/env bash
set -ex

# kolla_set_configs
echo "/usr/local/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app" >/run_command

mapfile -t CMD < <(tail /run_command | xargs -n 1)

# kolla_extend_start
if [[ "${!KOLLA_BOOTSTRAP[*]}" ]]; then
    cd /skyline-apiserver/
    make db_sync
    exit 0
fi

if [[ -n "${LISTEN_ADDRESS}" ]]; then
    skyline-nginx-generator -o /etc/nginx/nginx.conf --listen-address "${LISTEN_ADDRESS}"
else
    skyline-nginx-generator -o /etc/nginx/nginx.conf
fi

nginx

echo "Running command: ${CMD[*]}"
exec "${CMD[@]}"
