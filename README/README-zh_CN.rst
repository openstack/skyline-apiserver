===========================
OpenStack Skyline APIServer
===========================

`English <../README.rst>`__ \| 简体中文 \| `한국어 <./README-ko_KR.rst>`__

Skyline 是一个经过 UI 和 UE 优化过的 OpenStack 仪表盘，支持 OpenStack
Train 及以上版本。Skyline 拥有现代化的技术栈和生态，更易于开发者维护和
使用者操作，以及更高的并发性能。

Skyline 的吉祥物是九色鹿。九色鹿源自于敦煌壁画《九色鹿本生》，其寓意是佛理
因果和知恩图报，这与九州云自创办以来秉持的拥抱和反馈社区理念一致。我们也希望
Skyline 像九色鹿一样，轻巧、优雅，而又能力强大，为 OpenStack 社区和用户
提供更优质的 Dashboard。

|image0|

**目录**

-  `Skyline API Server <#skyline-api-server>`__

   -  `资源 <#资源>`__
   -  `快速开始 <#快速开始>`__

      -  `先决条件 <#先决条件>`__
      -  `配置 <#配置>`__
      -  `部署 - 数据库使用 Sqlite <#部署---数据库使用-sqlite>`__
      -  `部署 - 数据库使用 MariaDB <#部署---数据库使用-mariadb>`__
      -  `访问测试 <#访问测试>`__

   -  `开发 Skyline-apiserver <#开发-skyline-apiserver>`__

      -  `依赖工具 <#依赖工具>`__
      -  `安装和运行 <#安装和运行>`__

   -  `Devstack 集成 <#devstack-集成>`__
   -  `Kolla Ansible 部署 <#kolla-ansible-部署>`__

资源
----

-  `开发者手册 <https://docs.openstack.org/skyline-apiserver/latest/>`__
-  `发布小结 <https://docs.openstack.org/releasenotes/skyline-apiserver/>`__
-  `Wiki <https://wiki.openstack.org/wiki/Skyline>`__
-  `Bug 跟踪器 <https://launchpad.net/skyline-apiserver>`__

快速开始
--------

先决条件
~~~~~~~~

-  一个至少运行核心组件的 OpenStack 环境, 并能通过 Keystone endpoint
   访问 OpenStack 组件
-  一个安装有容器引擎的
   (`docker <https://docs.docker.com/engine/install/>`__ 或
   `podman <https://podman.io/getting-started/installation>`__) 的 Linux
   服务器

配置
~~~~

1. 在 Linux 服务器中编辑 ``/etc/skyline/skyline.yaml`` 文件

   可以参考 `sample file <../etc/skyline.yaml.sample>`__,
   并根据实际的环境修改以下参数

   -  database_url
   -  keystone_url
   -  default_region
   -  interface_type
   -  system_project_domain
   -  system_project
   -  system_user_domain
   -  system_user_name
   -  system_user_password

2. 如果需要对接 prometheus 则需要修改以下配置

   -  prometheus_basic_auth_password
   -  prometheus_basic_auth_user
   -  prometheus_enable_basic_auth
   -  prometheus_endpoint

部署 - 数据库使用 Sqlite
~~~~~~~~~~~~~~~~~~~~~~~~

如果从 dockerhub 拉取镜像失败可以从阿里镜像仓库中拉取，阿里镜像仓库中的镜像会每小时同步一下，镜像地址如下

- registry.cn-shanghai.aliyuncs.com/99cloud-sh/skyline:zed
- registry.cn-shanghai.aliyuncs.com/99cloud-sh/skyline:latest

1. 运行 skyline_bootstrap 容器进行初始化引导

   .. code:: bash

      rm -rf /tmp/skyline && mkdir /tmp/skyline

      docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

      # Check bootstrap is normal `exit 0`
      docker logs skyline_bootstrap

2. 初始化引导完成后运行 skyline 服务

   .. code:: bash

      docker rm -f skyline_bootstrap

   如果需要修改 skyline 端口号，则在以下命令中添加 ``-e LISTEN_ADDRESS=<ip:port>``

   ``LISTEN_ADDRESS`` 默认为 ``0.0.0.0:9999``

   如果需要修改某个 service 的 policy 规则，则在以下命令中添加 ``-v /etc/skyline/policy:/etc/skyline/policy``

   将对应的 policy yaml 文件重命名为 ``<service_name>_policy.yaml``, 并放其在 ``/etc/skyline/policy`` 文件夹下

   .. code:: bash

      docker run -d --name skyline --restart=always -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

部署 - 数据库使用 MariaDB
~~~~~~~~~~~~~~~~~~~~~~~~~

参考：https://docs.openstack.org/skyline-apiserver/latest/install/docker-install-ubuntu.html

1. 连接 OpenStack 环境的数据库, 并创建 ``skyline`` 数据库

   .. code:: bash

      $ mysql -u root -p
      MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS skyline DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
      Query OK, 1 row affected (0.001 sec)

2. 授予对数据库的适当访问权限

   用合适的密码替换 ``SKYLINE_DBPASS``

   .. code:: bash

      MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'localhost' IDENTIFIED BY 'SKYLINE_DBPASS';
      Query OK, 0 rows affected (0.001 sec)

      MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'%'  IDENTIFIED BY 'SKYLINE_DBPASS';
      Query OK, 0 rows affected (0.001 sec)

3. 创建 skyline 服务凭证

   .. code:: bash

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

4. 运行 skyline_bootstrap 容器进行初始化引导

   .. code:: bash

      docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host 99cloud/skyline:latest

      # Check bootstrap is normal `exit 0`
      docker logs skyline_bootstrap

5. 初始化引导完成后运行 skyline 服务

   .. code:: bash

      docker rm -f skyline_bootstrap

   如果需要修改 skyline 端口号，则在以下命令中添加 ``-e LISTEN_ADDRESS=<ip:port>``

   ``LISTEN_ADDRESS`` 默认为 ``0.0.0.0:9999``

   如果需要修改某个 service 的 policy 规则，则在以下命令中添加 ``-v /etc/skyline/policy:/etc/skyline/policy``

   将对应的 policy yaml 文件重命名为 ``<service_name>_policy.yaml``, 并放其在 ``/etc/skyline/policy`` 文件夹下

   .. code:: bash

      docker run -d --name skyline --restart=always -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host 99cloud/skyline:latest

API Doc
~~~~~~~~~

你可以使用 ``https://<ip_address>:9999/api/openstack/skyline/docs`` 来访问 API doc

访问测试
~~~~~~~~

现在你可以访问仪表盘: ``https://<ip_address>:9999``

开发 Skyline-apiserver
----------------------

**支持 Linux 和 Mac 操作系统 (推荐 Linux 操作系统) (由于 uvloop 和 cython 库)**

依赖工具
~~~~~~~~

python 使用了 3.7 版本的新特性 Context Variables 以及 uvloop (0.15.0+
需要 python 3.7+)，考虑大部分系统不支持 python 3.7 ，所以选择支持
python 3.8 及以上版本

-  make >= 3.82
-  python >= 3.8
-  node >= 10.22.0 (可选，只开发 API 就用不到)
-  yarn >= 1.22.4 (可选，只开发 API 就用不到)

安装和运行
~~~~~~~~~~

1. 安装依赖包

   .. code:: bash

      tox -e venv

2. 配置 ``skyline.yaml`` 文件

   .. code:: bash

      cp etc/skyline.yaml.sample etc/skyline.yaml
      export OS_CONFIG_DIR=$(pwd)/etc

   可能你需要根据实际的环境修改以下参数：

   .. code:: yaml

      - database_url
      - keystone_url
      - default_region
      - interface_type
      - system_project_domain
      - system_project
      - system_user_domain
      - system_user_name
      - system_user_password

   如果你为 ``database_url`` 设置了类似 ``sqlite:////tmp/skyline.db``
   ，只需要执行以下操作。 如果你为 ``database_url`` 设置了类似
   ``mysql://root:root@localhost:3306/skyline`` ，你应该先参考
   ``部署 - 数据库使用 MariaDB`` 一章中的 ``1`` 和 ``2`` 步骤。

3. 初始化 skyline 数据库

   .. code:: bash

      source .tox/venv/bin/activate
      make db_sync
      deactivate

4. 运行 skyline-apiserver

   .. code:: console

      $ source .tox/venv/bin/activate
      $ uvicorn --reload --reload-dir skyline_apiserver --port 28000 --log-level debug skyline_apiserver.main:app

      INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
      INFO:     Started reloader process [154033] using statreload
      INFO:     Started server process [154037]
      INFO:     Waiting for application startup.
      INFO:     Application startup complete.

   此时你可访问在线 API 文档：\ ``http://127.0.0.1:28000/docs``\ 。

   如果用 vscode 调试的话，可以通过 ``.vscode/launch.json`` 启动调试器。

5. 构建镜像

   .. code:: bash

      # Ubuntu 22.04 / 24.04 install docker-buildx
      # apt install docker-buildx
      # docker buildx create --name mybuilder --driver docker-container --use --bootstrap

      # 本地构建（仅当前平台）
      make build PLATFORMS=linux/amd64

      # 多平台构建并推送
      make build PLATFORMS=linux/amd64,linux/arm64 IMAGE=yourrepo/skyline IMAGE_TAG=latest PUSH=true

Devstack 集成
-------------

`与 Devstack 快速集成，搭建环境。 <../devstack/README.rst>`__

Kolla Ansible 部署
------------------

`使用 Kolla Ansible 部署环境。 <../kolla/README-zh_CN.md>`__

|image1|

.. |image0| image:: ../doc/source/images/logo/OpenStack_Project_Skyline_horizontal.png
.. |image1| image:: ../doc/source/images/logo/nine-color-deer-64.png
