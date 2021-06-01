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
from typing import Any, Dict

import httpx
from fastapi import HTTPException, status
from httpx import Response, codes


async def _http_request(
    method: types.FunctionType = httpx.AsyncClient.get,
    **kwargs,
) -> Response:
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await method(
                client,
                **kwargs,
            )
            return response
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


async def assert_http_request(
    method: types.FunctionType,
    expectedStatus: str = codes.OK,
    **kwargs,
) -> Response:
    response = await _http_request(method, **kwargs)
    if response.status_code != expectedStatus:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )
    return response


async def get_assert_200(
    url: str,
    cookies: Dict[str, Any] = None,
    headers: Dict[str, Any] = None,
    params: Dict[str, Any] = None,
) -> Response:
    return await assert_http_request(
        method=httpx.AsyncClient.get,
        expectedStatus=codes.OK,
        url=url,
        cookies=cookies,
        headers=headers,
        params=params,
    )


async def delete_assert_200(url, cookies: Dict[str, Any] = None) -> Response:
    return await assert_http_request(
        method=httpx.AsyncClient.delete,
        expectedStatus=codes.OK,
        url=url,
        cookies=cookies,
    )


async def post_assert_201(url: str, json: Dict[str, Any], cookies: Dict[str, Any]) -> Response:
    return await assert_http_request(
        method=httpx.AsyncClient.post,
        expectedStatus=codes.CREATED,
        url=url,
        json=json,
        cookies=cookies,
    )


async def put_assert_200(url: str, json: Dict[str, Any], cookies: Dict[str, Any]) -> Response:
    return await assert_http_request(
        method=httpx.AsyncClient.put,
        expectedStatus=codes.OK,
        url=url,
        json=json,
        cookies=cookies,
    )
