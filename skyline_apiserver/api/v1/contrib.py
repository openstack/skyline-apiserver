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

import asyncio
from typing import Any, List

from fastapi import APIRouter, Header, HTTPException, status

from skyline_apiserver import schemas
from skyline_apiserver.client.openstack import system
from skyline_apiserver.client.openstack.system import get_endpoints
from skyline_apiserver.config import CONF
from skyline_apiserver.log import LOG
from skyline_apiserver.types import constants

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
async def list_keystone_endpoints() -> List[schemas.KeystoneEndpoints]:
    """Contrib List Keystone Endpoints."""
    try:
        regions = await system.get_regions()
        tasks = [asyncio.create_task(get_endpoints(region)) for region in regions]
        endpoints = await asyncio.gather(*tasks)
        result = [
            {"region_name": region, "url": endpoint.get("keystone")}
            for region, endpoint in zip(regions, endpoints)
        ]
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
async def list_domains(
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> Any:
    """Contrib List Domain Names."""

    try:
        regions = await system.get_regions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    for region in regions:
        try:
            domains = await system.get_domains(x_openstack_request_id, region)
            return [domain for domain in domains if domain not in CONF.openstack.base_domains]
        except Exception as e:
            LOG.warning(str(e))
            continue
    return []


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
async def list_regions() -> Any:
    """Contrib List Regions."""
    try:
        return await system.get_regions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
