==================
Skyline API Server
==================

English \| `简体中文 <./README-zh_CN.rst>`__

Skyline is an OpenStack dashboard optimized by UI and UE, support
OpenStack Train+. It has a modern technology stack and ecology, is
easier for developers to maintain and operate by users, and has higher
concurrency performance.

Skyline's mascot is the nine-color deer. The nine-color deer comes from
Dunhuang mural “the nine-color king deer”, whose moral is Buddhist
cause-effect and gratefulness, which is consistent with 99cloud's
philosophy of embracing and feedback community since its inception. We
also hope Skyline can keep light, elegant and powerful as the nine-color
deer, to provide a better dashboard for the openstack community and
users.

|image0|

**Table of contents**

-  `Skyline API Server <#skyline-api-server>`__

   -  `Resources <#resources>`__
   -  `Quick Start <#quick-start>`__

      -  `Prerequisites <#prerequisites>`__
      -  `Configure <#configure>`__
      -  `Deployment with Sqlite <#deployment-with-sqlite>`__
      -  `Deployment with MariaDB <#deployment-with-mariadb>`__
      -  `Test Access <#test-access>`__

   -  `Develop Skyline-apiserver <#develop-skyline-apiserver>`__

      -  `Dependent tools <#dependent-tools>`__
      -  `Install & Run <#install--run>`__

   -  `Devstack Integration <#devstack-integration>`__
   -  `Kolla Ansible Deployment <#kolla-ansible-deployment>`__

Resources
---------

-  `Wiki <https://wiki.openstack.org/wiki/Skyline>`__
-  `Bug Tracker <https://launchpad.net/skyline-apiserver>`__

Quick Start
-----------

Prerequisites
~~~~~~~~~~~~~

-  An OpenStack environment that runs at least core components and can
   access OpenStack components through Keystone endpoints
-  A Linux server with container engine
   (`docker <https://docs.docker.com/engine/install/>`__ or
   `podman <https://podman.io/getting-started/installation>`__)
   installed

Configure
~~~~~~~~~

1. Edit the ``/etc/skyline/skyline.yaml`` file in linux server

   You can refer to the `sample file <etc/skyline.yaml.sample>`__, and
   modify the following parameters according to the actual environment

   -  database_url
   -  keystone_url
   -  default_region
   -  interface_type
   -  system_project_domain
   -  system_project
   -  system_user_domain
   -  system_user_name
   -  system_user_password

Deployment with Sqlite
~~~~~~~~~~~~~~~~~~~~~~

1. Run the skyline_bootstrap container to bootstrap

   .. code:: bash

      rm -rf /tmp/skyline && mkdir /tmp/skyline

      docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

      # Check bootstrap is normal `exit 0`
      docker logs skyline_bootstrap

2. Run the skyline service after bootstrap is complete

   .. code:: bash

      docker rm -f skyline_bootstrap

   ..

      If you need to modify skyline port, add
      ``-e LISTEN_ADDRESS=<ip:port>`` in the following command

      ``LISTEN_ADDRESS`` defaults to ``0.0.0.0:9999``

   .. code:: bash

      docker run -d --name skyline --restart=always -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

Deployment with MariaDB
~~~~~~~~~~~~~~~~~~~~~~~

1. Connect to database of the OpenStack environment and create the
   ``skyline`` database

   .. code:: bash

      $ mysql -u root -p
      MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS skyline DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
      Query OK, 1 row affected (0.001 sec)

2. Grant proper access to the databases

   Replace ``SKYLINE_DBPASS`` with a suitable password.

   .. code:: bash

      MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'localhost' IDENTIFIED BY 'SKYLINE_DBPASS';
      Query OK, 0 rows affected (0.001 sec)

      MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'%'  IDENTIFIED BY 'SKYLINE_DBPASS';
      Query OK, 0 rows affected (0.001 sec)

3. Create skyline service credentials

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

4. Run the skyline_bootstrap container to bootstrap

   .. code:: bash

      docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host 99cloud/skyline:latest

      # Check bootstrap is normal `exit 0`
      docker logs skyline_bootstrap

5. Run the skyline service after bootstrap is complete

   .. code:: bash

      docker rm -f skyline_bootstrap

   ..

      If you need to modify skyline port, add
      ``-e LISTEN_ADDRESS=<ip:port>`` in the following command

      ``LISTEN_ADDRESS`` defaults to ``0.0.0.0:9999``

   .. code:: bash

      docker run -d --name skyline --restart=always -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml --net=host 99cloud/skyline:latest

Test Access
~~~~~~~~~~~

You can now access the dashboard: ``https://<ip_address>:9999``

Develop Skyline-apiserver
-------------------------

**Support Linux & Mac OS (Recommend Linux OS) (Because uvloop & cython)**

Dependent tools
~~~~~~~~~~~~~~~

   Use the new feature Context Variables of python37 & uvloop(0.15.0+
   requires python37). Considering that most systems do not support
   python37, we choose to support python38 at least.

-  make >= 3.82
-  python >= 3.8
-  node >= 10.22.0 (Optional if you only develop with apiserver)
-  yarn >= 1.22.4 (Optional if you only develop with apiserver)

Install & Run
~~~~~~~~~~~~~

1. Installing dependency packages

   .. code:: bash

      tox -e venv

2. Set skyline.yaml config file

   .. code:: bash

      cp etc/skyline.yaml.sample etc/skyline.yaml
      export OS_CONFIG_DIR=$(pwd)/etc

   Maybe you should change the params with your real environment as
   followed:

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

   ..

      If you set such as ``sqlite:////tmp/skyline.db`` for
      ``database_url`` , just do as followed. If you set such as
      ``mysql://root:root@localhost:3306/skyline`` for ``database_url``
      , you should refer to steps ``1`` and ``2`` of the chapter
      ``Deployment with MariaDB`` at first.

3. Init skyline database

   .. code:: bash

      source .tox/venv/bin/activate
      make db_sync
      deactivate

4. Run skyline-apiserver

   .. code:: console

      $ source .tox/venv/bin/activate
      $ uvicorn --reload --reload-dir skyline_apiserver --port 28000 --log-level debug skyline_apiserver.main:app

      INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
      INFO:     Started reloader process [154033] using statreload
      INFO:     Started server process [154037]
      INFO:     Waiting for application startup.
      INFO:     Application startup complete.

   You can now access the online API documentation:
   ``http://127.0.0.1:28000/docs``.

   Or, you can launch debugger with ``.vscode/lauch.json`` with vscode.

5. Build Image

   .. code:: bash

      make build

Devstack Integration
--------------------

`Fast integration with Devstack to build an
environment. <./devstack/README.rst>`__

Kolla Ansible Deployment
------------------------

`Kolla Ansible to build an environment. <./kolla/README.md>`__

|image1|

.. |image0| image:: docs/images/OpenStack_Project_Skyline_horizontal.png
.. |image1| image:: docs/images/nine-color-deer-64.png
