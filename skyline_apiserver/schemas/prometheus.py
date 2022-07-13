from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PrometheusQueryResultBase(BaseModel):
    metric: Dict[str, str] = Field(..., description="Prometheus metric")
    value: List[Any] = Field(..., description="Prometheus metric value")


class PrometheusQueryDataBase(BaseModel):
    resultType: str = Field(..., description="Prometheus result type")


class PrometheusResponseBase(BaseModel):
    status: str = Field(..., description="Prometheus status")
    errorType: Optional[str] = Field(None, description="Prometheus error type")
    error: Optional[str] = Field(None, description="Prometheus error")
    warnings: Optional[str] = Field(None, description="Prometheus warnings")


class PrometheusQueryResult(PrometheusQueryResultBase):
    """"""


class PrometheusQueryData(PrometheusQueryDataBase):
    result: List[PrometheusQueryResult] = Field(..., description="Prometheus query result")


class PrometheusQueryResponse(PrometheusResponseBase):
    data: Optional[PrometheusQueryData] = Field(None, description="Prometheus query data")


class PrometheusQueryRangeResult(PrometheusQueryResultBase):
    """"""


class PrometheusQueryRangeData(PrometheusQueryDataBase):
    result: List[PrometheusQueryRangeResult] = Field(
        ..., description="Prometheus query range result"
    )


class PrometheusQueryRangeResponse(PrometheusResponseBase):
    data: Optional[PrometheusQueryRangeData] = Field(
        None, description="Prometheus query range data"
    )
