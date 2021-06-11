# Skyline API

[English](./README.md) | 简体中文

## 快速开始

### 依赖工具

- make >= 3.82
- poetry >= 1.1.0
  ([安装指南](https://python-poetry.org/docs/#installation))

### 开发模式

**支持 Linux 和 Mac 操作系统 (推荐 Linux 操作系统) (由于 uvloop 和 cython 库)**

- 安装依赖包

  ```bash
  make install
  ```

- 配置 skyline-apiserver.yaml 文件

  可能你需要根据实际的环境修改以下参数：

  ```yaml
  - database_url  (你可以设置为 sqlite:////tmp/skyline.db 来使用 sqlite)
  - default_region
  - keystone_url
  - system_project
  - system_project_domain
  - system_user_domain
  - system_user_name
  - system_user_password
  ```

  ```bash
  cp etc/skyline-apiserver.yaml.sample etc/skyline-apiserver.yaml
  export OS_CONFIG_DIR=$(pwd)/etc
  ```

- 初始化 skyline 数据库

  ```bash
  make db_sync
  ```

- 运行服务

  ```console
  $ poetry run uvicorn --reload --port 28000 --log-level debug skyline_apiserver.main:app

  INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
  INFO:     Started reloader process [154033] using statreload
  INFO:     Started server process [154037]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  ```

此时你可访问在线 API 文档：`http://127.0.0.1:28000/docs`
