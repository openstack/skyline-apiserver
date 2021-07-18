# Skyline API

English | [简体中文](./README-zh_CN.md)

## Quick Start

### Dependent tools

- make >= 3.82
- poetry >= 1.1.0
  ([Installation Guide](https://python-poetry.org/docs/#installation))

### Development mode

**Support Linux & Mac OS (Recommend Linux OS) (Because uvloop & cython)**

- Installing dependency packages

  ```bash
  make install
  ```

- Set skyline.yaml config file

  Maybe you should change the params with your real environment as followed:

  ```yaml
  - database_url  (you can set sqlite:////tmp/skyline.db to use sqlite)
  - default_region
  - keystone_url
  - system_project
  - system_project_domain
  - system_user_domain
  - system_user_name
  - system_user_password
  ```

  ```bash
  cp etc/skyline.yaml.sample etc/skyline.yaml
  export OS_CONFIG_DIR=$(pwd)/etc
  ```

- Init skyline database

  ```bash
  make db_sync
  ```

- Run server

  ```console
  $ poetry run uvicorn --reload --reload-dir libs/skyline-apiserver/skyline_apiserver --port 28000 --log-level debug skyline_apiserver.main:app

  INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
  INFO:     Started reloader process [154033] using statreload
  INFO:     Started server process [154037]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  ```

You can now access the online API documentation: `http://127.0.0.1:28000/docs`
