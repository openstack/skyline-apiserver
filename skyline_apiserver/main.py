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

import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import jose
from fastapi import FastAPI, Request, Response, status
from starlette.middleware.cors import CORSMiddleware

from skyline_apiserver.api.v1 import api_router
from skyline_apiserver.config import CONF, configure
from skyline_apiserver.context import RequestContext
from skyline_apiserver.core.security import generate_profile_by_token, parse_access_token
from skyline_apiserver.db import api as db_api, setup as db_setup
from skyline_apiserver.log import LOG, setup as log_setup
from skyline_apiserver.policy import setup as policies_setup
from skyline_apiserver.types import constants

PROJECT_NAME = "Skyline API"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure("skyline")
    log_setup(
        Path(CONF.default.log_dir).joinpath(CONF.default.log_file),
        debug=CONF.default.debug,
    )
    policies_setup()
    db_setup()

    # Set all CORS enabled origins
    if CONF.default.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in CONF.default.cors_allow_origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    LOG.debug("Skyline API server start")
    yield
    LOG.debug("Skyline API server stop")


app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{constants.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)


@app.middleware("http")
async def validate_token(request: Request, call_next):
    url_path = request.url.path
    LOG.debug(f"Request path: {url_path}")

    # Skip authentication for login and static endpoints
    ignore_urls = [
        f"{constants.API_PREFIX}/login",
        f"{constants.API_PREFIX}/websso",
        "/static",
        "/docs",
        f"{constants.API_PREFIX}/openapi.json",
        "/favicon.ico",
        f"{constants.API_PREFIX}/sso",
        f"{constants.API_PREFIX}/contrib/keystone_endpoints",
        f"{constants.API_PREFIX}/contrib/domains",
        f"{constants.API_PREFIX}/contrib/regions",
    ]

    for ignore_url in ignore_urls:
        if url_path.startswith(ignore_url):
            return await call_next(request)

    if url_path.startswith(constants.API_PREFIX):
        # Get token from cookie
        token = request.cookies.get(CONF.default.session_name)
        if not token:
            return Response(
                content="Unauthorized: Token not found", status_code=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # Purge revoked tokens
            db_api.purge_revoked_token()

            # Parse and validate token
            parsed_token = parse_access_token(token)
            is_revoked = db_api.check_token(parsed_token.uuid)
            if is_revoked:
                return Response(
                    content="Unauthorized: Token revoked",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            # Generate profile from token
            profile = generate_profile_by_token(parsed_token)

            # Create RequestContext from profile
            request.state.context = RequestContext(
                user_id=profile.user.id,
                project_id=profile.project.id,
                project_name=profile.project.name,
                user_domain_id=profile.user.domain.id,
                project_domain_id=profile.project.domain.id,
                roles=[role.name for role in profile.roles],
                auth_token=profile.keystone_token,
            )

            # Store profile in request state for backward compatibility
            request.state.profile = profile

            # Check if token needs renewal
            if 0 < profile.exp - time.time() < CONF.default.access_token_renew:
                profile.exp = int(time.time()) + CONF.default.access_token_expire
                # Note: We can't set cookies in middleware, so we'll handle this in the response
                request.state.token_needs_renewal = True
                request.state.new_token = profile.toJWTPayload()
                request.state.new_exp = str(profile.exp)

        except jose.exceptions.ExpiredSignatureError as e:
            return Response(
                content=f"Unauthorized: Token expired - {str(e)}",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                content=f"Unauthorized: {str(e)}", status_code=status.HTTP_401_UNAUTHORIZED
            )

    response = await call_next(request)

    # Handle token renewal in response
    if hasattr(request.state, "token_needs_renewal") and request.state.token_needs_renewal:
        response.set_cookie(CONF.default.session_name, request.state.new_token, secure = True, httponly=True)
        response.set_cookie(constants.TIME_EXPIRED_KEY, request.state.new_exp)

    return response


app.include_router(api_router, prefix=constants.API_PREFIX)
