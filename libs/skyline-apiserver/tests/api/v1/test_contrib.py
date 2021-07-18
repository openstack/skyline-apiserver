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

import pytest
from httpx import AsyncClient

from skyline_apiserver import main
from skyline_apiserver.config import CONF


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_regions(client: AsyncClient) -> None:
    r = await client.get(url=f"{main.API_PREFIX}/contrib/regions")
    result = r.json()
    assert r.status_code == 200
    assert len(result) > 0


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_domains(client: AsyncClient) -> None:
    r = await client.get(url=f"{main.API_PREFIX}/contrib/domains")
    result = r.json()
    assert r.status_code == 200
    assert len(result) > 0
    assert result[0] not in CONF.openstack.base_domains


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_keystone_endpoints(client: AsyncClient) -> None:
    r = await client.get(url=f"{main.API_PREFIX}/contrib/keystone_endpoints")
    result = r.json()
    assert r.status_code == 200
    assert len(result) > 0
