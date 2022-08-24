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

from pathlib import PurePath
from typing import Any, Dict, List

from keystoneauth1.identity.v3 import Token
from keystoneauth1.session import Session
from starlette.concurrency import run_in_threadpool

from skyline_apiserver.client import utils
from skyline_apiserver.client.utils import get_system_session
from skyline_apiserver.config import CONF
from skyline_apiserver.log import LOG
from skyline_apiserver.types import constants


async def get_project_scope_token(
    keystone_token: str,
    region: str,
    project_id: str,
) -> str:
    auth_url = await utils.get_endpoint(
        region=region,
        service="keystone",
        session=get_system_session(),
    )
    kwargs = {"project_id": project_id}
    scope_auth = Token(auth_url=auth_url, token=keystone_token, **kwargs)

    session = Session(auth=scope_auth, verify=False, timeout=constants.DEFAULT_TIMEOUT)
    keystone_token = session.get_token()

    return keystone_token


async def get_endpoints(region: str) -> Dict[str, Any]:
    access = await utils.get_access(session=get_system_session())
    catalogs = access.service_catalog.get_endpoints(
        region_name=region,
        interface=CONF.openstack.interface_type,
    )
    endpoints = {}
    for service_type, endpoint in catalogs.items():
        service = CONF.openstack.service_mapping.get(service_type)
        # Two cases:
        # 1. The service is created, but no endpoints are created for it.
        # 2. The service is not created.
        # Both of them, we will not add the related endpoint into profile.
        if service is None or not endpoint:
            continue

        path = PurePath("/").joinpath(CONF.openstack.nginx_prefix, region.lower(), service)
        endpoints[service] = str(path)
    nc = await utils.neutron_client(session=get_system_session(), region=region)
    neutron_extentions = await run_in_threadpool(nc.list_extensions)
    extentions_set = {i["alias"] for i in neutron_extentions["extensions"]}
    for alias, mapping_name in CONF.openstack.extension_mapping.items():
        if alias in extentions_set:
            endpoints[mapping_name] = endpoints["neutron"]
        else:
            LOG.info(f"The {alias} resource could not be found.")
    return endpoints


async def get_projects(global_request_id: str, region: str, user: str) -> List[Any]:
    kc = await utils.keystone_client(
        session=get_system_session(),
        region=region,
        global_request_id=global_request_id,
    )

    projects = kc.projects.list(user=user)
    return projects


async def get_domains(global_request_id: str, region: str) -> Any:
    kc = await utils.keystone_client(
        session=get_system_session(),
        region=region,
        global_request_id=global_request_id,
    )
    domains = [i.name for i in kc.domains.list(enabled=True)]
    return domains


async def get_regions() -> Any:
    access = await utils.get_access(session=get_system_session())
    catalogs = access.service_catalog.get_endpoints(interface=CONF.openstack.interface_type)
    regions = list(set(j["region_id"] for i in catalogs for j in catalogs[i]))
    return regions
