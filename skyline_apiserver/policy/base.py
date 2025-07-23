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

from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Dict, Iterator, List, Union

import attr
from immutables import Map
from keystoneauth1.access.access import AccessInfoV3
from oslo_policy import _cache_handler, _checks, policy

from skyline_apiserver.config import CONF
from skyline_apiserver.log import LOG

from .manager.base import APIRule, Rule


class UserContext(MutableMapping):
    def __init__(
        self,
        access: AccessInfoV3,
    ):
        self._data: Dict[str, Any] = {}
        self.access = access
        self._data.setdefault("auth_token", getattr(access, "auth_token", None))
        self._data.setdefault("user_id", getattr(access, "user_id", None))
        self._data.setdefault("project_id", getattr(access, "project_id", None))
        self._data.setdefault("tenant_id", getattr(access, "project_id", None))
        self._data.setdefault("domain_id", getattr(access, "domain_id", None))
        self._data.setdefault("user_domain_id", getattr(access, "user_domain_id", None))
        self._data.setdefault("project_domain_id", getattr(access, "project_domain_id", None))
        self._data.setdefault("username", getattr(access, "username", None))
        self._data.setdefault("project_name", getattr(access, "project_name", None))
        self._data.setdefault("domain_name", getattr(access, "domain_name", None))
        self._data.setdefault("user_domain_name", getattr(access, "user_domain_name", None))
        self._data.setdefault("project_domain_name", getattr(access, "project_domain_name", None))
        self._data.setdefault(
            "system_scope",
            "all"
            if getattr(access, "system") and getattr(access, "system", {}).get("all", False)
            else "",
        )
        self._data.setdefault("role_ids", getattr(access, "role_ids", []))
        self._data.setdefault("roles", getattr(access, "role_names", []))

        is_admin = False
        for role in CONF.openstack.system_admin_roles:
            if role in self._data["roles"]:
                is_admin = True
                break

        self._data.setdefault("is_admin", is_admin)

        is_reader_admin = False
        for role in CONF.openstack.system_reader_roles:
            if role in self._data["roles"]:
                is_reader_admin = True
                break

        self._data.setdefault("is_reader_admin", is_reader_admin)

    def __getitem__(self, k: Any) -> Any:
        return self._data[k]

    def __setitem__(self, k: Any, v: Any) -> None:
        self._data[k] = v

    def __delitem__(self, k: Any) -> None:
        del self._data[k]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return self._data.__str__()

    def __repr__(self) -> str:
        return self._data.__repr__()


@attr.s(kw_only=True, repr=True, frozen=False, slots=True, auto_attribs=True)
class Enforcer:
    service: str = attr.ib(repr=True, init=True)
    rules: Map = attr.ib(factory=Map, repr=True, init=False)
    file_rules: Dict[str, Any] = attr.ib(default={}, repr=True, init=True)
    _file_cache: Dict[str, Any] = attr.ib(default={}, repr=True, init=True)

    def load_rules(self) -> None:
        path = Path(CONF.default.policy_file_path).joinpath(
            str(self.service + "_" + CONF.default.policy_file_suffix)
        )
        if path.exists():
            reloaded, data = _cache_handler.read_cached_file(
                self._file_cache, path, force_reload=False
            )
            if reloaded or not self.file_rules:
                self.file_rules = policy.Rules.load(data)
        else:
            self.file_rules = {}

    def register_rules(self, rules: List[Union[Rule, APIRule]]) -> None:
        rule_map = {}
        for rule in rules:
            if rule.name in rule_map:
                raise ValueError(f"Duplicate policy rule {rule.name}.")

            rule_map[rule.name] = rule.basic_check

        self.rules = Map(rule_map)

    def authorize(self, rule: str, target: Dict[str, Any], context: UserContext) -> bool:
        try:
            self.load_rules()
        except Exception:
            LOG.debug(f"Failed to load {self.service} rules.")

        do_check = self.file_rules.get(rule) or self.rules.get(rule)
        if do_check is None:
            LOG.debug(f"Policy {rule} not registered.")
            return False

        try:
            result = _checks._check(
                rule=do_check,
                target=target,
                creds=context,
                enforcer=self,
                current_rule=rule,
            )
        except Exception:
            result = False

        return result
