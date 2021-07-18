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
from typing import Optional

import jose
from fastapi import HTTPException, Request, Response, status
from fastapi.security import APIKeyCookie

from skyline_apiserver import schemas
from skyline_apiserver.config import CONF
from skyline_apiserver.core.security import generate_profile_by_token, parse_access_token
from skyline_apiserver.db import api as db_api
from skyline_apiserver.types import constants


class TokenCookie(APIKeyCookie):
    async def __call__(self, request: Request) -> Optional[str]:
        api_key = request.cookies.get(self.model.name)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=constants.ERR_MSG_TOKEN_NOTFOUND,
            )
        return api_key


async def getJWTPayload(request: Request) -> (str):
    token = request.cookies.get(CONF.default.session_name)
    return token


async def get_profile(request: Request) -> schemas.Profile:
    payload = await TokenCookie(name=CONF.default.session_name)(request)
    try:
        await db_api.purge_revoked_token()
        token = parse_access_token(payload)
        is_revoked = await db_api.check_token(token.uuid)
        if is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=constants.ERR_MSG_TOKEN_REVOKED,
            )
        profile = await generate_profile_by_token(token)
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.detail,
        )
    except jose.exceptions.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=constants.ERR_MSG_TOKEN_EXPIRED + " : " + str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    return profile


async def get_profile_update_jwt(request: Request, response: Response) -> schemas.Profile:
    profile = await get_profile(request)

    if 0 < profile.exp - time.time() < CONF.default.access_token_renew:
        profile.exp = int(time.time()) + CONF.default.access_token_expire
        response.set_cookie(CONF.default.session_name, profile.toJWTPayload())
    return profile
