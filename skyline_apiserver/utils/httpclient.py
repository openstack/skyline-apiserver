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

import types
from typing import Any, Dict, Optional

import httpx
from fastapi import status
from fastapi.exceptions import HTTPException
from httpx import Response, codes


def _http_request(
    method: types.FunctionType = httpx.Client.get,  # type: ignore
    **kwargs,
) -> Response:
    with httpx.Client(verify=False) as client:
        try:
            response = method(
                client,
                **kwargs,
            )
            return response
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


def assert_http_request(
    method: types.FunctionType,
    expectedStatus: codes = codes.OK,
    **kwargs,
) -> Response:
    response = _http_request(method, **kwargs)
    if response.status_code != expectedStatus:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )
    return response


def get_assert_200(
    url: str,
    cookies: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Response:
    return assert_http_request(
        method=httpx.Client.get,  # type: ignore
        expectedStatus=codes.OK,
        url=url,
        cookies=cookies,
        headers=headers,
        params=params,
    )


def delete_assert_200(url, cookies: Optional[Dict[str, Any]] = None) -> Response:
    return assert_http_request(
        method=httpx.Client.delete,  # type: ignore
        expectedStatus=codes.OK,
        url=url,
        cookies=cookies,
    )


def post_assert_201(url: str, json: Dict[str, Any], cookies: Dict[str, Any]) -> Response:
    return assert_http_request(
        method=httpx.Client.post,  # type: ignore
        expectedStatus=codes.CREATED,
        url=url,
        json=json,
        cookies=cookies,
    )


def put_assert_200(url: str, json: Dict[str, Any], cookies: Dict[str, Any]) -> Response:
    return assert_http_request(
        method=httpx.Client.put,  # type: ignore
        expectedStatus=codes.OK,
        url=url,
        json=json,
        cookies=cookies,
    )
