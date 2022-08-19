===========================
OpenStack Skyline APIServer
===========================

.. image:: https://governance.openstack.org/tc/badges/skyline-apiserver.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on

OpenStack Skyline APIServer is the back-end server of Skyline.

Skyline is an OpenStack dashboard optimized by UI and UE, support OpenStack
Train+. It has a modern technology stack and ecology, is easier for developers
to maintain and operate by users, and has higher concurrency performance.

You can learn more about Skyline APIServer at:

* `Wiki <https://wiki.openstack.org/Skyline/>`__
* `Developer Docs <https://docs.openstack.org/skyline-apiserver/latest/>`__
* `Blueprints <https://blueprints.launchpad.net/skyline-apiserver/>`__
* `Release notes <https://docs.openstack.org/releasenotes/skyline-apiserver/>`__

Getting Started
---------------

If you'd like to run from the master branch, you can clone the git repo:

    git clone https://opendev.org/openstack/skyline-apiserver

You can raise bugs on `Launchpad <https://bugs.launchpad.net/skyline-apiserver>`__

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

.. |image1| image:: docs/images/nine-color-deer-64.png
