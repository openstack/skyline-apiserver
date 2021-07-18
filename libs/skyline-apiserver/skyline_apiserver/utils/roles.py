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

from fastapi import HTTPException, status

from skyline_apiserver import schemas
from skyline_apiserver.config import CONF


def is_system_admin(profile: schemas.Profile) -> bool:
    roles = set(role.name for role in profile.roles)
    if roles & set(CONF.openstack.system_admin_roles):
        return True
    return False


def is_system_reader_no_admin(profile: schemas.Profile) -> bool:
    roles = set(role.name for role in profile.roles)
    if (roles & set(CONF.openstack.system_reader_roles)) and (
        not roles & set(CONF.openstack.system_admin_roles)
    ):
        return True
    return False


def is_system_admin_or_reader(profile: schemas.Profile) -> bool:
    roles = set(role.name for role in profile.roles)
    if roles & set(CONF.openstack.system_admin_roles + CONF.openstack.system_reader_roles):
        return True
    return False


def assert_system_admin(profile: schemas.Profile, exception: str) -> None:
    if not is_system_admin(profile):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exception,
        )


def assert_system_admin_or_reader(profile: schemas.Profile, exception: str) -> None:
    if not is_system_admin_or_reader(profile):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exception,
        )
