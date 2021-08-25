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

from typing import Any, Dict

from fastapi import HTTPException, status
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.session import Session
from starlette.concurrency import run_in_threadpool

from skyline_apiserver import schemas
from skyline_apiserver.client import utils


async def list_projects(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    all_projects: bool,
    search_opts: Dict[str, Any] = None,
) -> Any:
    try:
        search_opts = search_opts if search_opts else {}
        kc = await utils.keystone_client(
            session=session,
            region=profile.region,
            global_request_id=global_request_id,
        )
        if not all_projects:
            search_opts["user"] = profile.user.id
        return await run_in_threadpool(kc.projects.list, **search_opts)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def revoke_token(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    token: str,
) -> None:
    """Revoke a token.
    :param token: The token to be revoked.
    :type token: str or :class:`keystoneclient.access.AccessInfo`
    """
    try:
        kc = await utils.keystone_client(
            session=session,
            region=profile.region,
            global_request_id=global_request_id,
        )
        kwargs = {"token": token}
        await run_in_threadpool(kc.tokens.revoke_token, **kwargs)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
