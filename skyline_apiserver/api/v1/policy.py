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
from skyline_apiserver.client.utils import generate_session, get_access
from skyline_apiserver.policy import ENFORCER, UserContext
from skyline_apiserver.schemas import Policies, PoliciesRules, common

router = APIRouter()


@router.get(
    "/policies",
    description="List policies and permissions",
    responses={
        200: {"model": Policies},
        401: {"model": common.UnauthorizedMessage},
        500: {"model": common.InternalServerErrorMessage},
    },
    response_model=Policies,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def list_policies(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
):
    session = await generate_session(profile)
    access = await get_access(session)
    user_context = UserContext(access)
    target = {
        "user_id": profile.user.id,
        "project_id": profile.project.id,
    }
    result = [
        {"rule": rule, "allowed": ENFORCER.authorize(rule, target, user_context)}
        for rule in ENFORCER.rules
    ]
    return {"policies": result}


@router.post(
    "/policies/check",
    description="Check policies permissions",
    responses={
        200: {"model": Policies},
        401: {"model": common.UnauthorizedMessage},
        403: {"model": common.ForbiddenMessage},
        500: {"model": common.InternalServerErrorMessage},
    },
    response_model=Policies,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def check_policies(
    policy_rules: PoliciesRules,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
):
    session = await generate_session(profile)
    access = await get_access(session)
    user_context = UserContext(access)
    target = {
        "user_id": profile.user.id,
        "project_id": profile.project.id,
    }
    try:
        result = [
            {"rule": rule, "allowed": ENFORCER.authorize(rule, target, user_context)}
            for rule in policy_rules.rules
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return {"policies": result}
