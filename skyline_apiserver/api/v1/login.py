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

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session
from keystoneclient.client import Client as KeystoneClient

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.client import utils
from skyline_apiserver.client.openstack.keystone import revoke_token
from skyline_apiserver.client.openstack.system import (
    get_endpoints,
    get_project_scope_token,
    get_projects,
)
from skyline_apiserver.client.utils import generate_session, get_system_session
from skyline_apiserver.config import CONF
from skyline_apiserver.core.security import (
    generate_profile,
    generate_profile_by_token,
    parse_access_token,
)
from skyline_apiserver.db import api as db_api
from skyline_apiserver.log import LOG
from skyline_apiserver.types import constants

router = APIRouter()


async def _patch_profile(profile: schemas.Profile, global_request_id: str) -> schemas.Profile:
    try:
        profile.endpoints = await get_endpoints(region=profile.region)
        profile.projects = await get_projects(
            global_request_id=global_request_id,
            region=profile.region,
            user=profile.user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    return profile


@router.post(
    "/login",
    description="Login & get user profile.",
    responses={
        200: {"model": schemas.Profile},
        401: {"model": schemas.UnauthorizedMessage},
    },
    response_model=schemas.Profile,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def login(
    request: Request,
    response: Response,
    credential: schemas.Credential,
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
):
    try:
        auth_url = await utils.get_endpoint(
            region=credential.region,
            service="keystone",
            session=get_system_session(),
        )
        unscope_auth = Password(
            auth_url=auth_url,
            user_domain_name=credential.domain,
            username=credential.username,
            password=credential.password,
            reauthenticate=False,
        )
        session = Session(auth=unscope_auth, verify=False, timeout=constants.DEFAULT_TIMEOUT)
        unscope_client = KeystoneClient(
            session=session,
            endpoint=auth_url,
            interface=CONF.openstack.interface_type,
        )
        project_scope = unscope_client.auth.projects()
        # we must get the project_scope with enabled project
        project_scope = [scope for scope in project_scope if scope.enabled]
        if not project_scope:
            raise Exception("You are not authorized for any projects or domains.")

        project_scope_token = await get_project_scope_token(
            keystone_token=session.get_token(),
            region=credential.region,
            project_id=project_scope[0].id,
        )

        profile = await generate_profile(
            keystone_token=project_scope_token,
            region=credential.region,
        )

        profile = await _patch_profile(profile, x_openstack_request_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    else:
        response.set_cookie(CONF.default.session_name, profile.toJWTPayload())
        return profile


@router.get(
    "/profile",
    description="Get user profile.",
    responses={
        200: {"model": schemas.Profile},
        401: {"model": schemas.UnauthorizedMessage},
    },
    response_model=schemas.Profile,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def get_profile(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
):
    return await _patch_profile(profile, x_openstack_request_id)


@router.post(
    "/logout",
    description="Log out.",
    responses={
        200: {"model": schemas.Message},
    },
    response_model=schemas.Message,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def logout(
    response: Response,
    request: Request,
    payload: str = Depends(deps.getJWTPayload),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
):
    if payload:
        try:
            token = parse_access_token(payload)
            profile = await generate_profile_by_token(token)
            session = await generate_session(profile)
            await revoke_token(profile, session, x_openstack_request_id, token.keystone_token)
            await db_api.revoke_token(profile.uuid, profile.exp)
        except Exception as e:
            LOG.debug(str(e))
    response.delete_cookie(CONF.default.session_name)
    return schemas.Message(message="Logout OK")


@router.post(
    "/switch_project/{project_id}",
    description="Switch project.",
    responses={
        200: {"model": schemas.Profile},
        401: {"model": schemas.UnauthorizedMessage},
    },
    response_model=schemas.Profile,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def switch_project(
    project_id: str,
    response: Response,
    profile: schemas.Profile = Depends(deps.get_profile),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
):
    try:
        project_scope_token = await get_project_scope_token(
            keystone_token=profile.keystone_token,
            region=profile.region,
            project_id=project_id,
        )

        profile = await generate_profile(
            keystone_token=project_scope_token,
            region=profile.region,
            uuid_value=profile.uuid,
        )
        profile = await _patch_profile(profile, x_openstack_request_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    else:
        response.set_cookie(CONF.default.session_name, profile.toJWTPayload())
        return profile
