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

from typing import Any, List, Optional, Sequence

from oslo_policy import _parser
from oslo_policy.policy import DocumentedRuleDefault, RuleDefault
from pydantic import BaseModel

from skyline_apiserver import schemas


class Rule:
    def __init__(
        self,
        name: str,
        check_str: str,
        description: str,
        basic_check_str: str = "",
    ) -> None:
        self.name = name
        self.check_str = check_str
        self.check = _parser.parse_rule(self.check_str)
        self.description = description or "No description"
        self.basic_check_str = basic_check_str or self.check_str
        self.basic_check = _parser.parse_rule(self.basic_check_str)

    def __str__(self) -> str:
        return f'"{self.name}": "{self.check_str}"'

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name='{self.name}', check_str='{self.check_str}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rule) and isinstance(self, Rule):
            return (self.name, self.check_str) == (other.name, other.check_str)
        return False

    def format_into_yaml(self) -> str:
        desc = f"# {self.description}\n"
        text = f"{desc}{str(self)}\n\n"

        return text

    @classmethod
    def from_oslo(cls, rule: RuleDefault):
        description = rule.description or ""
        description = description.replace("\n", "\n#")
        return cls(name=rule.name, check_str=rule.check_str, description=description)


class APIRule(Rule):
    def __init__(
        self,
        name: str,
        check_str: str,
        description: str,
        scope_types: List[str],
        operations: Optional[Sequence[Any]] = None,
        basic_check_str: str = "",
    ) -> None:
        super().__init__(name, check_str, description, basic_check_str)

        schemas.ScopeTypesSchema.parse_obj(scope_types)
        self.scope_types = scope_types

        # for Pydantic 2.x, automatically convert Operation instances to dict
        if operations and isinstance(operations[0], BaseModel):
            operations = [op.model_dump() for op in operations]
        self.operations: schemas.OperationsSchema = schemas.OperationsSchema.model_validate(
            operations
        )

    def format_into_yaml(self) -> str:
        op_list = [
            f"# {operation.method:8}{operation.path}\n" for operation in self.operations.root
        ]
        op = "".join(op_list)
        scope = f"# Intended scope(s): {self.scope_types}\n"

        desc = f"# {self.description}\n"
        text = f"{desc}{op}{scope}{str(self)}\n\n"

        return text

    def to_dict(self):
        return {
            "name": getattr(self, "name", None),
            "description": getattr(self, "description", None),
            "scope_types": getattr(self, "scope_types", None),
            "operations": self.operations.model_dump() if hasattr(self, "operations") else None,
        }

    def __repr__(self):
        return f"APIRule({self.to_dict()})"

    @classmethod
    def from_oslo(cls, rule: DocumentedRuleDefault):
        description = rule.description or ""
        description = description.replace("\n", "\n#")
        if isinstance(rule.scope_types, list):
            scope_types = [item for item in rule.scope_types]
        else:
            scope_types = ["project"]
        operations = []
        for operation in rule.operations:
            method = operation.get("method")
            if isinstance(method, list):
                for i in method:
                    operations.append(
                        schemas.Operation(method=i.upper(), path=operation.get("path", ""))
                    )
            elif isinstance(method, str):
                operations.append(
                    schemas.Operation(method=method.upper(), path=operation.get("path", "")),
                )
            else:
                operations.append(schemas.Operation(method="GET", path=operation.get("path", "")))
        return cls(
            name=rule.name,
            check_str=rule.check_str,
            description=description,
            scope_types=scope_types,
            operations=operations,
        )
