# Copyright 2022 99cloud
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

from pydantic import BaseModel, Field


class PrometheusQueryResultBase(BaseModel):
    metric: Dict[str, str] = Field(..., description="Prometheus metric")
    value: List[Any] = Field(..., description="Prometheus metric value")


class PrometheusQueryDataBase(BaseModel):
    resultType: str = Field(..., description="Prometheus result type")


class PrometheusResponseBase(BaseModel):
    status: str = Field(..., description="Prometheus status")
    errorType: Optional[str] = Field(default=None, description="Prometheus error type")
    error: Optional[str] = Field(default=None, description="Prometheus error")
    warnings: Optional[str] = Field(default=None, description="Prometheus warnings")


class PrometheusQueryResult(PrometheusQueryResultBase):
    """"""


class PrometheusQueryData(PrometheusQueryDataBase):
    result: List[PrometheusQueryResult] = Field(..., description="Prometheus query result")


class PrometheusQueryResponse(PrometheusResponseBase):
    data: Optional[PrometheusQueryData] = Field(default=None, description="Prometheus query data")


class PrometheusQueryRangeResult(PrometheusQueryResultBase):
    """"""


class PrometheusQueryRangeData(PrometheusQueryDataBase):
    result: List[PrometheusQueryRangeResult] = Field(
        ..., description="Prometheus query range result"
    )


class PrometheusQueryRangeResponse(PrometheusResponseBase):
    data: Optional[PrometheusQueryRangeData] = Field(
        default=None, description="Prometheus query range data"
    )
