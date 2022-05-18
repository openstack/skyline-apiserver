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
from novaclient.exceptions import BadRequest, Forbidden
from starlette.concurrency import run_in_threadpool

from skyline_apiserver import schemas
from skyline_apiserver.client import utils


async def list_servers(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    search_opts: Dict[str, Any] = None,
    marker: str = None,
    limit: int = None,
    sort_keys: str = None,
    sort_dirs: str = None,
) -> Any:
    try:
        nc = await utils.nova_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(
            nc.servers.list,
            search_opts=search_opts,
            marker=marker,
            limit=limit,
            sort_keys=sort_keys,
            sort_dirs=sort_dirs,
        )
    except BadRequest as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Forbidden as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def list_services(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    **kwargs: Any,
) -> Any:
    try:
        nc = await utils.nova_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(nc.services.list, **kwargs)
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
