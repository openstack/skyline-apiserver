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

import time
import uuid

from httpx import AsyncClient

from skyline_apiserver import config, main, schemas
from skyline_apiserver.types import constants


def get_session_profile() -> schemas.Profile:
    profile = schemas.Profile(
        username="testUser",
        keystone_token="testKeystoneToken",
        region="testRegion",
        project={
            "id": uuid.uuid4().hex,
            "name": "testProject",
            "domain": {"id": uuid.uuid4().hex, "name": "testDomain"},
        },
        user={
            "id": uuid.uuid4().hex,
            "name": "testUser",
            "domain": {
                "id": uuid.uuid4().hex,
                "name": "testDomain",
            },
        },
        roles=[{"id": uuid.uuid4().hex, "name": "testRole"}],
        keystone_token_exp="2221-01-13T12:29:37.000000Z",
        base_roles=[],
        exp=int(time.time()) + config.CONF.default.access_token_expire,
        uuid=uuid.uuid4().hex,
        endpoints={
            "placement": "/api/openstack/placement",
            "neutron": "/api/openstack/network",
            "swift": "/api/openstack/object-storage",
            "nova": "/api/openstack/compute",
            "heat": "/api/openstack/heat-api",
            "nova_legacy": "/api/openstack/compute",
            "cinderv2": "/api/openstack/volume",
            "heat-cfn": "/api/openstack/heat-api-cfn",
            "keystone": "/api/openstack/identity",
            "cinder": "/api/openstack/volume",
            "cinderv3": "/api/openstack/volume",
            "glance": "/api/openstack/image",
        },
        projects={
            "0e064ea01b614943993a28b2c15bd6c4": {"name": "demo", "domain_id": "default"},
            "4c017648d2e34d1a8e732b98e3232af9": {"name": "alt_demo", "domain_id": "default"},
            "e88226c062094881b7a1f01517b945b4": {"name": "admin", "domain_id": "default"},
        },
        version=constants.VERSION,
        license={
            "name": "test_license_name",
            "summary": "test_license_summary",
            "macs": [],
            "features": [{"name": "compute", "count": "3"}],
            "start": "2020-12-20",
            "end": "2030-10-02",
        },
        currency={"zh": "元", "en": "CNY"},
    )
    return profile


def get_session_token() -> str:
    profile = get_session_profile()
    return profile.toJWTPayload()


async def get_jwt_from_cookie(client: AsyncClient) -> str:
    login_data = {
        "region": "RegionOne",
        "username": config.CONF.openstack.system_user_name,
        "domain": config.CONF.openstack.system_user_domain,
        "password": config.CONF.openstack.system_user_password,
    }
    r = await client.post(
        url=f"{main.API_PREFIX}/login",
        json=login_data,
    )
    token = r.cookies.get(config.CONF.default.session_name, "")
    return token


async def _logout(client: AsyncClient) -> None:
    await client.post(f"{main.API_PREFIX}/logout")
