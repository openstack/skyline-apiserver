#!/usr/bin/env bash
set -ex

# kolla_set_configs
echo "/usr/local/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app" >/run_command

mapfile -t CMD < <(tail /run_command | xargs -n 1)

# kolla_extend_start
nginx-generator -o /etc/nginx/nginx.conf
nginx

echo "Running command: ${CMD[*]}"
exec "${CMD[@]}"
