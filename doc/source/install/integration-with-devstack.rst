.. _integration-with-devstack:

Integration with DevStack
~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   Ubuntu 20.04 (Focal Fossa) is the most tested and typically offers
   the smoothest experience. Ubuntu 22.04, 24.04, and Rocky Linux 9 are
   also supported, but may require additional testing or adjustments.

#. Download DevStack:

   .. code-block:: console

     # git clone https://opendev.org/openstack/devstack
     # cd devstack

#. Add this repo as an external repository in ``local.conf`` file:

   .. code-block:: console

     # cat local.conf

       [[local|localrc]]
       enable_plugin skyline-apiserver https://opendev.org/openstack/skyline-apiserver

   #. To use stable branches, make sure devstack is on that branch, and specify
      the branch name to enable_plugin, for example:

      .. code-block:: console

         enable_plugin skyline-apiserver https://opendev.org/openstack/skyline-apiserver master

#. Run ``stack.sh``:

   .. code-block:: console

     # ./stack.sh

#. Visit the skyline UI with 9999 port
