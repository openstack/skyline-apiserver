#!/usr/bin/env bash

set -ex

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
    barbican \
    designate \
    masakari"
BRANCH=`git rev-parse --abbrev-ref HEAD`

for project in ${INSTALL_PROJECTS}
do
    pip install -U git+https://opendev.org/openstack/${project}@${BRANCH}
done
