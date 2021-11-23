from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PrometheusQueryResult(BaseModel):
    metric: Dict[str, str]
    value: List[Any]


class PrometheusQueryData(BaseModel):
    result: List[PrometheusQueryResult]
    resultType: str


class PrometheusQueryResponse(BaseModel):
    status: str
    data: Optional[PrometheusQueryData]
    errorType: Optional[str]
    error: Optional[str]
    warnings: Optional[str]


class PrometheusQueryRangeResult(BaseModel):
    metric: Dict[str, str]
    values: List[Any]


class PrometheusQueryRangeData(BaseModel):
    result: List[PrometheusQueryRangeResult]
    resultType: str


class PrometheusQueryRangeResponse(BaseModel):
    status: str
    data: Optional[PrometheusQueryRangeData]
    errorType: Optional[str]
    error: Optional[str]
    warnings: Optional[str]
