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

from typing import Any, Dict, Optional

from cinderclient.exceptions import NotFound
from fastapi import status
from fastapi.exceptions import HTTPException
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.session import Session

from skyline_apiserver import schemas
from skyline_apiserver.client import utils


def list_volumes(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    limit: Optional[int] = None,
    marker: Optional[str] = None,
    search_opts: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None,
) -> Any:
    try:
        cc = utils.cinder_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return cc.volumes.list(
            search_opts=search_opts,
            limit=limit,
            marker=marker,
            sort=sort,
        )
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


def list_volume_snapshots(
    profile: schemas.Profile,
    session: Session,
    global_request_id: str,
    limit: Optional[int] = None,
    marker: Optional[str] = None,
    search_opts: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None,
) -> Any:
    try:
        cc = utils.cinder_client(
            region=profile.region,
            session=session,
            global_request_id=global_request_id,
        )
        return cc.volume_snapshots.list(
            search_opts=search_opts,
            limit=limit,
            marker=marker,
            sort=sort,
        )
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


def get_volume_snapshot(
    session: Session,
    region: str,
    global_request_id: str,
    snapshot_id: str,
) -> Any:
    try:
        cc = utils.cinder_client(
            session=session, region=region, global_request_id=global_request_id
        )
        return cc.volume_snapshots.get(snapshot_id)
    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except NotFound as e:
        raise e
