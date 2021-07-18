#!/usr/bin/env bash

# Install openstack service package
poetry run pip install --no-deps \
    keystone \
    openstack-placement \
    nova \
    cinder \
    glance \
    neutron neutron-vpnaas \
    openstack-heat \
    ironic-lib ironic ironic-inspector \
    octavia-lib octavia \
    panko

# Patch cinder
patch_path="$(poetry run python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/cinder/__init__.py"
sed -i 's/\(.*eventlet.*\)/# \1/g' $patch_path

# Patch neutron
patch_path="$(poetry run python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/neutron/conf/policies/floatingip_pools.py"
sed -i 's/admin/system/g' $patch_path

# Patch ironic
patch_path="$(poetry run python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/ironic/common/policy.py"
sed -i 's/\(.*lockutils.*\)/# \1/g' $patch_path

# Patch ironic_inspector
patch_path="$(poetry run python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/ironic_inspector/policy.py"
sed -i 's/\(.*lockutils.*\)/# \1/g' $patch_path
