from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from httpx import codes

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.config import CONF
from skyline_apiserver.types import constants
from skyline_apiserver.utils.httpclient import _http_request
from skyline_apiserver.utils.roles import is_system_admin_or_reader

router = APIRouter()


def get_prometheus_query_response(
    resp: dict,
    profile: schemas.Profile,
) -> schemas.PrometheusQueryResponse:
    ret = schemas.PrometheusQueryResponse(status=resp["status"])
    if "warnings" in resp:
        ret.warnings = resp["warnings"]
    if "errorType" in resp:
        ret.errorType = resp["errorType"]
    if "error" in resp:
        ret.error = resp["error"]
    if "data" in resp:
        result = [
            schemas.PrometheusQueryResult(metric=i["metric"], value=i["value"])
            for i in resp["data"]["result"]
        ]

        if not is_system_admin_or_reader(profile):
            result = [
                i
                for i in result
                if "project_id" in i.metric and i.metric["project_id"] == profile.project.id
            ]

        data = schemas.PrometheusQueryData(
            resultType=resp["data"]["resultType"],
            result=result,
        )
        ret.data = data

    return ret


def get_prometheus_query_range_response(
    resp: dict,
    profile: schemas.Profile,
) -> schemas.PrometheusQueryRangeResponse:
    ret = schemas.PrometheusQueryRangeResponse(status=resp["status"])
    if "warnings" in resp:
        ret.warnings = resp["warnings"]
    if "errorType" in resp:
        ret.errorType = resp["errorType"]
    if "error" in resp:
        ret.error = resp["error"]
    if "data" in resp:
        result = [
            schemas.PrometheusQueryRangeResult(metric=i["metric"], values=i["values"])
            for i in resp["data"]["result"]
        ]

        if not is_system_admin_or_reader(profile):
            result = [
                i
                for i in result
                if "project_id" in i.metric and i.metric["project_id"] == profile.project.id
            ]

        data = schemas.PrometheusQueryRangeData(
            resultType=resp["data"]["resultType"],
            result=result,
        )
        ret.data = data

    return ret


@router.get(
    "/query",
    description="Prometheus query API.",
    responses={
        200: {"model": schemas.PrometheusQueryResponse},
        401: {"model": schemas.UnauthorizedMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.PrometheusQueryResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
    response_model_exclude_none=True,
)
async def prometheus_query(
    query: str = None,
    time: str = None,
    timeout: str = None,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.PrometheusQueryResponse:
    kwargs = {}
    if query is not None:
        kwargs["query"] = query
    if time is not None:
        kwargs["time"] = time
    if timeout is not None:
        kwargs["timeout"] = timeout

    auth = None
    if CONF.default.prometheus_enable_basic_auth:
        auth = (
            CONF.default.prometheus_basic_auth_user,
            CONF.default.prometheus_basic_auth_password,
        )
    resp = await _http_request(
        url=CONF.default.prometheus_endpoint + constants.PROMETHEUS_QUERY_API,
        params=kwargs,
        auth=auth,
    )

    if resp.status_code != codes.OK:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return get_prometheus_query_response(resp.json(), profile)


@router.get(
    "/query_range",
    description="Prometheus query_range API.",
    responses={
        200: {"model": schemas.PrometheusQueryRangeResponse},
        401: {"model": schemas.UnauthorizedMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.PrometheusQueryRangeResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
    response_model_exclude_none=True,
)
async def prometheus_query_range(
    query: str = None,
    start: str = None,
    end: str = None,
    step: str = None,
    timeout: str = None,
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> schemas.PrometheusQueryRangeResponse:
    kwargs = {}
    if query is not None:
        kwargs["query"] = query
    if start is not None:
        kwargs["start"] = start
    if end is not None:
        kwargs["end"] = end
    if step is not None:
        kwargs["step"] = step
    if timeout is not None:
        kwargs["timeout"] = timeout

    auth = None
    if CONF.default.prometheus_enable_basic_auth:
        auth = (
            CONF.default.prometheus_basic_auth_user,
            CONF.default.prometheus_basic_auth_password,
        )
    resp = await _http_request(
        url=CONF.default.prometheus_endpoint + constants.PROMETHEUS_QUERY_RANGE_API,
        params=kwargs,
        auth=auth,
    )

    if resp.status_code != codes.OK:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return get_prometheus_query_range_response(resp.json(), profile)
