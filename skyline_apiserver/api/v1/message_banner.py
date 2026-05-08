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

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.db import api as db_api
from skyline_apiserver.utils.rackspace_status import (
    fetch_rackspace_status_message_banner_values,
)
from skyline_apiserver.utils.roles import assert_system_admin

router = APIRouter()
RACKSPACE_STATUS_SYNC_INTERVAL = 300
_rackspace_status_last_sync = 0.0


def _format_message_banner(message_banner) -> schemas.MessageBanner:
    if isinstance(message_banner, schemas.MessageBanner):
        return message_banner
    if isinstance(message_banner, dict):
        return schemas.MessageBanner(**message_banner)
    return schemas.MessageBanner(**dict(message_banner._mapping))


def _format_message_banners(message_banners) -> schemas.MessageBanners:
    return schemas.MessageBanners(
        message_banners=[
            _format_message_banner(message_banner) for message_banner in message_banners
        ]
    )


def _assert_message_banner_exist(banner_id: str):
    message_banner = db_api.get_message_banner(banner_id)
    if message_banner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message banner not found.",
        )
    return message_banner


def _model_dump(model) -> dict:
    return model.model_dump()


def _sync_rackspace_status_feed(force: bool = False) -> None:
    global _rackspace_status_last_sync

    now = time.time()
    if not force and now - _rackspace_status_last_sync < RACKSPACE_STATUS_SYNC_INTERVAL:
        return

    for values in fetch_rackspace_status_message_banner_values():
        db_api.sync_servicenow_ext_message_banner(values)
    _rackspace_status_last_sync = now


def _assert_same_region(message_banner, profile: schemas.Profile) -> None:
    region = getattr(message_banner, "region", None)
    if region and region != profile.region:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to manage message banners for another region.",
        )


def _manual_message_values(message_banner, profile: schemas.Profile) -> dict:
    values = _model_dump(message_banner)
    region = values.get("region") or profile.region
    if region != profile.region:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create message banners for another region.",
        )
    values.update(
        {
            "project_id": profile.project.id,
            "region": region,
            "source": "manual",
            "source_id": None,
            "source_url": None,
        }
    )
    return values


def _message_update_values(message_banner, existing_message_banner, profile) -> dict:
    values = _model_dump(message_banner)
    region = values.get("region") or existing_message_banner.region or profile.region
    if region != profile.region:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update message banners for another region.",
        )

    values["region"] = region
    if existing_message_banner.source != "manual":
        values.update(
            {
                "source": existing_message_banner.source,
                "source_id": existing_message_banner.source_id,
                "source_url": existing_message_banner.source_url,
            }
        )
        return values

    values.update(
        {
            "source": "manual",
            "source_id": None,
            "source_url": None,
        }
    )
    return values


@router.get(
    "/message-banners/active",
    description="Get active dashboard message banners.",
    responses={
        200: {"model": schemas.MessageBanners},
        401: {"model": schemas.UnauthorizedMessage},
    },
    response_model=schemas.MessageBanners,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_active_message_banners(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.MessageBanners:
    project_id = profile.project.id
    _sync_rackspace_status_feed()
    banners = db_api.list_active_message_banners(
        project_id=project_id,
        region=profile.region,
    )
    return _format_message_banners(banners)


@router.get(
    "/message-banners",
    description="Get all message banners.",
    responses={
        200: {"model": schemas.MessageBanners},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
    },
    response_model=schemas.MessageBanners,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_message_banners(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.MessageBanners:
    assert_system_admin(
        profile=profile,
        exception="Not allowed to list message banners.",
    )
    _sync_rackspace_status_feed()
    banners = db_api.list_message_banners(region=profile.region)
    return _format_message_banners(banners)


@router.get(
    "/message-banners/{banner_id}",
    description="Get a message banner.",
    responses={
        200: {"model": schemas.MessageBanner},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        404: {"model": schemas.NotFoundMessage},
    },
    response_model=schemas.MessageBanner,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def show_message_banner(
    banner_id: str,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.MessageBanner:
    assert_system_admin(
        profile=profile,
        exception="Not allowed to get message banners.",
    )
    message_banner = _assert_message_banner_exist(banner_id)
    _assert_same_region(message_banner, profile)
    return _format_message_banner(message_banner)


@router.post(
    "/message-banners",
    description="Create a message banner.",
    responses={
        200: {"model": schemas.MessageBanner},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
    },
    response_model=schemas.MessageBanner,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def create_message_banner(
    message_banner: schemas.CreateMessageBanner,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.MessageBanner:
    assert_system_admin(
        profile=profile,
        exception="Not allowed to create message banners.",
    )
    new_message_banner = db_api.create_message_banner(
        _manual_message_values(message_banner, profile)
    )
    return _format_message_banner(new_message_banner)


@router.put(
    "/message-banners/{banner_id}",
    description="Update a message banner.",
    responses={
        200: {"model": schemas.MessageBanner},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        404: {"model": schemas.NotFoundMessage},
    },
    response_model=schemas.MessageBanner,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def update_message_banner(
    banner_id: str,
    message_banner: schemas.UpdateMessageBanner,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.MessageBanner:
    assert_system_admin(
        profile=profile,
        exception="Not allowed to update message banners.",
    )
    existing_message_banner = _assert_message_banner_exist(banner_id)
    _assert_same_region(existing_message_banner, profile)
    updated_message_banner = db_api.update_message_banner(
        banner_id,
        _message_update_values(message_banner, existing_message_banner, profile),
    )
    return _format_message_banner(updated_message_banner)


@router.delete(
    "/message-banners/{banner_id}",
    description="Delete a message banner.",
    responses={
        200: {"model": schemas.MessageBanner},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        404: {"model": schemas.NotFoundMessage},
    },
    response_model=schemas.MessageBanner,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def delete_message_banner(
    banner_id: str,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.MessageBanner:
    assert_system_admin(
        profile=profile,
        exception="Not allowed to delete message banners.",
    )
    existing_message_banner = _assert_message_banner_exist(banner_id)
    _assert_same_region(existing_message_banner, profile)
    deleted_message_banner = db_api.delete_message_banner(banner_id)
    return _format_message_banner(deleted_message_banner)
