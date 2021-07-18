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

from importlib import import_module
from os import path
from pkgutil import iter_modules
from typing import Dict, List, Union

from .base import APIRule, Rule

LIST_RULES_FUNC_NAME = "list_rules"


def get_service_rules() -> Dict[str, List[Union[Rule, APIRule]]]:
    service_rules = {}
    current_path = path.dirname(path.abspath(__file__))
    for m in iter_modules(path=[current_path]):
        if m.name in ["base"] or m.ispkg:
            continue

        module = import_module(f"{__package__}.{m.name}")
        service_rules[m.name] = getattr(module, LIST_RULES_FUNC_NAME, [])

    return service_rules


__all__ = ("get_service_rules",)
