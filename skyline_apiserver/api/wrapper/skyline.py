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

from typing import Any, Dict, List


class APIResourceWrapper(object):
    """Simple wrapper for api objects."""

    _attrs: List[str] = []
    _attrs_mapping: Dict[str, Any] = {}
    _apiresource: Any = None

    def __init__(self, apiresource: Any) -> None:
        self._apiresource = apiresource

    def __getattribute__(self, attr: str) -> Any:
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            raise

    def __repr__(self) -> str:
        return "<%s: %s>" % (
            self.__class__.__name__,
            self.to_dict(),
        )

    def _get_value(self, key: str) -> Any:
        if isinstance(self._apiresource, dict):
            value = self._apiresource.get(key, None)
        else:
            value = getattr(self._apiresource, key, None)
        return value

    def to_dict(self) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in self._attrs_mapping.items():
            obj[key] = self._get_value(value)
        return obj


class Server(APIResourceWrapper):

    _attrs_mapping = {
        "id": "id",
        "name": "name",
        "project_id": "tenant_id",
        "project_name": "project_name",
        "host": "OS-EXT-SRV-ATTR:host",
        "hostname": "OS-EXT-SRV-ATTR:hostname",
        "image": "image",
        "image_name": "image_name",
        "image_os_distro": "image_os_distro",
        "fixed_addresses": "fixed_addresses",
        "floating_addresses": "floating_addresses",
        "flavor": "flavor",
        "flavor_info": "flavor",
        "status": "status",
        "locked": "locked",
        "created_at": "created",
        "updated_at": "updated",
        "task_state": "OS-EXT-STS:task_state",
        "vm_state": "OS-EXT-STS:vm_state",
        "power_state": "OS-EXT-STS:power_state",
        "volumes_attached": "os-extended-volumes:volumes_attached",
        "root_device_name": "OS-EXT-SRV-ATTR:root_device_name",
        "metadata": "metadata",
    }

    def _format_flavor(self, obj: Dict[str, Any], key: str, return_key: str) -> None:
        flavor = self._get_value(key)
        obj[return_key] = flavor["original_name"] if flavor else None

    def _format_addr(
        self,
        obj: Dict[str, Any],
        key: str,
        address_type: str,
        return_key: str,
    ) -> None:
        addresses = []
        for _, v in self._get_value(key).items():
            addresses.extend(v)
        _addresses = []
        for address in addresses:
            if address.get("OS-EXT-IPS:type") == address_type:
                _addresses.append(address.get("addr"))
        obj[return_key] = _addresses

    def _format_image(self, obj: Dict[str, Any], key: str, return_key: str) -> None:
        image = self._get_value(key)
        obj[return_key] = image["id"] if image else None

    def to_dict(self) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in self._attrs_mapping.items():
            if key == "flavor":
                self._format_flavor(obj, "flavor", key)
                continue
            if value == "fixed_addresses":
                self._format_addr(obj, "addresses", "fixed", key)
                continue
            if value == "floating_addresses":
                self._format_addr(obj, "addresses", "floating", key)
                continue
            if value == "image":
                self._format_image(obj, "image", key)
                continue
            obj[key] = self._get_value(value)
        return obj


class Volume(APIResourceWrapper):

    _attrs_mapping = {
        "id": "id",
        "name": "name",
        "project_id": "os-vol-tenant-attr:tenant_id",
        "project_name": "project_name",
        "host": "os-vol-host-attr:host",
        "snapshot_id": "snapshot_id",
        "source_volid": "source_volid",
        "size": "size",
        "status": "status",
        "volume_type": "volume_type",
        "attachments": "attachments",
        "encrypted": "encrypted",
        "bootable": "bootable",
        "multiattach": "multiattach",
        "availability_zone": "availability_zone",
        "created_at": "created_at",
        "volume_image_metadata": "volume_image_metadata",
    }


class VolumeSnapshot(APIResourceWrapper):

    _attrs_mapping = {
        "id": "id",
        "name": "name",
        "project_id": "os-extended-snapshot-attributes:project_id",
        "project_name": "project_name",
        "size": "size",
        "status": "status",
        "volume_id": "volume_id",
        "volume_name": "volume_name",
        "created_at": "created_at",
        "metadata": "metadata",
    }


class Flavor(APIResourceWrapper):

    _attrs_mapping = {
        "id": "id",
        "name": "name",
        "vcpus": "vcpus",
        "ram": "ram",
        "disk": "disk",
        "is_public": "os-flavor-access:is_public",
        "is_in_use": "is_in_use",
    }


class Service(APIResourceWrapper):

    _attrs_mapping = {
        "id": "id",
        "binary": "binary",
        "disabled_reason": "disabled_reason",
        "host": "host",
        "state": "state",
        "status": "status",
        "updated_at": "updated_at",
        "forced_down": "forced_down",
        "zone": "zone",
    }


class Image(APIResourceWrapper):
    _attrs_mapping = {
        "id": "id",
        "name": "name",
        "os_distro": "os_distro",
        "block_device_mapping": "block_device_mapping",
        "image_type": "image_type",
        "status": "status",
        "visibility": "visibility",
        "disk_format": "disk_format",
        "size": "size",
        "created_at": "created_at",
    }


class Project(APIResourceWrapper):
    _attrs_mapping = {
        "id": "id",
        "name": "name",
    }


class Port(APIResourceWrapper):
    _attrs_mapping = {
        "id": "id",
        "name": "name",
        "ipv4": "fixed_ips",
        "ipv6": "fixed_ips",
        "mac_address": "mac_address",
        "device_owner": "device_owner",
        "device_id": "device_id",
        "server_name": "server_name",
        "status": "status",
        "created_at": "created_at",
        "project_id": "project_id",
        "network_id": "network_id",
        "binding_vnic_type": "binding:vnic_type",
        "description": "description",
        "port_security_enabled": "port_security_enabled",
        "qos_policy_id": "qos_policy_id",
        "fixed_ips": "fixed_ips",
    }

    def _format_ip(
        self,
        obj: Dict[str, Any],
        key: str,
        return_key: str,
    ) -> None:
        ips = []
        fixed_ips = self._get_value(key)
        if fixed_ips:
            for ip in fixed_ips:
                if return_key == "ipv4" and ":" not in ip["ip_address"]:
                    ips.append(ip["ip_address"])
                elif return_key == "ipv6" and "." not in ip["ip_address"]:
                    ips.append(ip["ip_address"])
        obj[return_key] = ips

    def to_dict(self) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in self._attrs_mapping.items():
            if key == "ipv4":
                self._format_ip(obj, "fixed_ips", key)
                continue
            if key == "ipv6":
                self._format_ip(obj, "fixed_ips", key)
                continue
            obj[key] = self._get_value(value)
        return obj
