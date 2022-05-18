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

from dataclasses import asdict
from importlib import metadata
from importlib.metadata import EntryPoint
from pathlib import Path
from typing import Dict, List, Tuple, Union

import pytest
from click.testing import CliRunner
from oslo_policy.policy import DocumentedRuleDefault, RuleDefault

from skyline_apiserver.cmd.policy_manager import (
    generate_conf,
    generate_rule,
    generate_sample,
    policy_manager,
    validate,
)
from skyline_apiserver.policy.manager import get_service_rules
from skyline_apiserver.tests import fake
from skyline_apiserver.tests.fake import (
    FAKE_NS,
    FAKE_SERVICE_EPS,
    FAKER,
    FakeDocumentedRuleData,
    FakeRuleData,
)
from skyline_apiserver.tests.models import ArgumentData, TestData
from skyline_apiserver.types import constants


class TestPolicyManager:
    @pytest.fixture(autouse=True)
    def setup_entry_points(self, monkeypatch) -> None:
        eps = []
        for ep_names in FAKE_SERVICE_EPS.values():
            for ep_name in ep_names:
                fake_rules: List[Union[DocumentedRuleDefault, RuleDefault]]
                fake_rules = [
                    DocumentedRuleDefault(**asdict(FakeDocumentedRuleData()))
                    for _ in range(FAKER.numbers.integer_number(1, 10))
                ]
                fake_rules.extend(
                    [
                        RuleDefault(**asdict(FakeRuleData()))
                        for _ in range(FAKER.numbers.integer_number(1, 3))
                    ],
                )
                monkeypatch.setattr(fake, f"{ep_name}_list_rules", lambda: fake_rules)
                eps.append(
                    EntryPoint(
                        name=ep_name,
                        value=f"skyline_apiserver.tests.fake:{ep_name}_list_rules",
                        group=FAKE_NS,
                    ),
                )

        def entry_points() -> Dict[str, Tuple[EntryPoint, ...]]:
            return {FAKE_NS: tuple(eps)}

        monkeypatch.setattr(metadata, "entry_points", entry_points)
        monkeypatch.setattr(constants, "POLICY_NS", FAKE_NS)
        monkeypatch.setattr(constants, "SUPPORTED_SERVICE_EPS", FAKE_SERVICE_EPS)

    @pytest.fixture
    def runner(self) -> CliRunner:
        runner = CliRunner()
        return runner

    @pytest.mark.ddt(
        TestData(
            arguments=("dir_path",),
            argument_data_set=[
                ArgumentData(
                    id="str_dir_path",
                    values=(FAKER.text.word(),),
                ),
            ],
        ),
    )
    def test_generate_sample(self, runner: CliRunner, tmp_path: Path, dir_path: str) -> None:
        sample_dir = tmp_path.joinpath(dir_path)
        sample_dir.mkdir(parents=True, exist_ok=True)
        policy_manager.add_command(generate_sample)
        result = runner.invoke(
            policy_manager,
            ["generate-sample", "--dir", sample_dir.as_posix()],
        )
        assert result.exit_code == 0
        for service in FAKE_SERVICE_EPS:
            assert sample_dir.joinpath(service).exists()
            assert sample_dir.joinpath(service).joinpath("policy.yaml.sample").exists()

    @pytest.mark.ddt(
        TestData(
            arguments=("dir_path",),
            argument_data_set=[
                ArgumentData(
                    id="str_dir_path",
                    values=(FAKER.text.word(),),
                ),
            ],
        ),
        TestData(
            arguments=("description",),
            argument_data_set=[
                ArgumentData(
                    id="str_description",
                    values=(FAKER.text.text(),),
                ),
            ],
        ),
    )
    def test_generate_conf(
        self,
        runner: CliRunner,
        tmp_path: Path,
        dir_path: str,
        description: str,
    ) -> None:
        conf_dir = tmp_path.joinpath(dir_path)
        conf_dir.mkdir(parents=True, exist_ok=True)
        policy_manager.add_command(generate_conf)
        result = runner.invoke(
            policy_manager,
            ["generate-conf", "--dir", conf_dir.as_posix(), "--desc", description],
        )
        service_rules = get_service_rules()
        assert result.exit_code == 0
        for service in service_rules:
            assert conf_dir.joinpath(service).exists()
            assert conf_dir.joinpath(service).joinpath("policy.yaml").exists()
            assert description in conf_dir.joinpath(service).joinpath("policy.yaml").read_text()

    def test_generate_rule(self, runner: CliRunner) -> None:
        policy_manager.add_command(generate_rule)
        for ep_names in FAKE_SERVICE_EPS.values():
            for ep_name in ep_names:
                result = runner.invoke(policy_manager, ["generate-rule", ep_name])
                assert result.exit_code == 0

    def test_validate(self, runner: CliRunner) -> None:
        policy_manager.add_command(validate)
        result = runner.invoke(
            policy_manager,
            [
                "validate",
                "--diff",
            ],
        )
        assert result.exit_code == 0
