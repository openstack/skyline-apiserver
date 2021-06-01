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

import os

import pytest
from jsonschema import ValidationError

from skyline_apiserver.config import base


@pytest.mark.parametrize(
    "opt",
    [
        {"name": "test0", "help": "this is test0"},
        {"name": "test1", "help": "this is test1", "deprecated": True},
        {"name": "test2", "help": "this is test2", "schema": {"type": "string"}},
        {"name": "test3", "help": "this is test3", "default": "test3"},
    ],
)
@pytest.mark.parametrize("value", ["test_value"])
def test_opt_from_init(opt, value):
    opt = base.Opt(**opt)
    assert opt._loaded is False
    if opt.default is not None:
        value = None
        result = opt.default
    else:
        result = value
    opt.load(value)
    assert opt._loaded is True
    assert opt.value == result
    with pytest.raises(ValueError):
        opt.load(value)


@pytest.mark.parametrize(
    "opt,value",
    [
        ({"name": "test0", "help": "this is test0", "schema": {"type": "null"}}, "test_value"),
        ({"name": "test1", "help": "this is test1", "schema": {"type": "string"}}, None),
        ({"name": "test2", "help": "this is test2", "schema": {"type": "array"}}, None),
        ({"name": "test3", "help": "this is test3", "schema": {"type": "object"}}, None),
    ],
)
def test_opt_from_init_validate(opt, value):
    opt = base.Opt(**opt)
    assert opt._loaded is False
    with pytest.raises(ValidationError):
        opt.load(value)


@pytest.mark.parametrize("opt", [{"name": "test0"}, {"help": "this is test1"}])
def test_opt_from_init_error(opt):
    with pytest.raises(TypeError):
        opt = base.Opt(**opt)


@pytest.mark.parametrize(
    "opt_schema",
    [
        {"title": "test0", "description": "this is test0", "type": "string"},
        {"title": "test1", "description": "this is test1", "type": "string", "default": "test"},
        {"title": "test2", "description": "this is test2", "type": "string", "deprecated": True},
        {
            "title": "test3",
            "description": "this is test3",
            "type": "string",
            "default": "test",
            "deprecated": True,
        },
    ],
)
@pytest.mark.parametrize("value", ["test_value"])
def test_opt_from_schema(opt_schema, value):
    opt = base.Opt.from_schema(opt_schema)
    assert opt._loaded is False
    if opt.default is not None:
        value = None
        result = opt.default
    else:
        result = value
    opt.load(value)
    assert opt._loaded is True
    assert opt.value == result
    with pytest.raises(ValueError):
        opt.load(value)


@pytest.mark.parametrize(
    "opt_schema",
    [
        {"title": "not_description"},
        {"description": "not title"},
        {
            "title": "test_title",
            "description": "deprecated is not boolean",
            "deprecated": "somestring",
        },
    ],
)
def test_opt_from_schema_error(opt_schema):
    with pytest.raises(ValidationError):
        base.Opt.from_schema(opt_schema)


# TODO: add test Group & Configuration


@pytest.mark.parametrize("config_dir", [None, "/etc/tests"])
@pytest.mark.parametrize("config_file", [None, "/etc/tests/test.yaml"])
def test_get_config_file(config_dir, config_file):
    env = {}
    if config_dir is not None:
        env["OS_CONFIG_DIR"] = config_dir
    if config_file is not None:
        env["OS_CONFIG_FILE"] = config_file
    result = []
    def_config_dir = os.path.join("/etc", "skyline")
    result.append(def_config_dir if config_dir is None else config_dir)
    def_config_file = os.path.join(result[0], "skyline_apiserver.yaml")
    result.append(def_config_file if config_file is None else config_file)
    assert base.Configuration._get_config_file(env) == tuple(result)


def test_get_config_file_from_env(monkeypatch):
    monkeypatch.setenv("OS_CONFIG_DIR", "/etc/tests_env")
    monkeypatch.setenv("OS_CONFIG_FILE", "/etc/tests_env/tests_env.yaml")
    assert base.Configuration._get_config_file() == (
        "/etc/tests_env",
        "/etc/tests_env/tests_env.yaml",
    )
