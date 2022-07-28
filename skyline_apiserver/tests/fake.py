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

import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Union

from mimesis import Generic
from pydantic import StrictBool, StrictInt, StrictStr

FAKER = Generic()

FAKE_NS = "skyline_apiserver.tests.mock_ns"

FAKE_SERVICE_EPS = {
    "cinder": ["cinder"],
    "glance": ["glance"],
    "heat": ["heat"],
    "keystone": ["keystone"],
    "neutron": ["neutron"],
    "nova": ["nova"],
}

current_module = sys.modules[__name__]

for ep_names in FAKE_SERVICE_EPS.values():
    for ep_name in ep_names:
        setattr(current_module, f"{ep_name}_list_rules", lambda: [])


@dataclass
class FakeOptData:
    name: str = field(default_factory=lambda: "_".join(FAKER.text.words()))
    description: str = field(default_factory=lambda: str(FAKER.text.text()))
    schema: Any = field(
        default_factory=lambda: FAKER.random.choice(
            [StrictBool, StrictInt, StrictStr, List, Dict],
        ),
    )
    default: Any = None
    deprecated: bool = False


@dataclass
class FakeOperation:
    method: Union[str, Any] = field(
        default_factory=lambda: FAKER.choice(["GET", "POST", "PUT", "PATCH", "DELETE"]),
    )
    path: Union[str, Any] = field(
        default_factory=lambda: FAKER.choice(["/resources", "/resources/{resource_id}"]),
    )


@dataclass
class FakeDocumentedRuleData:
    name: str = field(default_factory=lambda: ":".join(FAKER.text.words()))
    description: str = field(default_factory=lambda: FAKER.text.text())
    check_str: str = field(
        default_factory=lambda: f'role:{FAKER.choice(["admin", "member", "reader"])}',
    )
    scope_types: Union[List[str], Any] = field(
        default_factory=lambda: FAKER.choice(
            ["system", "domain", "project"],
            length=FAKER.numbers.integer_number(1, 3),
            unique=True,
        ),
    )
    operations: List[Dict[str, str]] = field(
        default_factory=lambda: [
            asdict(FakeOperation()) for _ in range(FAKER.numbers.integer_number(1, 5))
        ],
    )


@dataclass
class FakeRuleData:
    name: str = field(default_factory=lambda: ":".join(FAKER.text.words()))
    description: str = field(default_factory=lambda: FAKER.text.text())
    check_str: str = field(
        default_factory=lambda: f'role:{FAKER.choice(["admin", "member", "reader"])}',
    )
    scope_types: Union[List[str], Any] = field(
        default_factory=lambda: FAKER.choice(
            ["system", "domain", "project"],
            length=FAKER.numbers.integer_number(1, 3),
            unique=True,
        ),
    )
