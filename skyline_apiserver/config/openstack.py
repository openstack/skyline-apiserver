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

from typing import Dict, List

from pydantic import HttpUrl, StrictInt, StrictStr

from skyline_apiserver.config.base import Opt
from skyline_apiserver.types import InterfaceType

keystone_url = Opt(
    name="keystone_url",
    description="Keystone endpoint address",
    schema=HttpUrl,
    default="http://localhost:5000/v3/",
)

system_project_domain = Opt(
    name="system_project_domain",
    description="Skyline system project's domain",
    schema=StrictStr,
    default="Default",
)

system_project = Opt(
    name="system_project",
    description="Skyline system project",
    schema=StrictStr,
    default="service",
)

system_user_domain = Opt(
    name="system_user_domain",
    description="Skyline system user's domain",
    schema=StrictStr,
    default="Default",
)

system_user_name = Opt(
    name="system_user_name",
    description="Skyline system username",
    schema=StrictStr,
    default="skyline",
)

system_user_password = Opt(
    name="system_user_password",
    description="Skyline system 's password",
    schema=StrictStr,
    default="",
)

default_region = Opt(
    name="default_region",
    description="Skyline default region",
    schema=StrictStr,
    default="RegionOne",
)

interface_type = Opt(
    name="interface_type",
    description="OpenStack endpoint interface type",
    schema=InterfaceType,
    default="public",
)

nginx_prefix = Opt(
    name="nginx_prefix",
    description="Endpoint prefix",
    schema=StrictStr,
    default="/api/openstack",
)

base_roles = Opt(
    name="base_roles",
    description="base roles list",
    schema=List[StrictStr],
    default=[
        "keystone_system_admin",
        "keystone_system_reader",
        "keystone_project_admin",
        "keystone_project_member",
        "keystone_project_reader",
        "nova_system_admin",
        "nova_system_reader",
        "nova_project_admin",
        "nova_project_member",
        "nova_project_reader",
        "cinder_system_admin",
        "cinder_system_reader",
        "cinder_project_admin",
        "cinder_project_member",
        "cinder_project_reader",
        "glance_system_admin",
        "glance_system_reader",
        "glance_project_admin",
        "glance_project_member",
        "glance_project_reader",
        "neutron_system_admin",
        "neutron_system_reader",
        "neutron_project_admin",
        "neutron_project_member",
        "neutron_project_reader",
        "heat_system_admin",
        "heat_system_reader",
        "heat_project_admin",
        "heat_project_member",
        "heat_project_reader",
        "placement_system_admin",
        "placement_system_reader",
        "panko_system_admin",
        "panko_system_reader",
        "panko_project_admin",
        "panko_project_member",
        "panko_project_reader",
        "ironic_system_admin",
        "ironic_system_reader",
        "octavia_system_admin",
        "octavia_system_reader",
        "octavia_project_admin",
        "octavia_project_member",
        "octavia_project_reader",
    ],
)

base_domains = Opt(
    name="base_domains",
    description="base domains list",
    schema=List[StrictStr],
    default=[
        "heat_user_domain",
    ],
)

system_admin_roles = Opt(
    name="system_admin_roles",
    description="system admin roles have system permission",
    schema=List[StrictStr],
    default=["admin", "system_admin"],
)

system_reader_roles = Opt(
    name="system_reader_roles",
    description="system reader roles have system permission",
    schema=List[StrictStr],
    default=["system_reader"],
)

service_mapping = Opt(
    name="service_mapping",
    description=(
        "openstack service mapping, service mapping in the format <service_type>:<service_name>"
    ),
    schema=Dict[StrictStr, StrictStr],
    default={
        "baremetal": "ironic",
        "compute": "nova",
        "container": "zun",
        "container-infra": "magnum",
        "database": "trove",
        "identity": "keystone",
        "image": "glance",
        "key-manager": "barbican",
        "load-balancer": "octavia",
        "network": "neutron",
        "object-store": "swift",
        "orchestration": "heat",
        "placement": "placement",
        "sharev2": "manilav2",
        "volumev3": "cinder",
    },
)

extension_mapping = Opt(
    name="extension_mapping",
    description="Mapping of extension from extensions api",
    schema=Dict[StrictStr, StrictStr],
    default={
        "vpnaas": "neutron_vpn",
        "fwaas_v2": "neutron_firewall",
    },
)

reclaim_instance_interval = Opt(
    name="reclaim_instance_interval",
    description="reclaim instance interval",
    schema=StrictInt,
    default=60 * 60 * 24 * 7,
)


GROUP_NAME = __name__.split(".")[-1]
ALL_OPTS = (
    keystone_url,
    system_project_domain,
    system_project,
    system_user_domain,
    system_user_name,
    system_user_password,
    default_region,
    interface_type,
    nginx_prefix,
    base_roles,
    base_domains,
    system_admin_roles,
    system_reader_roles,
    service_mapping,
    extension_mapping,
    reclaim_instance_interval,
)

__all__ = ("GROUP_NAME", "ALL_OPTS")
