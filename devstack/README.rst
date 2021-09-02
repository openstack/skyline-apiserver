============================
Enabling Skyline in Devstack
============================

.. note::

    Ubuntu 20.04 (Focal Fossa) is the most tested, and will probably go the smoothest.

1. Download DevStack::

    git clone https://github.com/openstack-dev/devstack.git
    cd devstack

2. Add this repo as an external repository in ``local.conf`` file::

    > cat local.conf
    [[local|localrc]]
    enable_plugin skyline https://opendev.org/skyline/skyline-apiserver

    To use stable branches, make sure devstack is on that branch, and specify
    the branch name to enable_plugin, for example::

    enable_plugin skyline https://opendev.org/skyline/skyline-apiserver master

3. run ``stack.sh``
