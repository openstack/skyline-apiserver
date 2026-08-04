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

from pathlib import PurePath
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends, Form, Header
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from keystoneauth1 import exceptions as ks_exceptions
from keystoneauth1.identity import v3 as v3_auth
from keystoneauth1.identity.v3 import Password, Token
from keystoneauth1.session import Session
from keystoneclient.client import Client as KeystoneClient
from starlette.requests import Request
from starlette.responses import Response

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.client import utils
from skyline_apiserver.client.openstack.keystone import get_token_data, get_user, revoke_token
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

TOTP_ERROR_INVALID = "invalid_totp"
TOTP_ERROR_RECEIPT_EXPIRED = "receipt_expired"
TOTP_ERROR_AUTH_FAILED = "authentication_failed"


def _requires_totp_step(exc: ks_exceptions.MissingAuthMethods) -> bool:
    if not exc.receipt:
        return False
    for rule in exc.required_auth_methods or []:
        if "totp" in rule and "password" in rule:
            return True
    return False


def _totp_required_detail(receipt: str) -> Dict[str, Any]:
    return schemas.TOTPRequiredDetail(totp_required=True, receipt=receipt).model_dump()


def _raise_for_missing_auth_methods(exc: ks_exceptions.MissingAuthMethods) -> None:
    if _requires_totp_step(exc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_totp_required_detail(exc.receipt),
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="An error occurred authenticating. Please try again later.",
    )


def _is_receipt_auth_error(exc: Exception) -> bool:
    if isinstance(exc, ks_exceptions.MissingAuthMethods):
        return not exc.receipt

    if isinstance(exc, ks_exceptions.http.HttpError):
        response = exc.response
        if response is None:
            return False
        receipt_header = response.headers.get("Openstack-Auth-Receipt")
        try:
            body = response.json()
        except Exception:
            body = {}
        error = body.get("error") if isinstance(body, dict) else {}
        if isinstance(error, dict):
            code = str(error.get("code", "")).lower()
            message = str(error.get("message", "")).lower()
            if "receipt" in code and "expir" in code:
                return True
            if "receipt" in message and "expir" in message:
                return True
        if isinstance(body, dict) and "required_auth_methods" in body and not receipt_header:
            return True
    return False


def _raise_for_totp_auth_error(exc: Exception, username: str, domain: str) -> None:
    if _is_receipt_auth_error(exc):
        LOG.warning(
            "TOTP receipt expired or invalid for user %s in domain %s: %s",
            username,
            domain,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TOTP_ERROR_RECEIPT_EXPIRED,
        )

    if isinstance(exc, ks_exceptions.http.Unauthorized):
        LOG.warning(
            "TOTP authentication failed for user %s in domain %s: %s",
            username,
            domain,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TOTP_ERROR_INVALID,
        )

    LOG.exception(
        "Unexpected error during TOTP authentication for user %s in domain %s",
        username,
        domain,
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=TOTP_ERROR_AUTH_FAILED,
    )


def _build_profile_from_unscope(
    unscope_token: str,
    region: str,
    x_openstack_request_id: str,
    project_scope: List[Any],
    default_project_id: Optional[str],
    original_ip: Optional[str] = None,
) -> schemas.Profile:
    if default_project_id not in [i.id for i in project_scope]:
        default_project_id = None
    project_scope_token = get_project_scope_token(
        keystone_token=unscope_token,
        region=region,
        project_id=default_project_id or project_scope[0].id,
        original_ip=original_ip,
    )
    profile = generate_profile(
        keystone_token=project_scope_token,
        region=region,
        original_ip=original_ip,
    )
    return _patch_profile(profile, x_openstack_request_id, original_ip=original_ip)


def _set_login_cookies(response: Response, profile: schemas.Profile) -> None:
    response.set_cookie(CONF.default.session_name, profile.toJWTPayload())
    response.set_cookie(constants.TIME_EXPIRED_KEY, str(profile.exp))


def _finish_login(
    unscope_token: str,
    region: str,
    response: Response,
    x_openstack_request_id: str,
    project_enabled: bool = True,
    original_ip: Optional[str] = None,
) -> schemas.Profile:
    project_scope, _, default_project_id = _get_projects_and_unscope_token(
        region=region,
        token=unscope_token,
        project_enabled=project_enabled,
        original_ip=original_ip,
    )
    profile = _build_profile_from_unscope(
        unscope_token=unscope_token,
        region=region,
        x_openstack_request_id=x_openstack_request_id,
        project_scope=project_scope,
        default_project_id=default_project_id,
        original_ip=original_ip,
    )
    _set_login_cookies(response, profile)
    return profile


def _get_totp_session(
    region: str,
    domain: str,
    username: str,
    passcode: str,
    receipt: str,
    original_ip: Optional[str] = None,
) -> Session:
    auth_url = utils.get_endpoint(
        region=region,
        service="identity",
        session=get_system_session(original_ip=original_ip),
    )
    totp_auth = v3_auth.TOTP(
        auth_url=auth_url,
        username=username,
        passcode=passcode,
        user_domain_name=domain,
    )
    totp_auth.add_method(v3_auth.ReceiptMethod(receipt=receipt))
    return Session(
        auth=totp_auth,
        original_ip=original_ip,
        verify=CONF.default.cafile,
        timeout=constants.DEFAULT_TIMEOUT,
    )


def _get_default_project_id(
    session: Session,
    region: str,
    user_id: Optional[str] = None,
    original_ip: Optional[str] = None,
) -> Union[str, None]:
    system_session = get_system_session(original_ip=original_ip)
    if not user_id:
        token = session.get_token()
        token_data = get_token_data(token, region, system_session)  # type: ignore
        _user_id = token_data["token"]["user"]["id"]
    else:
        _user_id = user_id
    user = get_user(_user_id, region, system_session)
    return getattr(user, "default_project_id", None)


def _get_projects_and_unscope_token(
    region: str,
    domain: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    project_enabled: bool = False,
    original_ip: Optional[str] = None,
) -> Tuple[List[Any], str, Union[str, None]]:
    auth_url = utils.get_endpoint(
        region=region,
        service="identity",
        session=get_system_session(original_ip=original_ip),
    )

    if token:
        unscope_auth = Token(
            auth_url=auth_url,
            token=token,
            reauthenticate=False,
        )
    else:
        unscope_auth = Password(  # type: ignore
            auth_url=auth_url,
            user_domain_name=domain,
            username=username,
            password=password,  # type: ignore
            reauthenticate=False,
        )

    session = Session(
        auth=unscope_auth,
        original_ip=original_ip,
        verify=CONF.default.cafile,
        timeout=constants.DEFAULT_TIMEOUT,
    )

    if not token:
        try:
            session.get_token()
        except ks_exceptions.MissingAuthMethods as exc:
            _raise_for_missing_auth_methods(exc)

    unscope_client = KeystoneClient(
        session=session,
        endpoint=auth_url,
        interface=CONF.openstack.interface_type,
    )

    project_scope = unscope_client.auth.projects()
    unscope_token = token if token else session.get_token()

    if project_enabled:
        project_scope = [scope for scope in project_scope if scope.enabled]

    if not project_scope:
        raise Exception("You are not authorized for any projects or domains.")

    default_project_id = _get_default_project_id(
        session,
        region,
        original_ip=original_ip,
    )

    return project_scope, unscope_token, default_project_id  # type: ignore


def _get_user_regions(
    profile: schemas.Profile,
    original_ip: Optional[str] = None,
) -> List[str]:
    try:
        user_session = generate_session(profile, original_ip=original_ip)
        access = utils.get_access(session=user_session)
        catalogs: Dict[str, Any] = (
            access.service_catalog.get_endpoints(interface=CONF.openstack.interface_type) or {}
        )
        regions = list(set(j["region_id"] for i in catalogs for j in (catalogs[i] or [])))
        return sorted(regions)
    except Exception:
        return []


def _patch_profile(
    profile: schemas.Profile,
    global_request_id: str,
    original_ip: Optional[str] = None,
) -> schemas.Profile:
    try:
        profile.regions = _get_user_regions(profile, original_ip=original_ip)
        profile.endpoints = get_endpoints(
            region=profile.region,
            original_ip=original_ip,
        )

        projects = get_projects(
            global_request_id=global_request_id,
            region=profile.region,
            user=profile.user.id,
            original_ip=original_ip,
        )

        if not projects:
            projects, _, default_project_id = _get_projects_and_unscope_token(
                region=profile.region,
                token=profile.keystone_token,
                original_ip=original_ip,
            )
        else:
            default_project_id = _get_default_project_id(
                get_system_session(original_ip=original_ip),
                profile.region,
                user_id=profile.user.id,
                original_ip=original_ip,
            )

        profile.projects = {
            i.id: {
                "name": i.name,
                "enabled": i.enabled,
                "domain_id": i.domain_id,
                "domain_name": getattr(getattr(i, "domain", None), "name", None),
                "description": i.description,
            }
            for i in projects
        }

        profile.default_project_id = default_project_id

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
        401: {"model": schemas.LoginUnauthorizedMessage},
    },
    response_model=schemas.Profile,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def login(
    request: Request,
    response: Response,
    credential: schemas.Credential,
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.Profile:
    region = CONF.openstack.default_region
    domain = credential.domain or CONF.openstack.user_default_domain
    original_ip = deps.get_original_ip(request)
    try:
        (project_scope, unscope_token, default_project_id,) = _get_projects_and_unscope_token(
            region=region,
            domain=domain,
            username=credential.username,
            password=credential.password,
            project_enabled=True,
            original_ip=original_ip,
        )
        profile = _build_profile_from_unscope(
            unscope_token=unscope_token,
            region=region,
            x_openstack_request_id=x_openstack_request_id,
            project_scope=project_scope,
            default_project_id=default_project_id,
            original_ip=original_ip,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    else:
        _set_login_cookies(response, profile)
        return profile


@router.post(
    "/login/totp",
    description="Complete login with TOTP passcode after password auth.",
    responses={
        200: {"model": schemas.Profile},
        401: {"model": schemas.UnauthorizedMessage},
    },
    response_model=schemas.Profile,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def login_totp(
    request: Request,
    response: Response,
    credential: schemas.TOTPCredential,
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.Profile:
    region = credential.region or CONF.openstack.default_region
    domain = credential.domain or CONF.openstack.user_default_domain
    original_ip = deps.get_original_ip(request)

    try:
        totp_session = _get_totp_session(
            region=region,
            domain=domain,
            username=credential.username,
            passcode=credential.passcode,
            receipt=credential.receipt,
            original_ip=original_ip,
        )
        unscope_token = totp_session.get_token()
        if not unscope_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=TOTP_ERROR_AUTH_FAILED,
            )
        return _finish_login(
            unscope_token=unscope_token,
            region=region,
            response=response,
            x_openstack_request_id=x_openstack_request_id,
            project_enabled=True,
            original_ip=original_ip,
        )
    except HTTPException:
        raise
    except Exception as exc:
        _raise_for_totp_auth_error(exc, credential.username, domain)


@router.get(
    "/config",
    description="Get public configuration",
    responses={
        200: {"model": schemas.Config},
    },
    response_model=schemas.Config,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def get_config(request: Request) -> schemas.Config:
    return schemas.Config(
        default_domain=CONF.openstack.user_default_domain,
        default_region=CONF.openstack.default_region,
    )


@router.get(
    "/sso",
    description="SSO configuration.",
    responses={
        200: {"model": schemas.SSO},
    },
    response_model=schemas.SSO,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def get_sso(request: Request) -> schemas.SSO:
    sso: Dict = {
        "enable_sso": False,
        "protocols": [],
    }
    if CONF.openstack.sso_enabled:
        protocols: List = []

        ks_url = CONF.openstack.keystone_url.rstrip("/")
        url_scheme = "https" if CONF.default.ssl_enabled else "http"
        port = f":{request.url.port}" if request.url.port else ""
        base_url = f"{url_scheme}://{request.url.hostname}{port}"
        base_path = str(PurePath("/").joinpath(CONF.openstack.nginx_prefix, "skyline"))

        for protocol in CONF.openstack.sso_protocols:

            url = (
                f"{ks_url}/auth/OS-FEDERATION/websso/{protocol}"
                f"?origin={base_url}{base_path}{constants.API_PREFIX}/websso"
            )

            protocols.append(
                {
                    "protocol": protocol,
                    "url": url,
                }
            )

        sso = {
            "enable_sso": CONF.openstack.sso_enabled,
            "protocols": protocols,
        }

    return schemas.SSO(**sso)


@router.post(
    "/websso",
    description="Websso",
    responses={
        302: {"description": "Redirect to SSO provider"},
        401: {"model": schemas.common.UnauthorizedMessage},
    },
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    response_description="Redirect",
)
def websso(
    request: Request,
    token: str = Form(...),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> RedirectResponse:
    original_ip = deps.get_original_ip(request)
    try:
        project_scope, _, default_project_id = _get_projects_and_unscope_token(
            region=CONF.openstack.sso_region,
            token=token,
            project_enabled=True,
            original_ip=original_ip,
        )

        if default_project_id not in [i.id for i in project_scope]:
            default_project_id = None
        project_scope_token = get_project_scope_token(
            keystone_token=token,
            region=CONF.openstack.sso_region,
            project_id=default_project_id or project_scope[0].id,
            original_ip=original_ip,
        )

        profile = generate_profile(
            keystone_token=project_scope_token,
            region=CONF.openstack.sso_region,
            original_ip=original_ip,
        )

        profile = _patch_profile(
            profile,
            x_openstack_request_id,
            original_ip=original_ip,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    else:
        response = RedirectResponse(url="/base/overview", status_code=status.HTTP_302_FOUND)
        response.set_cookie(CONF.default.session_name, profile.toJWTPayload())
        response.set_cookie(constants.TIME_EXPIRED_KEY, str(profile.exp))
        return response


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
def get_profile(
    request: Request,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.Profile:
    return _patch_profile(
        profile,
        x_openstack_request_id,
        original_ip=deps.get_original_ip(request),
    )


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
def logout(
    response: Response,
    request: Request,
    payload: str = Depends(deps.getJWTPayload),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.Message:
    if payload:
        try:
            original_ip = deps.get_original_ip(request)
            token = parse_access_token(payload)
            profile = generate_profile_by_token(token, original_ip=original_ip)
            session = generate_session(profile, original_ip=original_ip)
            revoke_token(profile, session, x_openstack_request_id, token.keystone_token)
            db_api.revoke_token(profile.uuid, profile.exp)
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
def switch_project(
    project_id: str,
    request: Request,
    response: Response,
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.Profile:
    profile = deps.get_profile(request)
    original_ip = deps.get_original_ip(request)
    region = profile.region
    if profile.projects and project_id not in profile.projects:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Project not accessible",
        )
    try:
        project_scope_token = get_project_scope_token(
            keystone_token=profile.keystone_token,
            region=region,
            project_id=project_id,
            original_ip=original_ip,
        )
        new_profile = generate_profile(
            keystone_token=project_scope_token,
            region=region,
            original_ip=original_ip,
        )
        new_profile = _patch_profile(
            new_profile,
            x_openstack_request_id,
            original_ip=original_ip,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    else:
        response.set_cookie(CONF.default.session_name, new_profile.toJWTPayload())
        response.set_cookie(constants.TIME_EXPIRED_KEY, str(new_profile.exp))
        return new_profile


@router.post(
    "/switch_region/{region}",
    description="Switch region.",
    responses={
        200: {"model": schemas.Profile},
        401: {"model": schemas.UnauthorizedMessage},
    },
    response_model=schemas.Profile,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def switch_region(
    region: str,
    request: Request,
    response: Response,
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
) -> schemas.Profile:
    profile = deps.get_profile(request)
    original_ip = deps.get_original_ip(request)
    allowed_regions = profile.regions or _get_user_regions(
        profile,
        original_ip=original_ip,
    )
    if region not in allowed_regions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Region not accessible",
        )
    try:
        new_profile = generate_profile(
            keystone_token=profile.keystone_token,
            region=region,
            original_ip=original_ip,
        )
        new_profile = _patch_profile(
            new_profile,
            x_openstack_request_id,
            original_ip=original_ip,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    else:
        response.set_cookie(CONF.default.session_name, new_profile.toJWTPayload())
        response.set_cookie(constants.TIME_EXPIRED_KEY, str(new_profile.exp))
        return new_profile
