# Skyline

[English](./README.md) | 简体中文

Skyline 是一个经过 UI 和 UE 优化过的 OpenStack 仪表盘, 拥有现代化的技术栈和生态，更易于开发者维护和使用者操作, 以及更高的并发性能.

**目录**

- [资源](#资源)
- [快速开始](#快速开始)
- [开发 Skyline-apiserver](#开发-skyline-apiserver)

## 资源

- [Wiki](https://wiki.openstack.org/wiki/Skyline)
- [Bug 跟踪器](https://launchpad.net/skyline-apiserver)

## 快速开始

### 先决条件

- 一个至少运行核心组件的 OpenStack 环境, 并能通过 Keystone endpoint 访问 OpenStack 组件
- 一个安装有容器引擎的 ([docker](https://docs.docker.com/engine/install/) 或 [podman](https://podman.io/getting-started/installation)) 的 Linux 服务器

### 配置和部署

#### 1. 连接 OpenStack 环境的数据库, 并创建 `skyline` 数据库

```bash
$ mysql -u root -p
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS skyline DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
Query OK, 1 row affected (0.001 sec)
```

#### 2. 授予对数据库的适当访问权限

用合适的密码替换 `SKYLINE_DBPASS`

```bash
MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'localhost' IDENTIFIED BY 'SKYLINE_DBPASS';
Query OK, 0 rows affected (0.001 sec)

MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'%'  IDENTIFIED BY 'SKYLINE_DBPASS';
Query OK, 0 rows affected (0.001 sec)
```

#### 3. 创建 skyline 服务凭证

```bash
# Source the admin credentials
$ source admin-openrc

# Create the skyline user
$ openstack user create --domain default --password-prompt skyline
User Password:
Repeat User Password:
+---------------------+----------------------------------+
| Field               | Value                            |
+---------------------+----------------------------------+
| domain_id           | default                          |
| enabled             | True                             |
| id                  | 1qaz2wsx3edc4rfv5tgb6yhn7ujm8ikl |
| name                | skyline                          |
| options             | {}                               |
| password_expires_at | 2020-08-08T08:08:08.123456       |
+---------------------+----------------------------------+

# Add the admin role to the skyline user:
$ openstack role add --project service --user skyline admin
```

#### 4. 在 Linux 服务器中编辑 `/etc/skyline/skyline.yaml` 文件

可以参考 [sample file](etc/skyline.yaml.sample), 并根据实际的环境修改以下参数

- database_url
- keystone_url
- default_region
- interface_type
- system_project_domain
- system_project
- system_user_domain
- system_user_name
- system_user_password

#### 5. 运行 skyline_bootstrap 容器进行初始化引导

```bash
docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host skyline:latest

# Check bootstrap is normal `exit 0`
docker logs skyline_bootstrap
```

#### 5. 初始化引导完成后运行 skyline 服务

```bash
docker rm -f skyline_bootstrap

docker run -d --name skyline --restart=always -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host skyline:latest
```

#### 6. 完成安装

现在你可以访问仪表盘: `https://<ip_address>:8080`

## 开发 Skyline-apiserver

**支持 Linux 和 Mac 操作系统 (推荐 Linux 操作系统) (由于 uvloop 和 cython 库)**

### 依赖工具

- make >= 3.82
- poetry >= 1.1.0
  ([安装指南](https://python-poetry.org/docs/#installation))

### 安装和运行

#### 1. 安装依赖包

```bash
make install
```

#### 2. 配置 `skyline.yaml` 文件

```bash
cp etc/skyline.yaml.sample etc/skyline.yaml
export OS_CONFIG_DIR=$(pwd)/etc
```

可能你需要根据实际的环境修改以下参数：

```yaml
- database_url  (你可以设置为 sqlite:///tmp/skyline.db 来使用 sqlite)
- keystone_url
- default_region
- interface_type
- system_project_domain
- system_project
- system_user_domain
- system_user_name
- system_user_password
```

#### 3. 初始化 skyline 数据库

```bash
pushd /skyline/libs/skyline-apiserver/
make db_sync
popd
```

#### 4. 运行 skyline-apiserver

```bash
$ poetry run uvicorn --reload --reload-dir libs/skyline-apiserver/skyline_apiserver --port 28000 --log-level debug skyline_apiserver.main:app

INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
INFO:     Started reloader process [154033] using statreload
INFO:     Started server process [154037]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

此时你可访问在线 API 文档：`http://127.0.0.1:28000/docs`
