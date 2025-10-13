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

from typing import Any, Optional

import openstack
from cinderclient.client import Client as CinderClient
from keystoneauth1.access.access import AccessInfoV3
from keystoneauth1.identity.v3 import Password, Token
from keystoneauth1.session import Session
from keystoneclient.client import Client as KeystoneClient
from keystoneclient.httpclient import HTTPClient
from neutronclient.v2_0.client import Client as NeutronClient
from novaclient.client import Client as NovaClient

from skyline_apiserver import schemas
from skyline_apiserver.config import CONF
from skyline_apiserver.types import constants

SESSION = None


def generate_session(profile: schemas.Profile) -> Any:
    auth_url = get_endpoint(
        region=profile.region,
        service="identity",
        session=get_system_session(),
    )
    kwargs = {
        "auth_url": auth_url,
        "token": profile.keystone_token,
        "project_id": profile.project.id,
    }
    auth = Token(**kwargs)
    session = Session(auth=auth, verify=CONF.default.cafile, timeout=constants.DEFAULT_TIMEOUT)
    session.auth.auth_ref = session.auth.get_auth_ref(session)  # type: ignore # noqa E501
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
    SESSION = Session(auth=auth, verify=CONF.default.cafile, timeout=constants.DEFAULT_TIMEOUT)
    return SESSION


def get_system_scope_access(keystone_token: str, region: str) -> AccessInfoV3:
    auth_url = get_endpoint(region, "identity", get_system_session())
    scope_auth = Token(auth_url, keystone_token, system_scope="all")
    session = Session(
        auth=scope_auth, verify=CONF.default.cafile, timeout=constants.DEFAULT_TIMEOUT
    )
    return session.auth.get_auth_ref(session)  # type: ignore


def get_access(session: Session) -> AccessInfoV3:
    auth = session.auth
    if auth._needs_reauthenticate():  # type: ignore
        auth.auth_ref = auth.get_auth_ref(session)  # type: ignore
    return auth.auth_ref  # type: ignore


def get_endpoint(region: str, service: str, session: Session) -> Any:
    access = get_access(session=session)
    service_catalog = access.service_catalog
    endpoint = service_catalog.get_urls(
        region_name=region,
        service_type=service,
        interface=CONF.openstack.interface_type,
    )
    if not endpoint:
        raise ValueError("Endpoint not found")
    return endpoint[0]


def keystone_client(
    session: Session,
    region: str,
    global_request_id: Optional[str] = None,
    version: str = constants.KEYSTONE_API_VERSION,
) -> HTTPClient:
    endpoint = get_endpoint(region, "identity", session=session)
    client = KeystoneClient(
        version=version,
        session=session,
        endpoint=endpoint,
        global_request_id=global_request_id,
        interface=CONF.openstack.interface_type,
    )
    return client


def image_client(
    session: Session,
    region: str,
    global_request_id: Optional[str] = None,
) -> HTTPClient:
    endpoint = get_endpoint(region, "image", session=session)
    client = openstack.connection.Connection(
        session=session,
        endpoint=endpoint,
        global_request_id=global_request_id,
    )
    return client


def nova_client(
    session: Session,
    region: str,
    global_request_id: Optional[str] = None,
    version: str = constants.NOVA_API_VERSION,
) -> HTTPClient:
    endpoint = get_endpoint(region, "compute", session=session)
    client = NovaClient(
        version=version,
        session=session,
        endpoint_override=endpoint,
        global_request_id=global_request_id,
    )
    return client


def cinder_client(
    session: Session,
    region: str,
    global_request_id: Optional[str] = None,
    version: str = constants.CINDER_API_VERSION,
) -> HTTPClient:
    endpoint = get_endpoint(region, "block-storage", session=session)
    client = CinderClient(
        version=version,
        session=session,
        endpoint_override=endpoint,
        global_request_id=global_request_id,
    )
    return client


def neutron_client(
    session: Session,
    region: str,
    global_request_id: Optional[str] = None,
    version: str = constants.NEUTRON_API_VERSION,
) -> NeutronClient:
    endpoint = get_endpoint(region, "network", session=session)
    client = NeutronClient(
        version=version,
        session=session,
        endpoint_override=endpoint,
        global_request_id=global_request_id,
    )
    return client
