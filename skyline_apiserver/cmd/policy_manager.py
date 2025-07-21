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

import json
from importlib import metadata
from logging import StreamHandler
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Union

import click
from oslo_policy.policy import DocumentedRuleDefault, RuleDefault

from skyline_apiserver.log import LOG, setup as log_setup
from skyline_apiserver.policy.manager import get_service_rules
from skyline_apiserver.policy.manager.base import APIRule, Rule
from skyline_apiserver.types import constants

DEBUG = False

OSRules = Iterable[Union[DocumentedRuleDefault, RuleDefault]]


def load_list_rules_funcs(
    namespace: str,
    service_eps: Dict[str, List[str]],
) -> Dict[str, Callable[[], OSRules]]:
    eps = set(metadata.entry_points()[namespace])  # type: ignore [unused-ignore, call-overload]
    supported_eps = set()
    for ep_names in service_eps.values():
        supported_eps.update(ep_names)
    return {ep.name: ep.load() for ep in eps if ep.name in supported_eps}


def load_list_rules_func(namespace: str, service_ep: str) -> Union[None, Callable[[], OSRules]]:
    eps = set(metadata.entry_points()[namespace])  # type: ignore [unused-ignore, call-overload]
    for ep in eps:
        if ep.name == service_ep:
            return ep.load()

    return None


def comparison_rules(
    service: str,
    rule: Union[Rule, APIRule],
    os_rule: Union[Rule, APIRule],
) -> None:
    if isinstance(rule, APIRule) and isinstance(os_rule, APIRule):
        if rule.scope_types != os_rule.scope_types:
            LOG.error(
                f'\nService "{service}" rule "{rule.name}" scope_types is {rule.scope_types},\n'
                f"which is different from os_rule {os_rule.scope_types}.\n",
            )
        if rule.operations != os_rule.operations:
            LOG.error(
                f'\nService "{service}" rule "{rule.name}" operations is {rule.operations},\n'
                f"which is different from os_rule {os_rule.operations}.\n",
            )
    elif (isinstance(rule, Rule) and isinstance(os_rule, APIRule)) or (
        isinstance(rule, APIRule) and isinstance(os_rule, Rule)
    ):
        LOG.warning(
            f'\nService "{service}" rule "{rule.name}" is {rule.__class__},\n'
            f"which is different from os_rule {os_rule.__class__}.\n",
        )
    elif isinstance(rule, Rule) and isinstance(os_rule, Rule):
        pass
    else:
        LOG.error(f'\nService "{service}" rule "{rule.name}" is unknown class type.\n')


@click.group(name="skyline-policy-manager", help="Policy manager command line.")
@click.option("--debug", is_flag=True, default=False, help="Output more info.")
def policy_manager(debug: bool) -> None:
    global DEBUG
    DEBUG = debug
    log_setup(StreamHandler(), debug=DEBUG, colorize=True, level="INFO")


@click.command(help="Generate sample policy yaml file.")
@click.option("--dir", help='Directory of policy file.(default: "./tmp")', default="./tmp")
def generate_sample(dir: str) -> None:
    list_rules_funcs = load_list_rules_funcs(constants.POLICY_NS, constants.SUPPORTED_SERVICE_EPS)

    rule_map = {}
    for service, eps in constants.SUPPORTED_SERVICE_EPS.items():
        rules = []
        api_rules = []
        for ep in eps:
            ep_rules = list_rules_funcs.get(ep, lambda: [])()
            for rule in ep_rules:
                if isinstance(rule, DocumentedRuleDefault):
                    api_rules.append(APIRule.from_oslo(rule))
                elif isinstance(rule, RuleDefault):
                    rules.append(Rule.from_oslo(rule))

        rule_map[service] = {"rules": rules, "api_rules": api_rules}

    for service, item in rule_map.items():
        dir_path = Path(dir).joinpath(service)
        dir_path.mkdir(mode=0o755, parents=True, exist_ok=True)
        file_path = dir_path.joinpath("policy.yaml.sample")
        with open(file_path, "w") as f:
            f.write(f"{'#' * 20}\n# {service}\n{'#' * 20}\n\n")
            for rule in item.get("rules", []):
                f.writelines(rule.format_into_yaml())
            for rule in item.get("api_rules", []):
                f.writelines(rule.format_into_yaml())

    LOG.info("Generate sample policy successful")


@click.command(help="Generate policy yaml file.")
@click.option("--dir", help='Directory of policy file.(default: "./tmp")', default="./tmp")
@click.option("--desc", help="Description of the generated policy file.", default="")
def generate_conf(dir: str, desc: str) -> None:
    for service, rules in get_service_rules().items():
        dir_path = Path(dir).joinpath(service)
        dir_path.mkdir(mode=0o755, parents=True, exist_ok=True)
        file_path = dir_path.joinpath("policy.yaml")
        with open(file_path, "w") as f:
            f.write(f"{'#' * 20}\n# {service}\n{'#' * 20}\n")
            f.write(f"# {desc}\n\n")
            for rule in rules:
                rule_yaml = rule.format_into_yaml()
                f.writelines(rule_yaml)

    LOG.info("Generate policy successful")


@click.command(help="Generate service rule code.")
@click.argument("service")
def generate_rule(service: str) -> None:
    entry_points = constants.SUPPORTED_SERVICE_EPS.get(service, [])
    if not entry_points:
        LOG.error(f"Service {service} is not supported.")
        return

    rules = []
    api_rules = []
    for entry_point in entry_points:
        ep_rules_func = load_list_rules_func(constants.POLICY_NS, entry_point)
        if ep_rules_func is None:
            raise Exception(
                f"Not found entry point '{entry_point}' in oslo.policy.policies namespace.",
            )

        ep_rules = [item for item in ep_rules_func()]
        for rule in ep_rules:
            if isinstance(rule, DocumentedRuleDefault):
                api_rules.append(APIRule.from_oslo(rule))
            elif isinstance(rule, RuleDefault):
                rules.append(Rule.from_oslo(rule))

    header_str = """\
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

# flake8: noqa
# fmt: off

from . import base

list_rules = ("""
    print(header_str)

    rule_format_str = (
        "    base.Rule(\n"
        "        name={name},\n"
        "        check_str=({check_str}),\n"
        "        description={description},\n"
        "    ),"
    )
    for r in rules:
        print(
            rule_format_str.format(
                name=r.name,
                check_str=r.check_str,
                description=r.description,
            ),
        )

    apirule_format_str = (
        "    base.APIRule(\n"
        "        name={name},\n"
        "        check_str=({check_str}),\n"
        "        description={description},\n"
        "        scope_types={scope_types},\n"
        "        operations={operations},\n"
        "    ),"
    )
    for r in api_rules:
        print(
            apirule_format_str.format(
                name=r.name,
                check_str=r.check_str,
                description=r.description,
                scope_types=r.scope_types,
                operations=r.operations.model_dump(),
            ),
        )

    footer_str = """)

__all__ = ("list_rules",)\
"""
    print(footer_str)

    LOG.info("Generate service rule code successful")


@click.command(help="Validate all policy rules.")
@click.option("--diff", help="Output policy rule diff info.", is_flag=True, default=False)
def validate(diff: bool) -> None:
    list_rules_funcs = load_list_rules_funcs(constants.POLICY_NS, constants.SUPPORTED_SERVICE_EPS)

    os_rule_map = {}
    for service, eps in constants.SUPPORTED_SERVICE_EPS.items():
        service_rules = {}
        for ep in eps:
            ep_rules = list_rules_funcs.get(ep, lambda: [])()
            for rule in ep_rules:
                if rule.name in service_rules:
                    LOG.error(
                        f'Service "{service}" entry point "{ep}" has duplicate rules '
                        f'"{rule.name}", please check source code of {service} service.',
                    )
                if isinstance(rule, DocumentedRuleDefault):
                    service_rules[rule.name] = APIRule.from_oslo(rule)
                elif isinstance(rule, RuleDefault):
                    service_rules[rule.name] = Rule.from_oslo(rule)

            if not service_rules:
                LOG.warning(
                    f'Service "{service}" does not load any rules, please check whether the '
                    f"service package is installed (pip list).",
                )
        os_rule_map[service] = service_rules

    for service, rules in get_service_rules().items():
        for r in rules:
            os_rule = os_rule_map.get(service, {}).get(r.name)
            if os_rule is None:
                LOG.warning(
                    f'Rule "{r.name}" is not found in service "{service}", if it\'s deprecated, '
                    f"please remove.",
                )
            else:
                if diff:
                    LOG.info(
                        f'\nService "{service}" rule "{r.name}" compare results:\n'
                        f'{"OpenStack":10}: {os_rule.check_str}\n{"Custom":10}: {r.check_str}\n',
                    )
                comparison_rules(service, r, os_rule)

        unmanaged_rules = set(os_rule_map.get(service, {}).keys()) - set(
            [r.name for r in rules],
        )
        for r in unmanaged_rules:
            LOG.error(f"Rule {r} is unmanaged, please add it in '{service}' service")

    LOG.info("Validate policy completed")


def main() -> None:
    policy_manager.add_command(generate_sample)
    policy_manager.add_command(generate_conf)
    policy_manager.add_command(generate_rule)
    policy_manager.add_command(validate)
    policy_manager()
