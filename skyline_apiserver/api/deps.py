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

from typing import Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from skyline_apiserver import schemas


def getJWTPayload(request: Request) -> Optional[str]:
    """Get JWT payload from request state (set by middleware)."""
    if hasattr(request.state, "profile"):
        return request.state.profile.toJWTPayload()
    return None


def get_profile(request: Request) -> schemas.Profile:
    """Get profile from request state (set by middleware)."""
    if not hasattr(request.state, "profile"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Profile not found in request state",
        )
    return request.state.profile


def get_profile_update_jwt(request: Request, response: Response) -> schemas.Profile:
    """Get profile from request state and handle token renewal."""
    profile = get_profile(request)

    # Token renewal is handled in the middleware
    # This function is kept for backward compatibility
    return profile
