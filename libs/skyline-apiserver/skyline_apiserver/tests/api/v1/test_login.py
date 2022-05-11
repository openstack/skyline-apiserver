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

import os
import time

import pytest
from httpx import AsyncClient
from skyline_apiserver import __version__, main
from skyline_apiserver.config import CONF
from skyline_apiserver.db import api as db_api, setup as db_setup
from skyline_apiserver.types import constants
from utils import utils


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_login(client: AsyncClient) -> None:
    login_data = {
        "region": "RegionOne",
        "username": CONF.openstack.system_user_name,
        "domain": CONF.openstack.system_user_domain,
        "password": CONF.openstack.system_user_password,
    }
    r = await client.post(
        url=f"{main.API_PREFIX}/login",
        json=login_data,
    )
    result = r.json()
    assert r.status_code == 200
    assert "keystone_token" in result
    assert "keystone" in result["endpoints"]
    assert "projects" in result
    await utils._logout(client)


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_profile_ok(client: AsyncClient, login_jwt: str) -> None:
    r = await client.get(
        f"{main.API_PREFIX}/profile",
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == 200
    assert "keystone_token" in result
    assert "keystone" in result["endpoints"]
    assert "projects" in result
    assert "base_roles" in result
    assert "base_domains" in result
    assert result["version"] == __version__
    assert len(CONF.openstack.base_domains) == len(result["base_domains"])


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_switch_project(client: AsyncClient, login_jwt: str) -> None:
    r = await client.get(
        f"{main.API_PREFIX}/profile",
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == 200
    assert "project" in result

    project_id = result["project"]["id"]
    r = await client.post(
        f"{main.API_PREFIX}/switch_project/{project_id}",
    )
    result = r.json()
    assert r.status_code == 200
    assert project_id == result["project"]["id"]
    await utils._logout(client)


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_profile_no_auth(client: AsyncClient) -> None:
    r = await client.get(f"{main.API_PREFIX}/profile")
    result = r.json()
    assert r.status_code == 401
    assert result["detail"] == constants.ERR_MSG_TOKEN_NOTFOUND


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_profile_token_expire(client: AsyncClient) -> None:
    profile = utils.get_session_profile()
    profile.exp = int(time.time()) - 1
    token = profile.toJWTPayload()

    r = await client.get(
        f"{main.API_PREFIX}/profile",
        cookies={CONF.default.session_name: token},
    )
    result = r.json()
    assert r.status_code == 401
    assert result["detail"].startswith(constants.ERR_MSG_TOKEN_EXPIRED)


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_profile_token_revoke(client: AsyncClient) -> None:
    profile = utils.get_session_profile()
    await db_setup()
    await db_api.revoke_token(profile.uuid, profile.exp)
    token = profile.toJWTPayload()

    r = await client.get(
        f"{main.API_PREFIX}/profile",
        cookies={CONF.default.session_name: token},
    )
    result = r.json()
    assert r.status_code == 401
    assert result["detail"] == constants.ERR_MSG_TOKEN_REVOKED


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_logout(client: AsyncClient, session_token: str) -> None:
    r = await client.post(
        f"{main.API_PREFIX}/logout",
        cookies={CONF.default.session_name: session_token},
    )
    assert r.status_code == 200
