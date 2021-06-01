# Skyline API

English | [简体中文](./README-zh_CN.md)

## Quick Start

### Dependent tools

- make >= 3.82
- poetry >= 1.1.0
  ([Installation Guide](https://python-poetry.org/docs/#installation))

### Development mode

**Only support Linux (Because uvloop & cython)**

```bash
make install
cp etc/skyline_apiserver.yaml.sample etc/skyline_apiserver.yaml
export OS_CONFIG_DIR=$(pwd)/etc
rm -f /tmp/skyline_apiserver.db
make db_sync
```

```console
# $ poetry run gunicorn -c etc/gunicorn.py --reload skyline_apiserver.main:app
$ poetry run uvicorn --reload --port 28000 --log-level debug skyline_apiserver.main:app

INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
INFO:     Started reloader process [154033] using statreload
INFO:     Started server process [154037]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

You can now access the online API documentation: `http://127.0.0.1:28000/docs`
