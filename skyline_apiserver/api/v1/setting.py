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

from fastapi import APIRouter, Depends, HTTPException, status

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.config import CONF
from skyline_apiserver.db import api as db_api
from skyline_apiserver.types import constants
from skyline_apiserver.utils.roles import assert_system_admin

router = APIRouter()


def assert_setting_key_exist(key: str):
    if key not in CONF.setting.base_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not a valid setting key.",
        )


@router.get(
    "/setting/{key}",
    description="Get a setting item.",
    responses={
        200: {"model": schemas.Setting},
        401: {"model": schemas.UnauthorizedMessage},
        404: {"model": schemas.NotFoundMessage},
    },
    response_model=schemas.Setting,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def show_setting(
    key: str,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Setting:
    assert_setting_key_exist(key)
    setting = await db_api.get_setting(key)
    value = getattr(CONF.setting, key) if setting is None else setting.value
    hidden = key in constants.SETTINGS_HIDDEN_SET
    restart_service = key in constants.SETTINGS_RESTART_SET
    return schemas.Setting(key=key, value=value, hidden=hidden, restart_service=restart_service)


@router.put(
    "/setting",
    description="Update a setting item.",
    responses={
        200: {"model": schemas.Setting},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        404: {"model": schemas.NotFoundMessage},
    },
    response_model=schemas.Setting,
    status_code=status.HTTP_200_OK,
    response_description="ok",
)
async def update_setting(
    setting: schemas.UpdateSetting,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Setting:
    assert_system_admin(profile=profile, exception="Not allowed to update settings.")
    assert_setting_key_exist(setting.key)
    setting = await db_api.update_setting(setting.key, setting.value)
    hidden = setting.key in constants.SETTINGS_HIDDEN_SET
    restart_service = setting.key in constants.SETTINGS_RESTART_SET
    return schemas.Setting(
        key=setting.key,
        value=setting.value,
        hidden=hidden,
        restart_service=restart_service,
    )


@router.get(
    "/settings",
    description="Get all settings.",
    responses={
        200: {"model": schemas.Settings},
        401: {"model": schemas.UnauthorizedMessage},
    },
    response_model=schemas.Settings,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def list_settings(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Settings:
    settings = {
        k: schemas.Setting(
            key=k,
            value=getattr(CONF.setting, k),
            hidden=k in constants.SETTINGS_HIDDEN_SET,
            restart_service=k in constants.SETTINGS_RESTART_SET,
        )
        for k in CONF.setting.base_settings
    }
    db_settings = await db_api.list_settings()
    for item in db_settings:
        if item.key in CONF.setting.base_settings:
            settings[item.key].value = item.value
    settings = list(settings.values())
    return schemas.Settings(settings=settings)


@router.delete(
    "/setting/{key}",
    description="Reset a setting item to default",
    responses={
        204: {"model": None},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        404: {"model": schemas.NotFoundMessage},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="No Content",
)
async def reset_setting(
    key: str,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> None:
    assert_system_admin(profile=profile, exception="Not allowed to reset settings.")
    assert_setting_key_exist(key)
    await db_api.delete_setting(key)
