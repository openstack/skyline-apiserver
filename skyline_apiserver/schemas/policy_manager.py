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

from enum import Enum
from typing import List

from pydantic import BaseModel, Field, RootModel


class ScopeType(str, Enum):
    system = "system"
    domain = "domain"
    project = "project"


class ScopeTypesSchema(RootModel[List[ScopeType]]):
    pass


class Method(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


class Operation(BaseModel):
    method: str
    path: str


class OperationSchema(BaseModel):
    method: Method = Field(..., description="Operation method")
    path: str = Field(..., description="Operation path")


class OperationsSchema(RootModel[List[OperationSchema]]):
    pass


__all__ = ("ScopeTypesSchema", "Operation", "OperationsSchema")
