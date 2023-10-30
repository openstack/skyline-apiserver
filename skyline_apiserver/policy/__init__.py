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

from oslo_policy import _parser

from .base import Enforcer, UserContext
from .manager import get_service_rules

ENFORCER = {}


def setup() -> None:
    service_rules = get_service_rules()
    for service, rules in service_rules.items():
        api_rules = []
        for rule in rules:
            rule.check = _parser.parse_rule(rule.check_str)
            rule.basic_check = _parser.parse_rule(rule.basic_check_str)
            api_rules.append(rule)
            enforcer = Enforcer(service=service)
            enforcer.register_rules(api_rules)
            ENFORCER[service] = enforcer


__all__ = (
    "ENFORCER",
    "UserContext",
    "setup",
)
