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

from typing import Any

from cinderclient.client import Client as CinderClient
from glanceclient.client import Client as GlanceClient
from keystoneauth1.access.access import AccessInfoV3
from keystoneauth1.identity.v3 import Password, Token
from keystoneauth1.session import Session
from keystoneclient.client import Client as KeystoneClient
from keystoneclient.httpclient import HTTPClient
from neutronclient.v2_0.client import Client as NeutronClient
from novaclient.client import Client as NovaClient
from osc_placement.http import SessionClient as PlacementClient
from starlette.concurrency import run_in_threadpool

from skyline_apiserver import schemas
from skyline_apiserver.config import CONF
from skyline_apiserver.types import constants

SESSION = None


async def generate_session(profile: schemas.Profile) -> Any:
    auth_url = await get_endpoint(
        region=profile.region,
        service="keystone",
        session=get_system_session(),
    )
    kwargs = {
        "auth_url": auth_url,
        "token": profile.keystone_token,
        "project_id": profile.project.id,
    }
    auth = Token(**kwargs)
    session = Session(auth=auth, verify=False)
    session.auth.auth_ref = await run_in_threadpool(session.auth.get_auth_ref, session)
    return session


def get_system_session() -> Session:
    global SESSION
    if SESSION is not None:
        return SESSION

    auth = Password(
        auth_url=CONF.openstack.keystone_url,
        user_domain_name=CONF.openstack.system_user_domain,
        username=CONF.openstack.system_user_name,
        password=CONF.openstack.system_user_password,
        project_name=CONF.openstack.system_project,
        project_domain_name=CONF.openstack.system_project_domain,
        reauthenticate=True,
    )
    SESSION = Session(auth=auth, verify=False)
    return SESSION


async def get_access(session: Session) -> AccessInfoV3:
    auth = session.auth
    if auth._needs_reauthenticate():
        auth.auth_ref = await run_in_threadpool(auth.get_auth_ref, session)
    return auth.auth_ref


async def get_endpoint(region: str, service: str, session: Session) -> Any:
    access = await get_access(session=session)
    service_catalog = access.service_catalog
    endpoint = service_catalog.get_urls(
        region_name=region,
        service_name=service,
        interface=CONF.openstack.interface_type,
    )
    if not endpoint:
        raise ValueError("Endpoint not found")
    return endpoint[0]


async def keystone_client(
    session: Session,
    region: str,
    version: str = constants.KEYSTONE_API_VERSION,
) -> HTTPClient:
    endpoint = await get_endpoint(region, "keystone", session=session)
    client = KeystoneClient(version=version, session=session, endpoint=endpoint)
    return client


async def glance_client(
    session: Session,
    region: str,
    version: str = constants.GLANCE_API_VERSION,
) -> HTTPClient:
    endpoint = await get_endpoint(region, "glance", session=session)
    client = GlanceClient(version=version, session=session, endpoint=endpoint)
    return client


async def nova_client(
    session: Session,
    region: str,
    version: str = constants.NOVA_API_VERSION,
) -> HTTPClient:
    endpoint = await get_endpoint(region, "nova", session=session)
    client = NovaClient(version=version, session=session, endpoint_override=endpoint)
    return client


async def cinder_client(
    session: Session,
    region: str,
    version: str = constants.CINDER_API_VERSION,
) -> HTTPClient:
    endpoint = await get_endpoint(region, "cinderv3", session=session)
    client = CinderClient(version=version, session=session, endpoint_override=endpoint)
    return client


async def neutron_client(
    session: Session,
    region: str,
    version: str = constants.NEUTRON_API_VERSION,
) -> HTTPClient:
    endpoint = await get_endpoint(region, "neutron", session=session)
    client = NeutronClient(version=version, session=session, endpoint_override=endpoint)
    return client


async def placement_client(
    session: Session,
    region: str,
    version: str = constants.PLACEMENT_API_VERSION,
) -> HTTPClient:
    endpoint = await get_endpoint(region, "placement", session=session)
    ks_filter = {"service_type": "placement", "endpoint_override": endpoint}
    client = PlacementClient(api_version=version, session=session, ks_filter=ks_filter)
    return client
