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

from typing import TYPE_CHECKING

from _pytest.mark import ParameterSet
from tests.models import TestData

if TYPE_CHECKING:
    from _pytest.python import Metafunc


def pytest_generate_tests(metafunc: Metafunc) -> None:
    for marker in metafunc.definition.iter_markers(name="ddt"):
        test_data: TestData
        for test_data in marker.args:
            argument_length = len(test_data.arguments)
            argvalues = []
            for argument_data in test_data.argument_data_set:
                if len(argument_data.values) != argument_length:
                    raise ValueError(
                        f'Argument data "{argument_data.id}" of method '
                        f'"{metafunc.function.__name__}" doesn\'t match '
                        "number of arguments.",
                    )
                argvalues.append(
                    ParameterSet(
                        id=argument_data.id,
                        marks=argument_data.marks,
                        values=argument_data.values,
                    ),
                )

            metafunc.parametrize(test_data.arguments, argvalues, indirect=test_data.indirect)
