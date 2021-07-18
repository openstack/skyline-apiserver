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
import uuid
from typing import Any, Dict

import pytest
from httpx import AsyncClient
from six.moves.urllib import parse

from skyline_apiserver import main


@pytest.mark.parametrize(
    ("params", "status_code"),
    (
        ({}, 200),
        ({"limit": 10}, 200),
        ({"limit": 20, "marker": str(uuid.uuid4())}, 400),
        ({"sort_dirs": "desc", "sort_keys": "uuid"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "display_name"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "vm_state"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "locked"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "created_at"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "host"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "project_id"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "abc123"}, 422),
        ({"all_projects": True}, 200),
        ({"all_projects": True, "project_id": str(uuid.uuid4())}, 200),
        ({"all_projects": True, "project_name": "test-project"}, 200),
        (
            {
                "all_projects": True,
                "project_id": str(uuid.uuid4()),
                "project_name": "test-project",
            },
            200,
        ),
        ({"name": "abc123"}, 200),
        ({"status": "ACTIVE"}, 200),
        ({"host": "host01"}, 200),
        ({"flavor_id": "abc123"}, 200),
        ({"uuid": [str(uuid.uuid4())]}, 200),
    ),
)
@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_servers(
    client: AsyncClient,
    login_jwt: str,
    params: Dict[str, Any],
    status_code: int,
) -> None:
    # list servers
    url = f"{main.API_PREFIX}/extension/servers" + "?%s" % parse.urlencode(params)
    r = await client.get(
        url=url,
        headers={"Content-Type": "application/json"},
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == status_code
    if status_code == 200:
        assert "servers" in result


@pytest.mark.parametrize(
    ("params", "status_code"),
    (
        ({}, 200),
        ({"limit": 10}, 200),
        ({"limit": 20, "marker": str(uuid.uuid4())}, 400),
        ({"sort_dirs": "desc", "sort_keys": "uuid"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "display_name"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "updated_at"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "project_id"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "abc123"}, 422),
        ({"all_projects": True}, 200),
        ({"all_projects": True, "project_id": str(uuid.uuid4())}, 200),
        ({"all_projects": True, "project_name": "test-project"}, 200),
        (
            {
                "all_projects": True,
                "project_id": str(uuid.uuid4()),
                "project_name": "test-project",
            },
            200,
        ),
        ({"name": "abc123"}, 200),
        ({"uuid": [str(uuid.uuid4())]}, 200),
    ),
)
@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_recycle_servers(
    client: AsyncClient,
    login_jwt: str,
    params: Dict[str, Any],
    status_code: int,
) -> None:
    # list recycle servers
    url = f"{main.API_PREFIX}/extension/recycle_servers" + "?%s" % parse.urlencode(params)
    r = await client.get(
        url=url,
        headers={"Content-Type": "application/json"},
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == status_code
    if status_code == 200:
        assert "recycle_servers" in result


@pytest.mark.parametrize(
    ("params", "status_code"),
    (
        ({}, 200),
        ({"limit": 10}, 200),
        ({"limit": 20, "marker": str(uuid.uuid4())}, 500),
        ({"sort_dirs": "desc", "sort_keys": "id"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "name"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "size"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "status"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "bootable"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "created_at"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "abc123"}, 422),
        ({"all_projects": True}, 200),
        ({"all_projects": True, "project_id": str(uuid.uuid4())}, 200),
        ({"name": "abc123"}, 200),
        ({"multiattach": True}, 200),
        ({"status": "available"}, 200),
        ({"uuid": [str(uuid.uuid4())]}, 200),
    ),
)
@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_volumes(
    client: AsyncClient,
    login_jwt: str,
    params: Dict[str, Any],
    status_code: int,
) -> None:
    # list volumes
    url = f"{main.API_PREFIX}/extension/volumes" + "?%s" % parse.urlencode(params)
    r = await client.get(
        url=url,
        headers={"Content-Type": "application/json"},
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == status_code
    if status_code == 200:
        assert "volumes" in result
        assert "count" in result


@pytest.mark.parametrize(
    ("params", "status_code"),
    (
        ({}, 200),
        ({"limit": 10}, 200),
        ({"limit": 20, "marker": str(uuid.uuid4())}, 500),
        ({"sort_dirs": "desc", "sort_keys": "id"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "name"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "status"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "created_at"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "abc123"}, 422),
        ({"all_projects": True}, 200),
        ({"all_projects": True, "project_id": str(uuid.uuid4())}, 200),
        ({"name": "abc123"}, 200),
        ({"status": "AVAILABLE"}, 200),
        ({"volume_id": str(uuid.uuid4())}, 200),
    ),
)
@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_volume_snapshots(
    client: AsyncClient,
    login_jwt: str,
    params: Dict[str, Any],
    status_code: int,
) -> None:
    # list volume snapshots
    url = f"{main.API_PREFIX}/extension/volume_snapshots" + "?%s" % parse.urlencode(params)
    r = await client.get(
        url=url,
        headers={"Content-Type": "application/json"},
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == status_code
    if status_code == 200:
        assert "volume_snapshots" in result
        assert "count" in result


@pytest.mark.parametrize(
    ("params", "status_code"),
    (
        ({}, 200),
        ({"limit": 10}, 200),
        ({"limit": 20, "marker": str(uuid.uuid4())}, 404),
        ({"sort_dirs": "desc", "sort_keys": "id"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "name"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "mac_address"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "status"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "project_id"}, 200),
        ({"sort_dirs": "desc", "sort_keys": "abc123"}, 422),
        ({"all_projects": True}, 200),
        ({"all_projects": True, "project_id": str(uuid.uuid4())}, 200),
        ({"name": "abc123"}, 200),
        ({"status": "ACTIVE"}, 200),
        ({"network_name": "net01"}, 200),
        ({"network_id": str(uuid.uuid4())}, 200),
        ({"device_id": str(uuid.uuid4())}, 200),
        ({"device_owner": "compute:nova"}, 200),
        ({"uuid": [str(uuid.uuid4())]}, 200),
    ),
)
@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_ports(
    client: AsyncClient,
    login_jwt: str,
    params: Dict[str, Any],
    status_code: int,
) -> None:
    # list ports
    url = f"{main.API_PREFIX}/extension/ports" + "?%s" % parse.urlencode(params)
    r = await client.get(
        url=url,
        headers={"Content-Type": "application/json"},
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == status_code
    if status_code == 200:
        assert "ports" in result


@pytest.mark.parametrize(
    ("params", "status_code"),
    (
        ({}, 200),
        ({"binary": "nova-compute"}, 200),
        ({"host": "host01"}, 200),
    ),
)
@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_compute_services(
    client: AsyncClient,
    login_jwt: str,
    params: Dict[str, Any],
    status_code: int,
) -> None:
    url = f"{main.API_PREFIX}/extension/compute-services" + "?%s" % parse.urlencode(params)
    r = await client.get(
        url=url,
        headers={"Content-Type": "application/json"},
        cookies={"session": login_jwt},
    )
    result = r.json()
    assert r.status_code == status_code
    if status_code == 200:
        assert "services" in result
