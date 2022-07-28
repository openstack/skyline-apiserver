# Copyright 2021 99cloud
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import copy
from typing import Dict, List


class APIResourceWrapper(object):
    """Simple wrapper for api objects.

    Define _attrs on the child class and pass in the
    api object as the only argument to the constructor
    """

    _attrs: List[str] = []
    _apiresource = None  # Make sure _apiresource is there even in __init__.

    def __init__(self, apiresource):
        self._apiresource = apiresource

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if attr not in self._attrs:
                raise
            # __getattr__ won't find properties
            return getattr(self._apiresource, attr)

    def __repr__(self):
        return "<%s: %s>" % (
            self.__class__.__name__,
            dict((attr, getattr(self, attr)) for attr in self._attrs if hasattr(self, attr)),
        )

    def to_dict(self):
        obj = {}
        for key in self._attrs:
            obj[key] = getattr(self, key, None)
        return obj

    @property
    def name_or_id(self):
        return self.name or "(%s)" % self.id[:13]


class APIDictWrapper(object):
    """Simple wrapper for api dictionaries

    Some api calls return dictionaries.  This class provides identical
    behavior as APIResourceWrapper, except that it will also behave as a
    dictionary, in addition to attribute accesses.

    Attribute access is the preferred method of access, to be
    consistent with api resource objects from novaclient.
    """

    _apidict: Dict[str, str] = {}  # Make sure _apidict is there even in __init__.

    def __init__(self, apidict):
        self._apidict = apidict

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if attr not in self._apidict:
                raise
            return self._apidict[attr]

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except (AttributeError, TypeError) as e:
            # caller is expecting a KeyError
            raise KeyError(e)

    def __contains__(self, item):
        try:
            return hasattr(self, item)
        except TypeError:
            return False

    def get(self, item, default=None):
        try:
            return getattr(self, item)
        except (AttributeError, TypeError):
            return default

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self._apidict)

    def to_dict(self):
        return self._apidict


class OSServer(APIResourceWrapper):

    _attrs = [
        "accessIPv4",
        "accessIPv6",
        "addresses",
        "config_drive",
        "created",
        "flavor",
        "hostId",
        "id",
        "image",
        "key_name",
        "links",
        "metadata",
        "name",
        "OS-DCF:diskConfig",
        "OS-EXT-AZ:availability_zone",
        "OS-EXT-SRV-ATTR:host",
        "OS-EXT-SRV-ATTR:hypervisor_hostname",
        "OS-EXT-SRV-ATTR:instance_name",
        "OS-EXT-STS:power_state",
        "OS-EXT-STS:task_state",
        "OS-EXT-STS:vm_state",
        "os-extended-volumes:volumes_attached",
        "OS-SRV-USG:launched_at",
        "OS-SRV-USG:terminated_at",
        "status",
        "tenant_id",
        "updated",
        "user_id",
        "fault",
        "progress",
        "security_groups",
        "servers_links",
        "OS-EXT-SRV-ATTR:hostname",
        "OS-EXT-SRV-ATTR:reservation_id",
        "OS-EXT-SRV-ATTR:launch_index",
        "OS-EXT-SRV-ATTR:kernel_id",
        "OS-EXT-SRV-ATTR:ramdisk_id",
        "OS-EXT-SRV-ATTR:root_device_name",
        "OS-EXT-SRV-ATTR:user_data",
        "locked",
        "host_status",
        "description",
        "tags",
        "trusted_image_certificates",
        "locked_reason",
    ]


class OSVolume(APIResourceWrapper):
    _attrs = [
        "migration_status",
        "attachments",
        "links",
        "availability_zone",
        "os-vol-host-attr:host",
        "encrypted",
        "encryption_key_id",
        "updated_at",
        "replication_status",
        "snapshot_id",
        "id",
        "size",
        "user_id",
        "os-vol-tenant-attr:tenant_id",
        "os-vol-mig-status-attr:migstat",
        "metadata",
        "status",
        "volume_image_metadata",
        "description",
        "multiattach",
        "source_volid",
        "consistencygroup_id",
        "os-vol-mig-status-attr:name_id",
        "name",
        "bootable",
        "created_at",
        "volume_type",
        "volume_type_id",
        "group_id",
        "volumes_links",
    ]


class OSVolumeSnapshot(APIResourceWrapper):
    _attrs = [
        "status",
        "os-extended-snapshot-attributes:progress",
        "description",
        "created_at",
        "name",
        "user_id",
        "volume_id",
        "volume_type_id",
        "os-extended-snapshot-attributes:project_id",
        "size",
        "id",
        "metadata",
        "updated_at",
        "snapshots_links",
    ]


class NeutronAPIDictWrapper(APIDictWrapper):
    def __init__(self, apidict):
        if "admin_state_up" in apidict:
            if apidict["admin_state_up"]:
                apidict["admin_state"] = "UP"
            else:
                apidict["admin_state"] = "DOWN"
        super(NeutronAPIDictWrapper, self).__init__(apidict)


class PortAllowedAddressPair(NeutronAPIDictWrapper):
    """Wrapper for neutron port allowed address pairs."""

    def __init__(self, addr_pair):
        super(PortAllowedAddressPair, self).__init__(addr_pair)


class OSPort(NeutronAPIDictWrapper):
    """Wrapper for neutron ports."""

    def __init__(self, apidict):
        pairs = apidict.get("allowed_address_pairs")
        if pairs:
            apidict = copy.deepcopy(apidict)
            wrapped_pairs = [PortAllowedAddressPair(pair) for pair in pairs]
            apidict["allowed_address_pairs"] = wrapped_pairs
        super(OSPort, self).__init__(apidict)
