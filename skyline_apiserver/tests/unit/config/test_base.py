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
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type

import pytest
from _pytest.fixtures import SubRequest
from pydantic import StrictBool, StrictFloat, StrictInt, StrictStr, ValidationError
from pydantic.errors import PydanticSchemaGenerationError

from skyline_apiserver.config.base import Configuration, Group, Opt
from skyline_apiserver.tests.fake import FAKER, FakeOptData
from skyline_apiserver.tests.models import ArgumentData, TestData


class TestOpt:
    @pytest.mark.ddt(
        TestData(
            arguments=("opt_data", "expected_schema_type"),
            argument_data_set=[
                ArgumentData(
                    id="bool_opt",
                    values=(asdict(FakeOptData(schema=StrictBool)), "boolean"),
                ),
                ArgumentData(
                    id="int_opt",
                    values=(asdict(FakeOptData(schema=StrictInt)), "integer"),
                ),
                ArgumentData(
                    id="float_opt",
                    values=(asdict(FakeOptData(schema=StrictFloat)), "number"),
                ),
                ArgumentData(
                    id="str_opt",
                    values=(asdict(FakeOptData(schema=StrictStr)), "string"),
                ),
                ArgumentData(
                    id="list_opt",
                    values=(asdict(FakeOptData(schema=List[StrictStr])), "array"),
                ),
                ArgumentData(
                    id="dict_opt",
                    values=(asdict(FakeOptData(schema=Dict[StrictStr, StrictStr])), "object"),
                ),
            ],
        ),
    )
    def test_opt_init(self, opt_data: Dict[str, Any], expected_schema_type: str) -> None:
        opt = Opt(**opt_data)
        opt_value_schema = opt._schema_model.schema().get("properties", {}).get("value", {})
        assert opt_value_schema.get("type") == expected_schema_type

    @pytest.mark.ddt(
        TestData(
            arguments=("opt_data", "expected_exception"),
            argument_data_set=[
                ArgumentData(
                    id="missing_parameters",
                    values=({"name": FAKER.text.word()}, TypeError),
                ),
                ArgumentData(
                    id="unknown_schema",
                    values=(
                        {
                            "name": FAKER.text.word(),
                            "description": FAKER.text.word(),
                            "schema": RuntimeError,
                        },
                        PydanticSchemaGenerationError,
                    ),
                ),
            ],
        ),
    )
    def test_opt_init_error(
        self,
        opt_data: Dict[str, Any],
        expected_exception: Type[Exception],
    ) -> None:
        with pytest.raises(expected_exception):
            Opt(**opt_data)

    @pytest.mark.ddt(
        TestData(
            arguments=("opt_data",),
            argument_data_set=[
                ArgumentData(
                    id="when_has_default",
                    values=(
                        asdict(
                            FakeOptData(schema=Optional[StrictStr], default=FAKER.text.word()),
                        ),
                    ),
                ),
                ArgumentData(
                    id="when_no_default",
                    values=(asdict(FakeOptData(schema=Optional[StrictStr])),),
                ),
            ],
        ),
        TestData(
            arguments=("opt_value",),
            argument_data_set=[
                ArgumentData(id="load_value", values=(FAKER.text.word(),)),
                ArgumentData(id="load_none", values=(None,)),
            ],
        ),
    )
    def test_opt_load(self, opt_data: Dict[str, Any], opt_value: Optional[str]) -> None:
        opt = Opt(**opt_data)
        opt.load(opt_value)
        if opt_value is not None:
            expected_result = opt_value
        else:
            expected_result = opt.default
        assert opt.value == expected_result

    @pytest.mark.ddt(
        TestData(
            arguments=("opt_data",),
            argument_data_set=[
                ArgumentData(
                    id="deprecated_warning",
                    values=(asdict(FakeOptData(schema=Optional[StrictStr], deprecated=True)),),
                ),
            ],
        ),
    )
    def test_opt_deprecated(self, opt_data: Dict[str, Any]) -> None:
        opt = Opt(**opt_data)
        expected_warn = DeprecationWarning
        with pytest.warns(expected_warn):
            opt.load(None)

    @pytest.mark.ddt(
        TestData(
            arguments=("opt_data", "opt_value"),
            argument_data_set=[
                ArgumentData(
                    id="validation_error",
                    values=(
                        asdict(FakeOptData(schema=StrictStr)),
                        FAKER.numbers.integer_number(),
                    ),
                ),
            ],
        ),
    )
    def test_opt_schema_validation(self, opt_data: Dict[str, Any], opt_value: int) -> None:
        opt = Opt(**opt_data)
        expected_exception = ValidationError
        with pytest.raises(expected_exception):
            opt.load(opt_value)


class TestGroup:
    @pytest.fixture
    def group_opts(self, request: SubRequest) -> Sequence[Opt]:
        count: int = request.param
        opts = []
        for _ in range(count):
            opt_data = asdict(
                FakeOptData(schema=StrictStr, default=FAKER.text.word()),
            )
            opt = Opt(**opt_data)
            opt.load(None)
            opts.append(opt)
        return opts

    @pytest.mark.ddt(
        TestData(
            arguments=("group_name", "group_opts"),
            indirect=("group_opts",),
            argument_data_set=[
                ArgumentData(id="empty_group", values=(FAKER.text.word(), 0)),
                ArgumentData(
                    id="normal_group",
                    values=(FAKER.text.word(), FAKER.numbers.integer_number(1, 10)),
                ),
            ],
        ),
    )
    def test_group_init(self, group_name: str, group_opts: Sequence[Opt]) -> None:
        group = Group(group_name, group_opts)
        for opt in group_opts:
            assert opt.value == getattr(group, opt.name, None)

    @pytest.mark.ddt(
        TestData(
            arguments=("group_name", "group_opts"),
            indirect=("group_opts",),
            argument_data_set=[
                ArgumentData(id="access_non-existent_opt", values=(FAKER.text.word(), 1)),
            ],
        ),
    )
    def test_group_access_error(self, group_name: str, group_opts: Sequence[Opt]) -> None:
        group = Group(group_name, group_opts)
        expected_exception = AttributeError
        with pytest.raises(expected_exception):
            getattr(group, f"{FAKER.text.word()}-test")

    @pytest.mark.ddt(
        TestData(
            arguments=("group_name", "group_opts"),
            indirect=("group_opts",),
            argument_data_set=[
                ArgumentData(
                    id="normal_group",
                    values=(FAKER.text.word(), FAKER.numbers.integer_number(1, 10)),
                ),
            ],
        ),
    )
    def test_group_like_collection(self, group_name: str, group_opts: Sequence[Opt]) -> None:
        group = Group(group_name, group_opts)
        for opt in group_opts:
            assert opt.name in group
        assert len(group) == len(group_opts)
        opt_names = {opt.name for opt in group_opts}
        for item in group:
            assert item in opt_names

    @pytest.mark.ddt(
        TestData(
            arguments=("group_name", "group_opts"),
            indirect=("group_opts",),
            argument_data_set=[
                ArgumentData(
                    id="normal_group",
                    values=(FAKER.text.word(), FAKER.numbers.integer_number(1, 10)),
                ),
            ],
        ),
    )
    def test_group_repr(self, group_name: str, group_opts: Sequence[Opt]) -> None:
        group = Group(group_name, group_opts)
        opt_template = "{}=Opt(name='{}')"
        for opt in group_opts:
            opt_str = opt_template.format(opt.name, opt.name)
            assert opt_str in repr(group)

    @pytest.mark.ddt(
        TestData(
            arguments=("group_name", "group_opts"),
            indirect=("group_opts",),
            argument_data_set=[
                ArgumentData(
                    id="normal_group",
                    values=(FAKER.text.word(), FAKER.numbers.integer_number(1, 10)),
                ),
            ],
        ),
    )
    def test_group_keys(self, group_name: str, group_opts: Sequence[Opt]) -> None:
        group = Group(group_name, group_opts)
        opt_names = {opt.name for opt in group_opts}
        for item in group.keys():
            assert item in opt_names

    @pytest.mark.ddt(
        TestData(
            arguments=("group_name", "group_opts"),
            indirect=("group_opts",),
            argument_data_set=[
                ArgumentData(
                    id="normal_group",
                    values=(FAKER.text.word(), FAKER.numbers.integer_number(1, 10)),
                ),
            ],
        ),
    )
    def test_group_values(self, group_name: str, group_opts: Sequence[Opt]) -> None:
        group = Group(group_name, group_opts)
        opts = {opt for opt in group_opts}
        opt_ids = {id(opt) for opt in group_opts}
        for item in group.values():
            assert item in opts
            assert id(item) in opt_ids

    @pytest.mark.ddt(
        TestData(
            arguments=("group_name", "group_opts"),
            indirect=("group_opts",),
            argument_data_set=[
                ArgumentData(
                    id="normal_group",
                    values=(FAKER.text.word(), FAKER.numbers.integer_number(1, 10)),
                ),
            ],
        ),
    )
    def test_group_items(self, group_name: str, group_opts: Sequence[Opt]) -> None:
        group = Group(group_name, group_opts)
        opt_names = {opt.name for opt in group_opts}
        opts = {opt for opt in group_opts}
        opt_ids = {id(opt) for opt in group_opts}
        for name, item in group.items():
            assert name in opt_names
            assert item in opts
            assert id(item) in opt_ids


class TestConfiguration:
    @pytest.fixture
    def config_groups(self, request: SubRequest) -> Sequence[Group]:
        count: int = request.param
        groups = []
        for _ in range(count):
            opts = []
            for __ in range(FAKER.numbers.integer_number(1, 10)):
                opt_data = asdict(
                    FakeOptData(schema=StrictStr, default=FAKER.text.word()),
                )
                opt = Opt(**opt_data)
                opt.load(None)
                opts.append(opt)
            group = Group(FAKER.text.word(), opts)
            groups.append(group)
        return groups

    @pytest.fixture
    def config_setup_params(
        self,
        request: SubRequest,
        tmp_path: Path,
    ) -> Tuple[str, Dict[str, str]]:
        project: str = request.param.get("project", "")
        env: Dict[str, str] = request.param.get("env", "")
        env["OS_CONFIG_DIR"] = tmp_path.as_posix()
        tmp_path.joinpath(f"{project}.yaml").write_text("{}")
        return (project, env)

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(id="empty_config", values=(0,)),
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_init(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        for group in config_groups:
            assert group is getattr(config, group.name, None)
            assert id(group) == id(getattr(config, group.name, None))

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="access_non-existent_group",
                    values=(1,),
                ),
            ],
        ),
    )
    def test_configuration_access_error(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        expected_exception = AttributeError
        with pytest.raises(expected_exception):
            getattr(config, f"{FAKER.text.word()}-test")

    @pytest.mark.ddt(
        TestData(
            arguments=(
                "project",
                "env",
                "expected_config_path",
            ),
            argument_data_set=[
                ArgumentData(
                    id="set_env_config_dir",
                    values=(
                        "fake_project_name",
                        {"OS_CONFIG_DIR": "env_config_dir"},
                        ("env_config_dir", "env_config_dir/fake_project_name.yaml"),
                    ),
                ),
                ArgumentData(
                    id="no_set_env",
                    values=(
                        "fake_project_name",
                        {},
                        (
                            "/etc/fake_project_name",
                            "/etc/fake_project_name/fake_project_name.yaml",
                        ),
                    ),
                ),
            ],
        ),
    )
    def test_configuration_get_config_path(
        self,
        project: str,
        env: Dict[str, str],
        expected_config_path: Tuple[str, str],
    ) -> None:
        assert Configuration.get_config_path(project, env) == expected_config_path

    @pytest.mark.ddt(
        TestData(
            arguments=("config_setup_params",),
            indirect=("config_setup_params",),
            argument_data_set=[
                ArgumentData(
                    id="set_env_config_dir",
                    values=(
                        {
                            "project": "fake_project_name",
                            "env": {"OS_CONFIG_DIR": ""},
                        },
                    ),
                ),
            ],
        ),
    )
    def test_configuration_setup(self, config_setup_params: Tuple[str, Dict[str, str]]) -> None:
        groups = []
        for _ in range(FAKER.numbers.integer_number(1, 10)):
            opts = []
            for __ in range(FAKER.numbers.integer_number(1, 10)):
                opt_data = asdict(
                    FakeOptData(schema=StrictStr, default=FAKER.text.word()),
                )
                opts.append(Opt(**opt_data))
            groups.append(Group(FAKER.text.word(), opts))
        config = Configuration(groups)
        project = config_setup_params[0]
        env = config_setup_params[1]
        config.setup(project, env)
        for group in config:
            for opt in getattr(config, group):
                opt_value = getattr(getattr(config, group, None), opt)
                assert isinstance(opt_value, str)

    @pytest.mark.ddt(
        TestData(
            arguments=("config_setup_params",),
            indirect=("config_setup_params",),
            argument_data_set=[
                ArgumentData(
                    id="not_found_config_file",
                    values=(
                        {
                            "project": "fake_project_name",
                            "env": {"OS_CONFIG_DIR": ""},
                        },
                    ),
                ),
            ],
        ),
    )
    def test_configuration_setup_non_existent_error(
        self,
        config_setup_params: Tuple[str, Dict[str, str]],
    ) -> None:
        groups = []
        for _ in range(FAKER.numbers.integer_number(1, 10)):
            opts = []
            for __ in range(FAKER.numbers.integer_number(1, 10)):
                opt_data = asdict(
                    FakeOptData(schema=StrictStr, default=FAKER.text.word()),
                )
                opts.append(Opt(**opt_data))
            groups.append(Group(FAKER.text.word(), opts))
        config = Configuration(groups)
        project = config_setup_params[0]
        env = config_setup_params[1]
        config_dir_path, config_file_path = config.get_config_path(project, env)
        Path(config_file_path).unlink(missing_ok=True)
        expected_exception = ValueError
        with pytest.raises(expected_exception, match="Not found config file"):
            config.setup(project, env)

    @pytest.mark.ddt(
        TestData(
            arguments=("config_setup_params",),
            indirect=("config_setup_params",),
            argument_data_set=[
                ArgumentData(
                    id="file_is_not_yaml",
                    values=(
                        {
                            "project": "fake_project_name",
                            "env": {"OS_CONFIG_DIR": ""},
                        },
                    ),
                ),
            ],
        ),
    )
    def test_configuration_setup_yaml_format_error(
        self,
        config_setup_params: Tuple[str, Dict[str, str]],
    ) -> None:
        groups = []
        for _ in range(FAKER.numbers.integer_number(1, 10)):
            opts = []
            for __ in range(FAKER.numbers.integer_number(1, 10)):
                opt_data = asdict(
                    FakeOptData(schema=StrictStr, default=FAKER.text.word()),
                )
                opts.append(Opt(**opt_data))
            groups.append(Group(FAKER.text.word(), opts))
        config = Configuration(groups)
        project = config_setup_params[0]
        env = config_setup_params[1]
        config_dir_path, config_file_path = config.get_config_path(project, env)
        Path(config_file_path).write_text("{")
        expected_exception = ValueError
        with pytest.raises(expected_exception, match="Load config file error"):
            config.setup(project, env)

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_cleanup(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        assert len(config) == len(config_groups)
        config.cleanup()
        assert len(config) == 0

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_call(self, config_groups: Sequence[Group]) -> None:
        config = Configuration()
        config(config_groups)
        for group in config_groups:
            assert group is getattr(config, group.name, None)
            assert id(group) == id(getattr(config, group.name, None))

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_like_collection(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        for group in config_groups:
            assert group.name in config
        assert len(config) == len(config_groups)
        group_names = {group.name for group in config_groups}
        for item in config:
            assert item in group_names

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_repr(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        group_template = "{}=Group(name='{}')"
        for group in config_groups:
            group_str = group_template.format(group.name, group.name)
            assert group_str in repr(config)

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_keys(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        group_names = {group.name for group in config_groups}
        for item in config.keys():
            assert item in group_names

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_values(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        groups = {group for group in config_groups}
        group_ids = {id(group) for group in config_groups}
        for item in config.values():
            assert item in groups
            assert id(item) in group_ids

    @pytest.mark.ddt(
        TestData(
            arguments=("config_groups",),
            indirect=("config_groups",),
            argument_data_set=[
                ArgumentData(
                    id="normal_config",
                    values=(FAKER.numbers.integer_number(1, 10),),
                ),
            ],
        ),
    )
    def test_configuration_items(self, config_groups: Sequence[Group]) -> None:
        config = Configuration(config_groups)
        group_names = {group.name for group in config_groups}
        groups = {group for group in config_groups}
        group_ids = {id(group) for group in config_groups}
        for name, item in config.items():
            assert name in group_names
            assert item in groups
            assert id(item) in group_ids
