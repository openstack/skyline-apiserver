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

from typing import List

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.client.openstack import system
from skyline_apiserver.client.openstack.system import get_domains, get_endpoints, get_regions

router = APIRouter()


@router.get(
    "/contrib/keystone_endpoints",
    description="List Keystone Endpoints",
    responses={
        200: {"model": List[schemas.KeystoneEndpoints]},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=List[schemas.KeystoneEndpoints],
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_keystone_endpoints() -> List[schemas.KeystoneEndpoints]:
    try:
        regions = system.get_regions()
        result = []
        for region in regions:
            endpoints = get_endpoints(region)
            result.append(
                schemas.KeystoneEndpoints(
                    **{"region_name": region, "url": endpoints.get("keystone")}
                )
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/contrib/domains",
    description="List Domains",
    responses={
        200: {"model": List[str]},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_domains(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> List[str]:
    return get_domains("", profile.region)


@router.get(
    "/contrib/regions",
    description="List Regions",
    responses={
        200: {"model": List[str]},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_regions() -> List[str]:
    return get_regions()
