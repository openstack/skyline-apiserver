# Copyright 2026 OpenStack Skyline Authors
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

from skyline_apiserver.config.openstack import service_mapping
from skyline_apiserver.policy.manager import get_service_rules
from skyline_apiserver.types import constants

# Prefixes of the rule names generated from Zaqar's own oslo.policy rules.
UPSTREAM_PREFIXES = ("queues:", "messages:", "claims:", "subscription:")


class TestZaqarPolicy:
    def test_zaqar_registered_in_supported_service_eps(self) -> None:
        assert constants.SUPPORTED_SERVICE_EPS.get("zaqar") == ["zaqar"]

    def test_messaging_mapped_to_zaqar_in_service_mapping(self) -> None:
        assert service_mapping.default["messaging"] == "zaqar"

    def test_zaqar_rules_are_discovered(self) -> None:
        service_rules = get_service_rules()
        assert service_rules.get("zaqar"), "zaqar rules were not discovered"

    def test_zaqar_uses_upstream_rule_names(self) -> None:
        names = [rule.name for rule in get_service_rules()["zaqar"]]
        # The UI relies on these resource prefixes coming from Zaqar itself.
        for prefix in UPSTREAM_PREFIXES:
            assert any(name.startswith(prefix) for name in names)
