# Skyline API

English | [简体中文](./README-zh_CN.md)

Skyline is an OpenStack dashboard optimized by UI and UE. It has a modern technology stack and ecology, is easier for developers to maintain and operate by users, and has higher concurrency performance.

**Table of contents**

- [Resources](#resources)
- [Quick Start](#quick-start)
- [Develop Skyline-apiserver](#develop-skyline-apiserver)

## Resources

- [Wiki](https://wiki.openstack.org/wiki/Skyline)
- [Bug Tracker](https://launchpad.net/skyline-apiserver)

## Quick Start

### Prerequisites

- An OpenStack environment that runs at least core components and can access OpenStack components through Keystone endpoints
- A Linux server with container engine ([docker](https://docs.docker.com/engine/install/) or [podman](https://podman.io/getting-started/installation)) installed

### Configure and deployment

#### 1. Connect to database of the OpenStack environment and create the `skyline` database

```bash
$ mysql -u root -p
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS skyline DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
Query OK, 1 row affected (0.001 sec)
```

#### 2. Grant proper access to the databases

Replace `SKYLINE_DBPASS` with a suitable password.

```bash
MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'localhost' IDENTIFIED BY 'SKYLINE_DBPASS';
Query OK, 0 rows affected (0.001 sec)

MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'%'  IDENTIFIED BY 'SKYLINE_DBPASS';
Query OK, 0 rows affected (0.001 sec)
```

#### 3. Create skyline service credentials

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

#### 4. Edit the `/etc/skyline/skyline.yaml` file in linux server

You can refer to the [sample file](etc/skyline.yaml.sample), and modify the following parameters according to the actual environment

- database_url
- keystone_url
- default_region
- interface_type
- system_project_domain
- system_project
- system_user_domain
- system_user_name
- system_user_password

#### 5. Run the skyline_bootstrap container to bootstrap

```bash
docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host skyline:latest

# Check bootstrap is normal `exit 0`
docker logs skyline_bootstrap
```

#### 5. Run the skyline service after bootstrap is complete

```bash
docker rm -f skyline_bootstrap

docker run -d --name skyline --restart=always -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host skyline:latest
```

#### 6. finish installation

You can now access the dashboard: `https://<ip_address>:8080`

## Develop Skyline-apiserver

**Support Linux & Mac OS (Recommend Linux OS) (Because uvloop & cython)**

### Dependent tools

- python >= 3.8
- yarn >= 1.22.4
- node >= 10.22.0
- make >= 3.82
- poetry >= 1.1.0
  ([Installation Guide](https://python-poetry.org/docs/#installation))

### Install & Run

#### 1. Installing dependency packages

```bash
make install
```

#### 2. Set skyline.yaml config file

```bash
cp etc/skyline.yaml.sample etc/skyline.yaml
export OS_CONFIG_DIR=$(pwd)/etc
```

Maybe you should change the params with your real environment as followed:

```yaml
- database_url
- keystone_url
- default_region
- interface_type
- system_project_domain
- system_project
- system_user_domain
- system_user_name
- system_user_password
```

> If you set such as `sqlite:////tmp/skyline.db` for `database_url` , just do as followed.
> If you set such as `mysql://root:root@localhost:3306/skyline` for `database_url` , you should refer to steps `1` and `2` of the chapter `Configure and deployment` at first.

#### 3. Init skyline database

```bash
pushd libs/skyline-apiserver/
make db_sync
popd
```

#### 4. Run skyline-apiserver

```bash
$ poetry run uvicorn --reload --reload-dir libs/skyline-apiserver/skyline_apiserver --port 28000 --log-level debug skyline_apiserver.main:app

INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
INFO:     Started reloader process [154033] using statreload
INFO:     Started server process [154037]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

You can now access the online API documentation: `http://127.0.0.1:28000/docs`
