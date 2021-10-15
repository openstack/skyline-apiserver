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
from skyline_apiserver.config.openstack import ALL_OPTS, GROUP_NAME


def test_group_name():
    assert GROUP_NAME == "openstack"


@pytest.mark.parametrize("host_value", ["localhost", "127.0.0.1", "host-1", "192.168.1.1"])
@pytest.mark.parametrize(
    "keystone_url_value",
    [
        "http://localhost:5000/v3/",
        "http://127.0.0.1:5000/v3/",
        "https://keystone:5000/v3/",
        "https://keystone:5000/",
        "https://keystone/",
    ],
)
def test_all_opts(host_value, keystone_url_value):
    for index, opt in enumerate(ALL_OPTS):
        object.__setattr__(opt, "_loaded", False)
        if index == 0:
            opt.load(host_value)
            assert opt.value == host_value
        elif index == 1:
            opt.load(keystone_url_value)
            assert opt.value == keystone_url_value
        object.__setattr__(opt, "_loaded", False)
