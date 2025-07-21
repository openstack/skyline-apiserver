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

from pydantic import UUID4, BaseModel, Field

SERVERS_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detailed-detail#list-servers-detailed"  # noqa
VOLUMES_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/block-storage/v3/index.html?expanded=list-accessible-volumes-with-details-detail#list-accessible-volumes-with-details"  # noqa
VOLUME_SNAPSHOTS_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/block-storage/v3/index.html?expanded=list-snapshots-and-details-detail#list-snapshots-and-details"  # noqa
PORTS_LIST_DOCS_LINKS = "https://docs.openstack.org/api-ref/network/v2/index.html?expanded=list-ports-detail#list-ports"  # noqa


class ServerStatus(str, Enum):
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


class VolumeStatus(str, Enum):
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


class VolumeSnapshotStatus(str, Enum):
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


class PortStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DOWN = "DOWN"
    BUILD = "BUILD"
    ERROR = "ERROR"
    N_A = "N/A"

    def __str__(self):
        return self.value


class PortDeviceOwner(str, Enum):
    null = ""
    # prefix compute
    compute_nova = "compute:nova"
    compute_kuryr = "compute:kuryr"
    # prefix network
    network_router_ha_interface = "network:router_ha_interface"
    network_ha_router_replicated_interface = "network:ha_router_replicated_interface"
    network_router_interface = "network:router_interface"
    network_router_gateway = "network:router_gateway"
    network_floatingip = "network:floatingip"
    network_local_ip = "network:local_ip"
    network_dhcp = "network:dhcp"
    network_router_interface_distributed = "network:router_interface_distributed"
    network_floatingip_agent_gateway = "network:floatingip_agent_gateway"
    network_router_centralized_snat = "network:router_centralized_snat"
    network_routed = "network:routed"
    network_distributed = "network:distributed"
    # octavia
    octavia = "Octavia"

    def __str__(self):
        return self.value


class SortDir(str, Enum):
    desc = "desc"
    asc = "asc"

    def __str__(self):
        return self.value


class ServerSortKey(str, Enum):
    uuid = "uuid"
    display_name = "display_name"
    vm_state = "vm_state"
    locked = "locked"
    created_at = "created_at"
    host = "host"
    project_id = "project_id"

    def __str__(self):
        return self.value


class RecycleServerSortKey(str, Enum):
    uuid = "uuid"
    display_name = "display_name"
    updated_at = "updated_at"
    project_id = "project_id"

    def __str__(self):
        return self.value


class VolumeSortKey(str, Enum):
    id = "id"
    name = "name"
    size = "size"
    status = "status"
    bootable = "bootable"
    created_at = "created_at"

    def __str__(self):
        return self.value


class VolumeSnapshotSortKey(str, Enum):
    id = "id"
    name = "name"
    status = "status"
    created_at = "created_at"

    def __str__(self):
        return self.value


class PortSortKey(str, Enum):
    id = "id"
    name = "name"
    mac_address = "mac_address"
    status = "status"
    project_id = "project_id"

    def __str__(self):
        return self.value


class FlavorInServer(BaseModel):
    ephemeral: Optional[int] = Field(None, description="Ephemeral disk size in GB")
    ram: Optional[int] = Field(None, description="RAM size in MB")
    original_name: Optional[str] = Field(None, description="Original flavor name")
    vcpus: Optional[int] = Field(None, description="Number of vCPUs")
    extra_specs: Optional[Dict[str, Any]] = Field(None, description="Extra specs")
    swap: Optional[int] = Field(None, description="Swap size in MB")
    disk: Optional[int] = Field(None, description="Disk size in GB")


class ServersResponseBase(BaseModel):
    id: UUID4 = Field(..., description="Server ID")
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {SERVERS_LIST_DOCS_LINKS}",
    )
    project_name: Optional[str] = Field(None, description="Project name")
    image: Optional[UUID4] = Field(None, description="Image ID")
    image_name: Optional[str] = Field(None, description="Image name")
    image_os_distro: Optional[str] = Field(None, description="Image OS distro")
    fixed_addresses: Optional[List] = Field(None, description="Fixed addresses")
    floating_addresses: Optional[List] = Field(None, description="Floating addresses")

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
    flavor_info: Optional[FlavorInServer] = Field(
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


class ServersResponse(BaseModel):
    servers: List[ServersResponseBase] = Field(..., description="Servers list")


class RecycleServersResponseBase(BaseModel):
    id: UUID4 = Field(..., description="Recycle server id")
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {SERVERS_LIST_DOCS_LINKS}",
    )
    project_name: Optional[str] = Field(None, description="Project name")
    image: Optional[UUID4] = Field(None, description="Image id")
    image_name: Optional[str] = Field(None, description="Image name")
    image_os_distro: Optional[str] = Field(None, description="Image os distro")
    fixed_addresses: Optional[List] = Field(None, description="Fixed addresses")
    floating_addresses: Optional[List] = Field(None, description="Floating addresses")
    deleted_at: Optional[str] = Field(None, description="Deleted at")
    updated_at: Optional[str] = Field(None, description="Updated at")
    reclaim_timestamp: float = Field(..., description="Reclaim timestamp")

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
    flavor_info: Optional[FlavorInServer] = Field(
        description="Will be removed, please use origin_data[flavor]",
        deprecated=True,
    )
    status: Optional[str] = Field(
        description="Will be removed, please use origin_data[status]",
        deprecated=True,
    )


class RecycleServersResponse(BaseModel):
    recycle_servers: List[RecycleServersResponseBase] = Field(
        ..., description="Recycle servers list"
    )


class VolumeAttachment(BaseModel):
    id: str = Field(..., description="Volume attachment id")
    device: Optional[str] = Field(None, description="Device name")
    server_id: Optional[str] = Field(None, description="Server id")
    server_name: Optional[str] = Field(None, description="Server name")


class VolumesResponseBase(BaseModel):
    id: UUID4 = Field(..., description="Volume ID")
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {VOLUMES_LIST_DOCS_LINKS}",
    )
    project_name: Optional[str] = Field(None, description="Project name")
    attachments: Optional[List[VolumeAttachment]] = Field(None, description="Volume attachments")

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


class VolumesResponse(BaseModel):
    count: Optional[int] = Field(0, description="Count of volumes")
    volumes: List[VolumesResponseBase] = Field(..., description="Volumes list")


class VolumeSnapshotChildVolume(BaseModel):
    volume_id: Optional[str] = Field(
        None, description="ID of volume", examples=["00000000-0000-0000-0000-000000000000"]
    )
    volume_name: Optional[str] = Field(
        None, description="Name of volume", examples=["child-volume-demo"]
    )


class VolumeSnapshotsResponseBase(BaseModel):
    id: str = Field(..., description="Snapshot ID")
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {VOLUME_SNAPSHOTS_LIST_DOCS_LINKS}",  # noqa
    )
    project_name: Optional[str] = Field(None, description="Project name")
    host: Optional[str] = Field(None, description="Host name")
    volume_name: Optional[str] = Field(
        None, description="Name of volume", examples=["volume-demo"]
    )
    child_volumes: Optional[List[VolumeSnapshotChildVolume]] = Field(
        None, description="Child volumes"
    )

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


class VolumeSnapshotsResponse(BaseModel):
    count: Optional[int] = Field(0, description="Count of volume snapshots")
    volume_snapshots: List[VolumeSnapshotsResponseBase] = Field(
        ..., description="Volume snapshots list"
    )


class PortsResponseBase(BaseModel):
    id: str = Field(..., description="Port ID")
    origin_data: Dict[str, Any] = Field(
        description=f"The origin_data is the same like the response of {PORTS_LIST_DOCS_LINKS}",  # noqa
    )
    server_name: Optional[str] = Field(None, description="Server name")
    network_name: Optional[str] = Field(None, description="Network name")
    ipv4: Optional[List] = Field(None, description="IPv4 addresses")
    ipv6: Optional[List] = Field(None, description="IPv6 addresses")

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


class PortsResponse(BaseModel):
    ports: List[PortsResponseBase] = Field(..., description="Ports list")


class ComputeServicesResponseBase(BaseModel):
    id: Optional[str] = Field(None, description="Service id")
    binary: str = Field(..., description="Service binary")
    disabled_reason: Optional[str] = Field(None, description="Disabled reason")
    host: str = Field(..., description="Host name")
    state: Optional[str] = Field(None, description="Service state")
    status: str = Field(..., description="Service status")
    updated_at: Optional[str] = Field(None, description="Updated at")
    forced_down: Optional[bool] = Field(None, description="Forced down")
    zone: Optional[str] = Field(None, description="Zone")


class ComputeServicesResponse(BaseModel):
    services: List[ComputeServicesResponseBase] = Field(..., description="Services list")
