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

from typing import Dict, List

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from keystoneauth1.exceptions.http import (
    InternalServerError as KeystoneInternalServerError,
    Unauthorized as KeystoneUnauthorized,
)

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.client.utils import generate_session, get_access, get_system_scope_access
from skyline_apiserver.config import CONF
from skyline_apiserver.log import LOG
from skyline_apiserver.policy import ENFORCER, UserContext
from skyline_apiserver.types import constants

router = APIRouter()


def _generate_target(profile: schemas.Profile) -> Dict[str, str]:
    return {
        "user_id": profile.user.id,
        "project_id": profile.project.id,
        # oslo policy
        "enforce_new_defaults": CONF.openstack.enforce_new_defaults,
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
        # barbican
        "target.container.project_id": profile.project.id,
        "target.secret.project_id": profile.project.id,
        "target.order.project_id": profile.project.id,
        "target.secret.creator_id": profile.user.id,
        # ironic
        "allocation.owner": profile.project.id,
        "node.lessee": profile.project.id,
        "node.owner": profile.project.id,
        # glance
        "member_id": profile.project.id,
        "owner": profile.project.id,
        # cinder
        "domain_id": profile.project.domain.id,
        # neutron
        "tenant_id": profile.project.id,
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
def list_policies(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Policies:
    session = generate_session(profile)
    access = get_access(session)
    user_context = UserContext(access)
    try:
        system_scope_access = get_system_scope_access(profile.keystone_token, profile.region)
        user_context["system_scope"] = (
            "all"
            if getattr(system_scope_access, "system")
            and getattr(system_scope_access, "system", {}).get("all", False)
            else user_context["system_scope"]
        )
    except KeystoneUnauthorized:
        LOG.debug("Keystone token is invalid. No privilege to access system scope.")
    except KeystoneInternalServerError:
        LOG.debug("Keystone is not reachable. No privilege to access system scope.")
    target = _generate_target(profile)

    results: List = []
    services = constants.SUPPORTED_SERVICE_EPS.keys()
    for service in services:
        try:
            enforcer = ENFORCER[service]
            result = [
                {
                    "rule": f"{service}:{rule}",
                    "allowed": enforcer.authorize(rule, target, user_context),
                }
                for rule in enforcer.rules
            ]
            results.extend(result)
        except Exception:
            msg = "An error occurred when calling %(service)s enforcer." % {
                "service": str(service)
            }
            LOG.warning(msg)

    return schemas.Policies(**{"policies": results})


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
def check_policies(
    policy_rules: schemas.PoliciesRules,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Policies:
    session = generate_session(profile)
    access = get_access(session)
    user_context = UserContext(access)
    try:
        system_scope_access = get_system_scope_access(profile.keystone_token, profile.region)
        user_context["system_scope"] = (
            "all"
            if getattr(system_scope_access, "system")
            and getattr(system_scope_access, "system", {}).get("all", False)
            else user_context["system_scope"]
        )
    except KeystoneUnauthorized:
        LOG.debug("Keystone token is invalid. No privilege to access system scope.")
    except KeystoneInternalServerError:
        LOG.debug("Keystone is not reachable. No privilege to access system scope.")
    target = _generate_target(profile)
    target.update(policy_rules.target if policy_rules.target else {})
    try:
        result: List = []
        for policy_rule in policy_rules.rules:
            service = policy_rule.split(":", 1)[0]
            rule = policy_rule.split(":", 1)[1]
            enforcer = ENFORCER[service]
            result.append(
                {"rule": policy_rule, "allowed": enforcer.authorize(rule, target, user_context)}
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return schemas.Policies(**{"policies": result})
