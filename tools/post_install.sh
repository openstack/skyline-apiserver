#!/usr/bin/env bash

# Install openstack service package
pip install -U \
    keystone \
    openstack-placement \
    nova \
    cinder \
    glance \
    trove \
    neutron neutron-vpnaas \
    openstack-heat \
    ironic \
    ironic-inspector \
    octavia \
    panko \
    manila \
    magnum \
    zun
