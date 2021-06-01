# Skyline API

[English](./README.md) | 简体中文

## 快速开始

### 依赖工具

- make >= 3.82
- poetry >= 1.1.0
  ([安装指南](https://python-poetry.org/docs/#installation))

### 开发模式

**仅支持 Linux (由于 uvloop 和 cython 库)**

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

此时可访问在线 API 文档：`http://127.0.0.1:28000/docs`
