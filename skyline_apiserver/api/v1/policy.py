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

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from keystoneauth1.exceptions.http import Unauthorized as KeystoneUnauthorized

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.client.utils import generate_session, get_access, get_system_scope_access
from skyline_apiserver.log import LOG
from skyline_apiserver.policy import ENFORCER, UserContext

router = APIRouter()


def _generate_target(profile: schemas.Profile) -> Dict[str, str]:
    return {
        "user_id": profile.user.id,
        "project_id": profile.project.id,
        # trove
        "tenant": profile.project.id,
        # keystone
        "trust.trustor_user_id": profile.user.id,
        "target.user.id": profile.user.id,
        "target.user.domain_id": profile.user.domain.id,
        "target.project.domain_id": profile.project.domain.id,
        "target.project.id": profile.project.id,
        "target.trust.trustor_user_id": profile.user.id,
        "target.trust.trustee_user_id": profile.user.id,
        "target.token.user_id": profile.user.id,
        "target.domain.id": profile.project.domain.id,
        "target.domain_id": profile.project.domain.id,
        "target.credential.user_id": profile.user.id,
        "target.role.domain_id": profile.project.domain.id,
        "target.group.domain_id": profile.project.domain.id,
        "target.limit.domain.id": profile.project.domain.id,
        "target.limit.project_id": profile.project.domain.id,
        "target.limit.project.domain_id": profile.project.domain.id,
        # ironic
        "allocation.owner": profile.project.id,
        "node.lessee": profile.project.id,
        "node.owner": profile.project.id,
        # glance
        "member_id": profile.project.id,
        "owner": profile.project.id,
        # cinder
        "domain_id": profile.project.domain.id,
    }


@router.get(
    "/policies",
    description="List policies and permissions",
    responses={
        200: {"model": schemas.Policies},
        401: {"model": schemas.UnauthorizedMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.Policies,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def list_policies(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Policies:
    session = await generate_session(profile)
    access = await get_access(session)
    user_context = UserContext(access)
    try:
        system_scope_access = await get_system_scope_access(
            profile.keystone_token, profile.region
        )
        user_context["system_scope"] = (
            "all"
            if getattr(system_scope_access, "system")
            and getattr(system_scope_access, "system", {}).get("all", False)
            else user_context["system_scope"]
        )
    except KeystoneUnauthorized:
        # User is not authorized to access the system scope. So just ignore the
        # exception and use the user_context as is.
        LOG.debug("Keystone token is invalid. No privilege to access system scope.")
    target = _generate_target(profile)
    result = [
        {"rule": rule, "allowed": ENFORCER.authorize(rule, target, user_context)}
        for rule in ENFORCER.rules
    ]
    return {"policies": result}


@router.post(
    "/policies/check",
    description="Check policies permissions",
    responses={
        200: {"model": schemas.Policies},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.Policies,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def check_policies(
    policy_rules: schemas.PoliciesRules,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Policies:
    session = await generate_session(profile)
    access = await get_access(session)
    user_context = UserContext(access)
    try:
        system_scope_access = await get_system_scope_access(
            profile.keystone_token, profile.region
        )
        user_context["system_scope"] = (
            "all"
            if getattr(system_scope_access, "system")
            and getattr(system_scope_access, "system", {}).get("all", False)
            else user_context["system_scope"]
        )
    except KeystoneUnauthorized:
        # User is not authorized to access the system scope. So just ignore the
        # exception and use the user_context as is.
        LOG.debug("Keystone token is invalid. No privilege to access system scope.")
    target = _generate_target(profile)
    target.update(policy_rules.target if policy_rules.target else {})
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
