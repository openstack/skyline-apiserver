Setting Up a Development Environment
====================================

This page describes how to setup a working Python development environment that
can be used in developing skyline-apiserver on Ubuntu. These instructions
assume you're already familiar with git. Refer to GettingTheCode_ for
additional information.

.. _GettingTheCode: https://wiki.openstack.org/wiki/Getting_The_Code

Following these instructions will allow you to run the skyline-apiserver unit
tests. Running skyline-apiserver is currently only supported on Linux(recommend
Ubuntu 20.04).

Virtual environments
--------------------

Skyline-apiserver development uses `virtualenv <https://pypi.org/project/virtualenv>`__
to track and manage Python dependencies while in development and testing. This
allows you to install all of the Python package dependencies in a virtual
environment or "virtualenv" (a special subdirectory of your skyline-apiserver
directory), instead of installing the packages at the system level.

.. note::

   Virtualenv is useful for running the unit tests, but is not
   typically used for full integration testing or production usage.

Linux Systems
-------------

Install the prerequisite packages.

On Ubuntu20.04-64::

  sudo apt-get install libssl-dev python3-pip libmysqlclient-dev libpq-dev libffi-dev

To get a full python3 development environment, the two python3 packages need to
be added to the list above::

  python3-dev python3-pip

Getting the code
----------------
Grab the code::

    git clone https://opendev.org/openstack/skyline-apiserver.git
    cd skyline-apiserver

Running unit tests
------------------

The preferred way to run the unit tests is using ``tox``. It executes tests in
isolated environment, by creating separate virtualenv and installing
dependencies from the ``requirements.txt`` and ``test-requirements.txt`` files,
so the only package you install is ``tox`` itself::

    sudo pip install tox

Run the unit tests by doing::

    tox -e py38

Setup Your Local Development Env
--------------------------------

#. Installing dependency packages

   .. code:: bash

      tox -e venv

#. Set skyline.yaml config file

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

#. Init skyline database

   .. code:: bash

      source .tox/venv/bin/activate
      make db_sync
      deactivate

#. Run skyline-apiserver

   .. code:: console

      $ source .tox/venv/bin/activate
      $ uvicorn --reload --reload-dir skyline_apiserver --port 28000 --log-level debug skyline_apiserver.main:app

      INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
      INFO:     Started reloader process [154033] using statreload
      INFO:     Started server process [154037]
      INFO:     Waiting for application startup.
      INFO:     Application startup complete.

   You can now access the online API documentation: ``http://127.0.0.1:28000/docs``.

   Or, you can launch debugger with ``.vscode/lauch.json`` with vscode.

Contributing Your Work
----------------------

Once your work is complete you may wish to contribute it to the project.
Skyline-apiserver uses the Gerrit code review system. For information on
how to submit your branch to Gerrit, see GerritWorkflow_.

.. _GerritWorkflow: https://docs.openstack.org/infra/manual/developers.html#development-workflow
