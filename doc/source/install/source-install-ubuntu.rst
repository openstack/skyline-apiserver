.. _source-install-ubuntu:

Source Install Ubuntu
~~~~~~~~~~~~~~~~~~~~~

This section describes how to install and configure the Skyline APIServer
service. Before you begin, you must have a ready OpenStack environment. At
least it includes ``keystone, glance, nova and neutron service``.

Prerequisites
-------------

Before you install and configure the Skyline APIServer service, you
must create a database.

#. To create the database, complete these steps:

   #. Use the database access client to connect to the database
      server as the ``root`` user:

      .. code-block:: console

        # mysql

   #. Create the ``skyline`` database:

      .. code-block:: console

        MariaDB [(none)]> CREATE DATABASE skyline DEFAULT CHARACTER SET \
          utf8 DEFAULT COLLATE utf8_general_ci;

   #. Grant proper access to the ``skyline`` database:

      .. code-block:: console

        MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'localhost' \
          IDENTIFIED BY 'SKYLINE_DBPASS';
        MariaDB [(none)]> GRANT ALL PRIVILEGES ON skyline.* TO 'skyline'@'%' \
          IDENTIFIED BY 'SKYLINE_DBPASS';

      Replace ``SKYLINE_DBPASS`` with a suitable password.

   #. Exit the database access client.

#. Source the ``admin`` credentials to gain access to admin-only
   CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   #. Create a ``skyline`` user:

      .. code-block:: console

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
        | password_expires_at | None                             |
        +---------------------+----------------------------------+

   #. Add the ``admin`` role to the ``skyline`` user:

      .. code-block:: console

        $ openstack role add --project service --user skyline admin

      .. note::

        This command provides no output.

Install and configure components
--------------------------------

We will install the Skyline APIServer service from source code.

#. Git clone the repository from OpenDev (GitHub)

   .. code-block:: console

      $ sudo apt update
      $ sudo apt install -y git
      $ cd ${HOME}
      $ git clone https://opendev.org/openstack/skyline-apiserver.git

   .. note::

      If you meet the following error, you need to run command ``sudo apt install -y ca-certificates``:

      `fatal: unable to access 'https://opendev.org/openstack/skyline-apiserver.git/': server
      certificate verification failed. CAfile: none CRLfile: none`

#. Install skyline-apiserver from source

   .. code-block:: console

      $ sudo apt install -y python3-pip
      $ sudo pip3 install skyline-apiserver/

#. Ensure that some folders of skyline-apiserver have been created

   .. code-block:: console

      $ sudo mkdir -p /etc/skyline /var/log/skyline

   .. note::

      Modify policy rules of services

      .. code-block:: console

         $ sudo mkdir -p /etc/skyline/policy

      Rename the service policy yaml file to ``<service_name>_policy.yaml``,
      and place it in ``/etc/skyline/policy`` folder.

#. Copy the configuration file to the configuration folder ``/etc/skyline``

   .. code-block:: console

      $ sudo cp ${HOME}/skyline-apiserver/etc/gunicorn.py /etc/skyline/gunicorn.py
      $ sudo sed -i "s/^bind = *.*/bind = ['0.0.0.0:28000']/g" /etc/skyline/gunicorn.py
      $ sudo cp ${HOME}/skyline-apiserver/etc/skyline.yaml.sample /etc/skyline/skyline.yaml

   .. note::

      We need to change the ``bind`` value in ``/etc/skyline/gunicorn.py`` to ``0.0.0.0:28000``.
      Default value is ``unix:/var/lib/skyline/skyline.sock``.

   .. note::

      Change the related configuration in ``/etc/skyline/skyline.yaml``. Detailed introduction
      of the configuration can be found in :ref:`configuration-settings`.

      .. code-block:: yaml

        default:
          database_url: mysql://skyline:SKYLINE_DBPASS@DB_SERVER:3306/skyline
          debug: true
          log_dir: /var/log/skyline
        openstack:
          keystone_url: http://KEYSTONE_SERVER:5000/v3/
          system_user_password: SKYLINE_SERVICE_PASSWORD

      Replace ``SKYLINE_DBPASS``, ``DB_SERVER``, ``KEYSTONE_SERVER`` and
      ``SKYLINE_SERVICE_PASSWORD`` with a correct value.

#. Populate the Skyline APIServer database

   .. code-block:: console

      $ cd ${HOME}/skyline-apiserver/
      $ make db_sync

Finalize installation
---------------------

#. Set start service config ``/etc/systemd/system/skyline-apiserver.service``

   .. code-block:: text

      [Unit]
      Description=Skyline APIServer

      [Service]
      Type=simple
      ExecStart=/usr/local/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app
      LimitNOFILE=32768

      [Install]
      WantedBy=multi-user.target

   .. code-block:: console

      $ sudo systemctl daemon-reload
      $ sudo systemctl enable skyline-apiserver
      $ sudo systemctl start skyline-apiserver
