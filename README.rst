==================
Skyline API Server
==================

English \| `简体中文 <./README/README-zh_CN.rst>`__ \| `한국어 <./README/README-ko_KR.rst>`__

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
   -  `OpenStack-Ansible Deployment <#openstack-ansible-deployment>`__

Resources
---------

-  `Developer Docs <https://docs.openstack.org/skyline-apiserver/latest/>`__
-  `Release notes <https://docs.openstack.org/releasenotes/skyline-apiserver/>`__
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

2. If you need to dock prometheus, you need to modify the following parameters

   -  prometheus_basic_auth_password
   -  prometheus_basic_auth_user
   -  prometheus_enable_basic_auth
   -  prometheus_endpoint

Deployment with Sqlite
~~~~~~~~~~~~~~~~~~~~~~

1. Run the skyline_bootstrap container to bootstrap

   .. code:: bash

      rm -rf /tmp/skyline && mkdir /tmp/skyline && mkdir /var/log/skyline

      docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /var/log/skyline:/var/log/skyline -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

      # Check bootstrap is normal `exit 0`
      docker logs skyline_bootstrap

2. Run the skyline service after bootstrap is complete

   .. code:: bash

      docker rm -f skyline_bootstrap

   If you need to modify skyline port, add ``-e LISTEN_ADDRESS=<ip:port>`` in the following command

   ``LISTEN_ADDRESS`` defaults to ``0.0.0.0:9999``

   If you need to modify the policy rules of a service, add ``-v /etc/skyline/policy:/etc/skyline/policy`` in the following command

   Rename the service policy yaml file to ``<service_name>_policy.yaml``, and place it in ``/etc/skyline/policy`` folder

   .. code:: bash

      docker run -d --name skyline --restart=always -v /var/log/skyline:/var/log/skyline -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

Deployment with MariaDB
~~~~~~~~~~~~~~~~~~~~~~~

https://docs.openstack.org/skyline-apiserver/latest/install/docker-install-ubuntu.html

API Doc
~~~~~~~~~

You can visit the API doc ``https://<ip_address>:9999/api/openstack/skyline/docs``

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
-  python >= 3.9
-  node >= 10.22.0 (Optional if you only develop with apiserver)
-  yarn >= 1.22.4 (Optional if you only develop with apiserver)

Install & Run
~~~~~~~~~~~~~

1. Installing dependency packages

   .. code:: bash

      tox -e venv
      . .tox/venv/bin/activate
      pip install -r requirements.txt -r test-requirements.txt -chttps://releases.openstack.org/constraints/upper/master
      pip install -e .

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

      # Ubuntu 22.04 / 24.04 install docker-buildx
      # apt install docker-buildx
      # docker buildx create --name mybuilder --driver docker-container --use --bootstrap

      # Local build (current platform only)
      make build PLATFORMS=linux/amd64

      # Multi-platform build and push
      make build PLATFORMS=linux/amd64,linux/arm64 IMAGE=yourrepo/skyline IMAGE_TAG=latest PUSH=true

DevStack Integration
--------------------

`Fast integration with DevStack to build an
environment. <https://docs.openstack.org/skyline-apiserver/latest/install/integration-with-devstack.html>`_

Kolla Ansible Deployment
------------------------

`Kolla Ansible to build an environment. <./kolla/README.md>`__

|image1|

.. |image0| image:: doc/source/images/logo/OpenStack_Project_Skyline_horizontal.png
.. |image1| image:: doc/source/images/logo/nine-color-deer-64.png

FAQ
---

1. Policy

   Q: Why common user could login, but could list the nova servers?
      `Bug #2049807 <https://bugs.launchpad.net/skyline-apiserver/+bug/2049807>`_

   ::

      Symptom:
      -----------------------------------
      1. Login Horizon with common user A, list servers OK.
      2. Login Skyline with same common user A, could list the nova servers, F12 show no http requests sent from network, however webpage show 401, do not allow to list servers

      Root Cause Analysis:
      -----------------------------------
      1. Horizon don't know whether a user could do an action at a resource or not. It simply pass request to recording service, & service (Nova) do the check by its policy file. So it works.
      2. Skyline check the action by itself, with /policy API. If you do not configure it, the default value follows community, like: https://docs.openstack.org/nova/2023.2/configuration/sample-policy.html

      How to fix:
      -----------------------------------
      1. By default, list servers need "project_reader_api": "role:reader and project_id:%(project_id)s"
      2. You should config your customized role, for example: member, _member_, projectAdmin, etc, create implied reader role. "openstack implied role create --implied-role member projectAdmin", or "openstack implied role create --implied-role reader _member_"

      # openstack implied role list
      +----------------------------------+-----------------+----------------------------------+-------------------+
      | Prior Role ID | Prior Role Name | Implied Role ID | Implied Role Name |
      +----------------------------------+-----------------+----------------------------------+-------------------+
      | fe21c5a0d17149c2a7b02bf39154d110 | admin | 4376fc38ba6a44e794671af0a9c60ef5 | member |
      | 4376fc38ba6a44e794671af0a9c60ef5 | member | e081e01b7a4345bc85f8d3210b95362d | reader |
      | bee8fa36149e434ebb69b61d12113031 | projectAdmin | 4376fc38ba6a44e794671af0a9c60ef5 | member |
      | 77cec9fc7e764bd4bf60581869c048de | _member_ | e081e01b7a4345bc85f8d3210b95362d | reader |
      +----------------------------------+-----------------+----------------------------------+-------------------+

OpenStack-Ansible Deployment
----------------------------

OpenStack-Ansible does support Skyline deployments starting with 2024.1 (Caracal) release.
In order to install Skyline you need to specify following in ``/etc/openstack_deploy/openstack_user_config.yml``:

.. code:: yaml

   skyline_dashboard_hosts:
     infra1:
       ip: 172.20.236.111
     infra2:
       ip: 172.20.236.112
     infra3:
       ip: 172.20.236.113

This defines on which hosts `skyline-apiserver` and `skyline-console` will be installed. A corresponding LXC containers
will be spawned on these hosts, in case you are using LXC for your deployment.

Once inventory is defined, you can run ``openstack-ansible openstack.osa.skyline`` to proceed with installation.

OpenStack-Ansible does support building ``skyline-console`` with yarn. This scenario makes sense, when you want to install an
untagged version of skyline-console from a commit SHA. For that you need to override a variable ``skyline_console_git_install_branch``
with a required commit SHA. Role will detect that a custom version is being used and proceed with ``yarn build``. You can also
specify ``skyline_console_yarn_build: true`` explicitly to enable this behavior regardlessly.

For All-In-One (AIO) deployments it is sufficient to add ``skyline`` to the list of scenarios to get Skyline installed as
a dashboard.

You can also have both Skyline and Horizon deployed. In that case, Horizon will be served on ``/horizon`` URI, while Skyline remain
on ``/``.
