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

from typing import Any, Dict, List, Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from keystoneauth1.exceptions.http import (
    InternalServerError as KeystoneInternalServerError,
    Unauthorized as KeystoneUnauthorized,
)
from keystoneauth1.identity.v3 import Token
from keystoneauth1.session import Session
from starlette.requests import Request

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.client.utils import (
    generate_session,
    get_access,
    get_endpoint,
    get_system_scope_access,
    get_system_session,
)
from skyline_apiserver.config import CONF
from skyline_apiserver.log import LOG
from skyline_apiserver.policy import ENFORCER, UserContext
from skyline_apiserver.types import constants

router = APIRouter()

# Services whose rules are evaluated a second time with the domain-scoped token
DOMAIN_SCOPE_SERVICES = ("keystone",)


def _generate_domain_target(profile: schemas.Profile) -> Dict[str, str]:
    """Policy target for the domain-scoped evaluation: everything belongs to the user's domain."""
    domain_id = profile.domain.id if profile.domain else profile.user.domain.id
    target = _generate_target(profile)
    target.update(
        {
            "target.user.domain_id": domain_id,
            "target.project.domain_id": domain_id,
            "target.domain.id": domain_id,
            "target.domain_id": domain_id,
            "target.role.domain_id": domain_id,
            "target.group.domain_id": domain_id,
            "target.limit.domain.id": domain_id,
            "domain_id": domain_id,
            # generic evaluation of grant rules: the least privileged role a manager may assign
            "target.role.name": "member",
        }
    )
    return target


def _domain_user_context(
    profile: schemas.Profile, original_ip: Optional[str] = None
) -> Optional[UserContext]:
    """Credentials of the domain-scoped token, or None when the session has none.

    Keystone rules compare ``token.domain.id`` (oslo.policy resolves dotted keys as nested
    lookups), so the ``token`` entry mirrors the shape Keystone itself uses.
    """
    if not profile.domain_scope_token or not profile.domain:
        return None
    try:
        auth_url = get_endpoint(
            profile.region, "identity", get_system_session(original_ip=original_ip)
        )
        # keep the domain scope: a bare token auth would re-scope to the default project
        auth = Token(auth_url, profile.domain_scope_token, domain_id=profile.domain.id)
        session = Session(
            auth=auth,
            original_ip=original_ip,
            verify=CONF.default.cafile,
            timeout=constants.DEFAULT_TIMEOUT,
        )
        access = session.auth.get_auth_ref(session)  # type: ignore
    except (KeystoneUnauthorized, KeystoneInternalServerError) as e:
        LOG.debug(f"Domain-scoped token not usable for policy evaluation: {str(e)}")
        return None
    context = UserContext(access)
    context["token"] = {"domain": {"id": profile.domain.id}}
    return context


def _authorize(
    service: str,
    enforcer: Any,
    rule: str,
    target: Dict[str, str],
    user_context: UserContext,
    domain_target: Optional[Dict[str, str]],
    domain_context: Optional[UserContext],
) -> bool:
    allowed = enforcer.authorize(rule, target, user_context)
    if not allowed and domain_context is not None and service in DOMAIN_SCOPE_SERVICES:
        allowed = enforcer.authorize(rule, domain_target, domain_context)
    return allowed


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
    request: Request,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Policies:
    original_ip = deps.get_original_ip(request)
    session = generate_session(profile, original_ip=original_ip)
    access = get_access(session)
    user_context = UserContext(access)
    try:
        system_scope_access = get_system_scope_access(
            profile.keystone_token,
            profile.region,
            original_ip=original_ip,
        )
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
    domain_context = _domain_user_context(profile, original_ip=original_ip)
    domain_target = _generate_domain_target(profile) if domain_context else None

    results: List = []
    services = constants.SUPPORTED_SERVICE_EPS.keys()
    for service in services:
        try:
            enforcer = ENFORCER[service]
            result = [
                {
                    "rule": f"{service}:{rule}",
                    "allowed": _authorize(
                        service,
                        enforcer,
                        rule,
                        target,
                        user_context,
                        domain_target,
                        domain_context,
                    ),
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
    request: Request,
    policy_rules: schemas.PoliciesRules,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.Policies:
    original_ip = deps.get_original_ip(request)
    session = generate_session(profile, original_ip=original_ip)
    access = get_access(session)
    user_context = UserContext(access)
    try:
        system_scope_access = get_system_scope_access(
            profile.keystone_token,
            profile.region,
            original_ip=original_ip,
        )
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
    domain_context = _domain_user_context(profile, original_ip=original_ip)
    domain_target = None
    if domain_context:
        domain_target = _generate_domain_target(profile)
        domain_target.update(policy_rules.target if policy_rules.target else {})
    try:
        result: List = []
        for policy_rule in policy_rules.rules:
            service = policy_rule.split(":", 1)[0]
            rule = policy_rule.split(":", 1)[1]
            enforcer = ENFORCER[service]
            result.append(
                {
                    "rule": policy_rule,
                    "allowed": _authorize(
                        service,
                        enforcer,
                        rule,
                        target,
                        user_context,
                        domain_target,
                        domain_context,
                    ),
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return schemas.Policies(**{"policies": result})
