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

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Policy(BaseModel):
    rule: str = Field(..., description="Policy rule")
    allowed: bool = Field(..., description="Policy allowed")


class Policies(BaseModel):
    policies: List[Policy] = Field(..., description="Policies list")


class PoliciesRules(BaseModel):
    rules: List[str] = Field(..., description="Policies rules list")
    target: Optional[Dict[str, str]] = Field(None, description="Policies targets")
