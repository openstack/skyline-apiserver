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

from typing import Iterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from skyline_apiserver.config import CONF
from skyline_apiserver.main import app
from utils import utils


@pytest.fixture(scope="function")
async def client() -> Iterator[AsyncClient]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    CONF.cleanup()


@pytest.fixture(scope="function")
async def session_token(client: AsyncClient) -> str:
    return utils.get_session_token()


@pytest.fixture(scope="function")
async def login_jwt(client: AsyncClient) -> str:
    return await utils.get_jwt_from_cookie(client)
