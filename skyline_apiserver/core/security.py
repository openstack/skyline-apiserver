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

import time
import uuid
from typing import Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from jose import jwt

from skyline_apiserver import schemas, version
from skyline_apiserver.client import utils
from skyline_apiserver.client.utils import get_system_session
from skyline_apiserver.config import CONF


def parse_access_token(token: str) -> (schemas.Payload):
    payload = jwt.decode(token, CONF.default.secret_key, algorithms=["HS256"])
    return schemas.Payload(
        keystone_token=payload["keystone_token"],
        region=payload["region"],
        exp=payload["exp"],
        uuid=payload["uuid"],
    )


def generate_profile_by_token(token: schemas.Payload) -> schemas.Profile:
    return generate_profile(
        keystone_token=token.keystone_token,
        region=token.region,
        exp=token.exp,
        uuid_value=token.uuid,
    )


def generate_profile(
    keystone_token: str,
    region: str,
    exp: Optional[int] = None,
    uuid_value: Optional[str] = None,
) -> schemas.Profile:
    try:
        kc = utils.keystone_client(session=get_system_session(), region=region)
        token_data = kc.tokens.get_token_data(token=keystone_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    else:
        return schemas.Profile(
            keystone_token=keystone_token,
            region=region,
            project=token_data["token"]["project"],
            user=token_data["token"]["user"],
            roles=token_data["token"]["roles"],
            keystone_token_exp=token_data["token"]["expires_at"],
            base_domains=CONF.openstack.base_domains,
            exp=exp or int(time.time()) + CONF.default.access_token_expire,
            uuid=uuid_value or uuid.uuid4().hex,
            version=version.version_string(),
        )
