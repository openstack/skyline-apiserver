.. _docker-install-ubuntu:

Docker Install Ubuntu
~~~~~~~~~~~~~~~~~~~~~

This section describes how to install and configure the Skyline APIServer
service. Before you begin, you must have a ready OpenStack environment. At
least it includes ``keystone, glance, nova and neutron service``.

.. note::

  You have install the docker service on the host machine. You can follow
  the `docker installation <https://docs.docker.com/engine/install/ubuntu/>`_.

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

We will install the Skyline APIServer service from docker image.

#. Pull the Skyline APIServer service image from Docker Hub:

   .. code-block:: console

      $ sudo docker pull 99cloud/skyline:latest

   .. note::

      Skyline docker image does not contain python driver for database. You may need to build a custom image from 99cloud/skyline which contains the python driver for the database you are using. If you are using mysql that may result in a Dockerfile ressembling the following

      .. code-block:: dockerfile

         FROM 99cloud/skyline:latest

         RUN apt install -y python3-mysqldb

#. Ensure that some folders of skyline-apiserver have been created

   .. code-block:: console

      $ sudo mkdir -p /etc/skyline /var/log/skyline /var/lib/skyline /var/log/nginx

   .. note::

      Modify policy rules of services

      .. code-block:: console

         $ sudo mkdir -p /etc/skyline/policy

      Rename the service policy yaml file to ``<service_name>_policy.yaml``,
      and place it in ``/etc/skyline/policy`` folder.

#. Set all value from :ref:`configuration-settings` into the configuration file
   ``/etc/skyline/skyline.yaml``

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

Finalize installation
---------------------

#. Run bootstrap server

   .. code-block:: console

      $ sudo docker run -d --name skyline_bootstrap \
        -e KOLLA_BOOTSTRAP="" \
        -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml \
        -v /var/log:/var/log \
        --net=host 99cloud/skyline:latest

   .. code-block:: text

      If you see the following message, it means that the bootstrap server is successful:

      + echo '/usr/local/bin/gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app'
      + mapfile -t CMD
      ++ xargs -n 1
      ++ tail /run_command
      + [[ -n 0 ]]
      + cd /skyline-apiserver/
      + make db_sync
      alembic -c skyline_apiserver/db/alembic/alembic.ini upgrade head
      2022-08-19 07:49:16.004 | INFO     | alembic.runtime.migration:__init__:204 - Context impl MySQLImpl.
      2022-08-19 07:49:16.005 | INFO     | alembic.runtime.migration:__init__:207 - Will assume non-transactional DDL.
      + exit 0

#. Cleanup bootstrap server

   .. code-block:: console

      $ sudo docker rm -f skyline_bootstrap

#. Run skyline-apiserver

   .. code-block:: console

      $ sudo docker run -d --name skyline --restart=always \
        -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml \
        -v /var/log:/var/log \
        --net=host 99cloud/skyline:latest

   .. note::

      The skyline image is both include skyline-apiserver and skyline-console.
      And the skyline-apiserver is bound as socket file
      ``/var/lib/skyline/skyline.sock``.

      So you can not access the skyline-apiserver openapi swagger. But now you
      can visit the skyline UI ``http://xxxxx:9999``.

   .. note::

      If you need to modify skyline port, add ``-e LISTEN_ADDRESS=<ip:port>`` in run command.
      Default port is 9999.

   .. note::

      If you want to enable ssl, add ``-e SSL_CERTFILE=<ssl-certfile> -e SSL_KEYFILE=<ssl-keyfile>``
      in run command. Default does not enable ssl.

   .. note::

      If you need to modify the policy rules of services,
      add ``-v /etc/skyline/policy:/etc/skyline/policy`` in run command.

API Doc
---------

You can visit the API doc ``http(s)://<ip_address>:9999/api/openstack/skyline/docs``
