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

from typing import Any

from fastapi import HTTPException, status
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.session import Session
from starlette.concurrency import run_in_threadpool

from skyline_apiserver import schemas
from skyline_apiserver.client import utils


async def list_networks(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    **kwargs: Any,
) -> Any:
    try:
        nc = await utils.neutron_client(
            session=session,
            region=profile.region,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(nc.list_networks, **kwargs)
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


async def list_ports(
    session: Session,
    region_name: str,
    global_request_id: str,
    **kwargs: Any,
) -> Any:
    try:
        nc = await utils.neutron_client(
            session=session,
            region=region_name,
            global_request_id=global_request_id,
        )
        return await run_in_threadpool(nc.list_ports, **kwargs)
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
