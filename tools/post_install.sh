#!/usr/bin/env bash

set -ex

# Some projects have been DEPRECATED.
# panko: https://opendev.org/openstack/panko
INSTALL_DEPRECATED_PROJECTS="panko"

INSTALL_PROJECTS="keystone \
    placement \
    nova \
    cinder \
    glance \
    trove \
    neutron neutron-vpnaas \
    heat \
    ironic \
    ironic-inspector \
    octavia \
    manila \
    magnum \
    zun\
    barbican"
BRANCH=`git rev-parse --abbrev-ref HEAD`

for project in ${INSTALL_PROJECTS}
do
    pip install -U git+https://opendev.org/openstack/${project}@${BRANCH}
done

for deprecated_project in ${INSTALL_DEPRECATED_PROJECTS}
do
    pip install -U ${deprecated_project}
done
