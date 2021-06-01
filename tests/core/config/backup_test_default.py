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

import pytest

from skyline_apiserver.config.default import ALL_OPTS, GROUP_NAME


def test_group_name():
    assert GROUP_NAME == "default"


@pytest.mark.parametrize("log_dir_value", [".", "./", "/", "/tmp", "/qwer"])
@pytest.mark.parametrize("debug_value", [True, False])
def test_all_opts(debug_value, log_dir_value):
    for index, opt in enumerate(ALL_OPTS):
        object.__setattr__(opt, "_loaded", False)
        if index == 0:
            opt.load(debug_value)
            assert opt.value == debug_value
        elif index == 1:
            opt.load(log_dir_value)
            assert opt.value == log_dir_value
        object.__setattr__(opt, "_loaded", False)
