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

from dataclasses import dataclass
from typing import Any, Collection, Sequence, Tuple, Union


@dataclass
class ArgumentData:
    id: str
    values: Sequence[object]
    # TODO: Fix type annotation of `marks` after the pytest > 7.0.0
    # marks: Collection[Union[pytest.MarkDecorator, pytest.Mark]]
    marks: Collection[Any] = ()


@dataclass
class TestData:
    arguments: Tuple[str, ...]
    argument_data_set: Sequence[ArgumentData]
    indirect: Union[bool, Tuple[str]] = False

    __test__ = False
