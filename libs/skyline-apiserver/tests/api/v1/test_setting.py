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

import pytest
from httpx import AsyncClient
from skyline_apiserver import main
from skyline_apiserver.config import CONF
from skyline_apiserver.types import constants


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_list_settings(client: AsyncClient, login_jwt: str) -> None:
    result = await client.get(
        f"{main.API_PREFIX}/settings",
        cookies={"session": login_jwt},
    )
    assert result.status_code == 200
    assert "settings" in result.json()
    settings = result.json()["settings"]
    for setting in settings:
        key = setting["key"]
        assert setting["hidden"] == (key in constants.SETTINGS_HIDDEN_SET)
        assert setting["restart_service"] == (key in constants.SETTINGS_RESTART_SET)
    # settings not only include something in CONF.setting.base_settings


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_default_setting(client: AsyncClient, login_jwt: str) -> None:
    for key in CONF.setting.base_settings:
        result = await client.get(
            f"{main.API_PREFIX}/setting/{key}",
            cookies={"session": login_jwt},
        )
        assert result.status_code == 200


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_get_setting_not_found(client: AsyncClient, login_jwt: str) -> None:
    key = str(uuid.uuid4().hex)
    result = await client.get(
        f"{main.API_PREFIX}/setting/{key}",
        cookies={"session": login_jwt},
    )
    assert result.status_code == 404


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_update_setting(client: AsyncClient, login_jwt: str) -> None:
    for key in CONF.setting.base_settings:
        # Create
        update_value = ["test1", "test2"]
        result = await client.put(
            url=f"{main.API_PREFIX}/setting",
            json={"key": key, "value": update_value},
            cookies={"session": login_jwt},
        )
        assert result.status_code == 200
        assert result.json()["value"] == update_value

        # Update
        update_value = ["test1", "test3"]
        result = await client.put(
            url=f"{main.API_PREFIX}/setting",
            json={"key": key, "value": update_value},
            cookies={"session": login_jwt},
        )
        assert result.status_code == 200
        assert result.json()["value"] == update_value
        break


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_update_setting_not_found(client: AsyncClient, login_jwt: str) -> None:
    key = str(uuid.uuid4().hex)
    update_value = {"value": "{}"}
    result = await client.put(
        url=f"{main.API_PREFIX}/setting",
        json={"key": key, "value": update_value},
        cookies={"session": login_jwt},
    )
    assert result.status_code == 404


@pytest.mark.skipif(os.getenv("TEST_API") != "true", reason="No backend OpenStack for api-test.")
@pytest.mark.asyncio
async def test_reset_setting(client: AsyncClient, login_jwt: str) -> None:
    for key in CONF.setting.base_settings:
        result = await client.delete(
            f"{main.API_PREFIX}/setting/{key}",
            cookies={"session": login_jwt},
        )
        assert result.status_code == 204
        result = await client.get(
            f"{main.API_PREFIX}/setting/{key}",
            cookies={"session": login_jwt},
        )
        assert result.json()["value"] == getattr(CONF.setting, key)
        break
