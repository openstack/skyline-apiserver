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

import base64
import json
import time
import uuid
import zlib
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt
from skyline_log import LOG

from skyline_apiserver import __version__
from skyline_apiserver import schemas
from skyline_apiserver.client import utils
from skyline_apiserver.client.utils import get_system_session
from skyline_apiserver.config import CONF
from skyline_apiserver.db import api as db_api
from skyline_apiserver.types import constants

LICENSE = None
CURRENCY = None


def parse_access_token(token: str) -> (schemas.Payload):
    payload = jwt.decode(token, CONF.default.secret_key)
    return schemas.Payload(
        keystone_token=payload["keystone_token"],
        region=payload["region"],
        exp=payload["exp"],
        uuid=payload["uuid"],
    )


async def generate_profile_by_token(token: schemas.Payload) -> schemas.Profile:
    return await generate_profile(
        keystone_token=token.keystone_token,
        region=token.region,
        exp=token.exp,
        uuid_value=token.uuid,
    )


async def get_license() -> Optional[schemas.License]:
    global LICENSE
    if LICENSE is not None:
        # Restart process or docker container to refresh
        return LICENSE

    db_license = await db_api.get_setting("license")
    if db_license is None:
        return None

    raw_data_bs = db_license.value.encode("utf-8")
    try:
        license_bs = base64.decodebytes(raw_data_bs)[256:]
        license_content = json.loads(zlib.decompress(license_bs))
    except Exception as e:
        LOG.error(e)
        msg = "License can not be parsed"
        LOG.error(msg)
        return None

    features = license_content["features"]
    addons = any([features, lambda x: "addons" in x])
    # In order to compatible the old license[no include addons field],
    # by default, we set firewall and loadbalance as default features.
    if not addons:
        features.append({"addons": ";".join(constants.ADDONS_DEFAULT)})

    LICENSE = schemas.License(
        name=license_content["name"],
        summary=license_content["summary"],
        macs=license_content["macs"],
        features=features,
        start=license_content["period"]["start"],
        end=license_content["period"]["end"],
    )

    return LICENSE


async def get_currency() -> dict:
    global CURRENCY
    if CURRENCY is not None:
        return CURRENCY

    db_currency = await db_api.get_setting("currency")
    if db_currency and type(db_currency.value) == dict:
        CURRENCY = db_currency.value

    if CURRENCY is None:
        CURRENCY = getattr(CONF.setting, "currency")
    return CURRENCY


async def generate_profile(
    keystone_token: str,
    region: str,
    exp: int = None,
    uuid_value: str = None,
) -> schemas.Profile:
    license = await get_license()
    currency = await get_currency()
    try:
        kc = await utils.keystone_client(session=get_system_session(), region=region)
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
            base_roles=CONF.openstack.base_roles,
            base_domains=CONF.openstack.base_domains,
            exp=exp or int(time.time()) + CONF.default.access_token_expire,
            uuid=uuid_value or uuid.uuid4().hex,
            version=__version__,
            license=license,
            currency=currency,
        )
