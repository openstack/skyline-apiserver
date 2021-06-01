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

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic.types import UUID4

SERVERS_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detailed-detail#list-servers-detailed"  # noqa
VOLUMES_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/block-storage/v3/index.html?expanded=list-accessible-volumes-with-details-detail#list-accessible-volumes-with-details"  # noqa
VOLUME_SNAPSHOTS_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/block-storage/v3/index.html?expanded=list-snapshots-and-details-detail#list-snapshots-and-details"  # noqa
PORTS_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/network/v2/index.html?expanded=list-ports-detail#list-ports"  # noqa


class ExtServerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BUILD = "BUILD"
    # DELETED = "DELETED"
    ERROR = "ERROR"
    HARD_REBOOT = "HARD_REBOOT"
    MIGRATING = "MIGRATING"
    # PASSWORD = "PASSWORD"
    PAUSED = "PAUSED"
    REBOOT = "REBOOT"
    REBUILD = "REBUILD"
    RESCUE = "RESCUE"
    RESIZE = "RESIZE"
    # REVERT_RESIZE = "REVERT_RESIZE"
    SHELVED = "SHELVED"
    SHELVED_OFFLOADED = "SHELVED_OFFLOADED"
    SHUTOFF = "SHUTOFF"
    SOFT_DELETED = "SOFT_DELETED"
    SUSPENDED = "SUSPENDED"
    UNKNOWN = "UNKNOWN"
    # VERIFY_RESIZE = "VERIFY_RESIZE"

    def __str__(self):
        return self.value


class ExtVolumeStatus(str, Enum):
    creating = "creating"
    available = "available"
    reserved = "reserved"
    attaching = "attaching"
    detaching = "detaching"
    in_use = "in-use"
    maintenance = "maintenance"
    deleting = "deleting"
    awaiting_transfer = "awaiting-transfer"
    error = "error"
    error_deleting = "error_deleting"
    backing_up = "backing-up"
    restoring_backup = "restoring-backup"
    error_backing_up = "error_backing-up"
    error_restoring = "error_restoring"
    error_extending = "error_extending"
    downloading = "downloading"
    uploading = "uploading"
    retyping = "retyping"
    extending = "extending"

    def __str__(self):
        return self.value


class ExtVolumeSnapshotStatus(str, Enum):
    CREATING = "CREATING"
    AVAILABLE = "AVAILABLE"
    # BACKING_UP = "BACKING_UP"
    DELETING = "DELETING"
    ERROR = "ERROR"
    # DELETED = "DELETED"
    # UNMANAGING = "UNMANAGING"
    # RESTORING = "RESTORING"
    ERROR_DELETING = "ERROR_DELETING"

    def __str__(self):
        return self.value


class ExtPortStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DOWN = "DOWN"
    BUILD = "BUILD"
    ERROR = "ERROR"
    N_A = "N/A"

    def __str__(self):
        return self.value


class ExtPortDeviceOwner(str, Enum):
    null = ""
    compute_nova = "compute:nova"
    network_dhcp = "network:dhcp"
    network_floatingip = "network:floatingip"
    network_router_gateway = "network:router_gateway"
    network_router_ha_interface = "network:router_ha_interface"
    network_ha_router_replicated_interface = "network:ha_router_replicated_interface"

    def __str__(self):
        return self.value


class ExtSortDir(str, Enum):
    desc = "desc"
    asc = "asc"

    def __str__(self):
        return self.value


class ExtServerSortKey(str, Enum):
    uuid = "uuid"
    display_name = "display_name"
    vm_state = "vm_state"
    locked = "locked"
    created_at = "created_at"
    host = "host"
    project_id = "project_id"

    def __str__(self):
        return self.value


class ExtRecycleServerSortKey(str, Enum):
    uuid = "uuid"
    display_name = "display_name"
    updated_at = "updated_at"
    project_id = "project_id"

    def __str__(self):
        return self.value


class ExtVolumeSortKey(str, Enum):
    id = "id"
    name = "name"
    size = "size"
    status = "status"
    bootable = "bootable"
    created_at = "created_at"

    def __str__(self):
        return self.value


class ExtVolumeSnapshotSortKey(str, Enum):
    id = "id"
    name = "name"
    status = "status"
    created_at = "created_at"

    def __str__(self):
        return self.value


class ExtPortSortKey(str, Enum):
    id = "id"
    name = "name"
    mac_address = "mac_address"
    status = "status"
    project_id = "project_id"

    def __str__(self):
        return self.value


class ExtFlavor(BaseModel):
    ephemeral: Optional[int]
    ram: Optional[int]
    original_name: Optional[str]
    vcpus: Optional[int]
    extra_specs: Optional[Dict[str, Any]]
    swap: Optional[int]
    disk: Optional[int]


class ExtListServersBaseResponse(BaseModel):
    id: UUID4
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {SERVERS_LIST_DOCS_LINKS}",
    )
    project_name: Optional[str]
    image: Optional[UUID4]
    image_name: Optional[str]
    image_os_distro: Optional[str]
    fixed_addresses: Optional[List]
    floating_addresses: Optional[List]

    name: Optional[str] = Field(
        description="Will be removed, please use origin_data[name]",
        deprecated=True,
    )
    project_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[tenant_id]",
        deprecated=True,
    )
    host: Optional[str] = Field(
        description="Will be removed, please use origin_data[OS-EXT-SRV-ATTR:host]",
        deprecated=True,
    )
    hostname: Optional[str] = Field(
        description="Will be removed, please use origin_data[OS-EXT-SRV-ATTR:hostname]",
        deprecated=True,
    )
    flavor: Optional[str] = Field(
        description="Will be removed, please use origin_data[flavor][original_name]",
        deprecated=True,
    )
    flavor_info: Optional[ExtFlavor] = Field(
        description="Will be removed, please use origin_data[flavor]",
        deprecated=True,
    )
    status: Optional[str] = Field(
        description="Will be removed, please use origin_data[status]",
        deprecated=True,
    )
    locked: Optional[bool] = Field(
        description="Will be removed, please use origin_data[locked]",
        deprecated=True,
    )
    created_at: Optional[str] = Field(
        description="Will be removed, please use origin_data[created]",
        deprecated=True,
    )
    task_state: Optional[str] = Field(
        description="Will be removed, please use origin_data[OS-EXT-STS:task_state]",
        deprecated=True,
    )
    vm_state: Optional[str] = Field(
        description="Will be removed, please use origin_data[OS-EXT-STS:vm_state]",
        deprecated=True,
    )
    power_state: Optional[int] = Field(
        description="Will be removed, please use origin_data[OS-EXT-STS:power_state]",
        deprecated=True,
    )
    root_device_name: Optional[str] = Field(
        description="Will be removed, please use origin_data[OS-EXT-SRV-ATTR:root_device_name]",
        deprecated=True,
    )
    metadata: Optional[Dict[str, Any]] = Field(
        description="Will be removed, please use origin_data[metadata]",
        deprecated=True,
    )


class ExtListServersResponse(BaseModel):
    servers: List[ExtListServersBaseResponse]


class ExtListRecycleServersBaseResponse(BaseModel):
    id: UUID4
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {SERVERS_LIST_DOCS_LINKS}",
    )
    project_name: Optional[str]
    image: Optional[UUID4]
    image_name: Optional[str]
    image_os_distro: Optional[str]
    fixed_addresses: Optional[List]
    floating_addresses: Optional[List]
    deleted_at: Optional[str]
    reclaim_timestamp: float

    name: Optional[str] = Field(
        description="Will be removed, please use origin_data[name]",
        deprecated=True,
    )
    project_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[tenant_id]",
        deprecated=True,
    )
    host: Optional[str] = Field(
        description="Will be removed, please use origin_data[OS-EXT-SRV-ATTR:host]",
        deprecated=True,
    )
    hostname: Optional[str] = Field(
        description="Will be removed, please use origin_data[OS-EXT-SRV-ATTR:hostname]",
        deprecated=True,
    )
    flavor: Optional[str] = Field(
        description="Will be removed, please use origin_data[flavor][original_name]",
        deprecated=True,
    )
    flavor_info: Optional[ExtFlavor] = Field(
        description="Will be removed, please use origin_data[flavor]",
        deprecated=True,
    )
    status: Optional[str] = Field(
        description="Will be removed, please use origin_data[status]",
        deprecated=True,
    )


class ExtListRecycleServersResponse(BaseModel):
    recycle_servers: List[ExtListRecycleServersBaseResponse]


class VolumeAttachment(BaseModel):
    id: str
    device: Optional[str]
    server_id: Optional[str]
    server_name: Optional[str]


class ExtListVolumesBaseResponse(BaseModel):
    id: UUID4
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {VOLUMES_LIST_DOCS_LINKS}",
    )
    project_name: Optional[str]
    attachments: Optional[List[VolumeAttachment]]

    name: Optional[str] = Field(
        description="Will be removed, please use origin_data[name]",
        deprecated=True,
    )
    project_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[os-vol-tenant-attr:tenant_id]",
        deprecated=True,
    )
    host: Optional[str] = Field(
        description="Will be removed, please use origin_data[os-vol-host-attr:host]",
        deprecated=True,
    )
    snapshot_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[snapshot_id]",
        deprecated=True,
    )
    source_volid: Optional[str] = Field(
        description="Will be removed, please use origin_data[source_volid]",
        deprecated=True,
    )
    size: Optional[int] = Field(
        description="Will be removed, please use origin_data[size]",
        deprecated=True,
    )
    status: Optional[str] = Field(
        description="Will be removed, please use origin_data[status]",
        deprecated=True,
    )
    volume_type: Optional[str] = Field(
        description="Will be removed, please use origin_data[volume_type]",
        deprecated=True,
    )
    encrypted: Optional[bool] = Field(
        description="Will be removed, please use origin_data[encrypted]",
        deprecated=True,
    )
    bootable: Optional[str] = Field(
        description="Will be removed, please use origin_data[bootable]",
        deprecated=True,
    )
    multiattach: Optional[bool] = Field(
        description="Will be removed, please use origin_data[multiattach]",
        deprecated=True,
    )
    availability_zone: Optional[str] = Field(
        description="Will be removed, please use origin_data[availability_zone]",
        deprecated=True,
    )
    created_at: Optional[str] = Field(
        description="Will be removed, please use origin_data[created_at]",
        deprecated=True,
    )


class ExtListVolumesResponse(BaseModel):
    count: int = 0
    volumes: List[ExtListVolumesBaseResponse]


class ExtListVolumeSnapshotsBaseResponse(BaseModel):
    id: str
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {VOLUME_SNAPSHOTS_LIST_DOCS_LINKS}",  # noqa
    )
    project_name: Optional[str]
    host: Optional[str]
    volume_name: Optional[str]
    child_volumes: Optional[List]

    name: Optional[str] = Field(
        description="Will be removed, please use origin_data[name]",
        deprecated=True,
    )
    project_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[os-extended-snapshot-attributes:project_id]",  # noqa
        deprecated=True,
    )
    size: Optional[int] = Field(
        description="Will be removed, please use origin_data[size]",
        deprecated=True,
    )
    status: Optional[str] = Field(
        description="Will be removed, please use origin_data[status]",
        deprecated=True,
    )
    volume_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[volume_id]",
        deprecated=True,
    )
    created_at: Optional[str] = Field(
        description="Will be removed, please use origin_data[created_at]",
        deprecated=True,
    )
    metadata: Optional[Dict[Any, Any]] = Field(
        description="Will be removed, please use origin_data[metadata]",
        deprecated=True,
    )


class ExtListVolumeSnapshotsResponse(BaseModel):
    count: int = 0
    volume_snapshots: List[ExtListVolumeSnapshotsBaseResponse]


class ExtListPortsBaseResponse(BaseModel):
    id: str
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {PORTS_LIST_DOCS_LINKS}",  # noqa
    )
    server_name: Optional[str]
    network_name: Optional[str]
    ipv4: Optional[List]
    ipv6: Optional[List]

    name: Optional[str] = Field(
        description="Will be removed, please use origin_data[name]",
        deprecated=True,
    )
    mac_address: Optional[str] = Field(
        description="Will be removed, please use origin_data[mac_address]",
        deprecated=True,
    )
    project_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[project_id]",
        deprecated=True,
    )
    device_owner: Optional[str] = Field(
        description="Will be removed, please use origin_data[device_owner]",
        deprecated=True,
    )
    device_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[device_id]",
        deprecated=True,
    )
    status: Optional[str] = Field(
        description="Will be removed, please use origin_data[status]",
        deprecated=True,
    )
    created_at: Optional[str] = Field(
        description="Will be removed, please use origin_data[created_at]",
        deprecated=True,
    )
    network_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[network_id]",
        deprecated=True,
    )
    binding_vnic_type: Optional[str] = Field(
        description="Will be removed, please use origin_data[binding:vnic_type]",
        deprecated=True,
    )
    description: Optional[str] = Field(
        description="Will be removed, please use origin_data[description]",
        deprecated=True,
    )
    port_security_enabled: Optional[bool] = Field(
        description="Will be removed, please use origin_data[port_security_enabled]",
        deprecated=True,
    )
    qos_policy_id: Optional[str] = Field(
        description="Will be removed, please use origin_data[qos_policy_id]",
        deprecated=True,
    )
    fixed_ips: Optional[List] = Field(
        description="Will be removed, please use origin_data[fixed_ips]",
        deprecated=True,
    )


class ExtListPortsResponse(BaseModel):
    count: int = 0
    ports: List[ExtListPortsBaseResponse]


class ExtListComputeServicesBaseResponse(BaseModel):
    id: Optional[str]
    binary: str
    disabled_reason: Optional[str]
    host: str
    state: Optional[str]
    status: str
    updated_at: Optional[str]
    forced_down: Optional[bool]
    zone: Optional[str]


class ExtListComputeServicesResponse(BaseModel):
    services: List[ExtListComputeServicesBaseResponse]
