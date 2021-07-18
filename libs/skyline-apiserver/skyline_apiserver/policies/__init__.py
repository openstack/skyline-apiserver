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

from skyline_policy_manager.policies import get_service_rules
from skyline_policy_manager.policies.base import APIRule

from .base import Enforcer, UserContext

ENFORCER = Enforcer()


def setup() -> None:
    service_rules = get_service_rules()
    all_api_rules = []
    for rules in service_rules.values():
        api_rules = [rule for rule in rules if isinstance(rule, APIRule)]
        all_api_rules.extend(api_rules)

    ENFORCER.register_rules(all_api_rules)


__all__ = (
    "ENFORCER",
    "UserContext",
    "setup",
)
