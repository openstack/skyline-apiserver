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

from pydantic import HttpUrl, StrictBool, StrictInt, StrictStr

from skyline_apiserver.config.base import Opt
from skyline_apiserver.types import InterfaceType

keystone_url = Opt(
    name="keystone_url",
    description=(
        "Keystone endpoint address. If using domain, "
        "top level domain is required. For example: example.org"
    ),
    schema=HttpUrl,
    default="http://127.0.0.1:5000/v3/",
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

user_default_domain = Opt(
    name="user_default_domain",
    description="Default domain for user authentication when no domain is specified",
    schema=StrictStr,
    default="Default",
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
        "block-storage": "cinder",
        "compute": "nova",
        "container": "zun",
        "container-infra": "magnum",
        "database": "trove",
        "dns": "designate",
        "identity": "keystone",
        "image": "glance",
        "instance-ha": "masakari",
        "key-manager": "barbican",
        "load-balancer": "octavia",
        "network": "neutron",
        "object-store": "swift",
        "orchestration": "heat",
        "placement": "placement",
        "sharev2": "manilav2",
    },
)

extension_mapping = Opt(
    name="extension_mapping",
    description="Mapping of extension from extensions api",
    schema=Dict[StrictStr, StrictStr],
    default={
        "floating-ip-port-forwarding": "neutron_port_forwarding",
        "fwaas_v2": "neutron_firewall",
        "qos": "neutron_qos",
        "vpnaas": "neutron_vpn",
    },
)

reclaim_instance_interval = Opt(
    name="reclaim_instance_interval",
    description="reclaim instance interval",
    schema=StrictInt,
    default=60 * 60 * 24 * 7,
)

enforce_new_defaults = Opt(
    name="enforce_new_defaults",
    description=(
        "This configuration is associated with `enforce_new_defaults`"
        "in oslo policy, which you can refer to the oslo policy parameters."
        "Skyline does not currently support deprecated policy setting, specify"
        "default:True."
    ),
    schema=StrictBool,
    default=True,
)

sso_enabled = Opt(
    name="sso_enabled",
    description="enable sso",
    schema=StrictBool,
    default=False,
)

sso_protocols = Opt(
    name="sso_protocols",
    description="SSO protocol list",
    schema=List[StrictStr],
    default=[
        "openid",
    ],
)

sso_region = Opt(
    name="sso_region",
    description="SSO region",
    schema=StrictStr,
    default="RegionOne",
)

GROUP_NAME = __name__.split(".")[-1]
ALL_OPTS = (
    enforce_new_defaults,
    sso_enabled,
    sso_protocols,
    sso_region,
    keystone_url,
    system_project_domain,
    system_project,
    system_user_domain,
    system_user_name,
    system_user_password,
    default_region,
    user_default_domain,
    interface_type,
    nginx_prefix,
    base_domains,
    system_admin_roles,
    system_reader_roles,
    service_mapping,
    extension_mapping,
    reclaim_instance_interval,
)

__all__ = ("GROUP_NAME", "ALL_OPTS")
