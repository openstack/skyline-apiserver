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

import os

from skyline_apiserver.config.base import Configuration, Group

from . import default, openstack, setting

CONF = Configuration()


def configure(project: str, setup: bool = True) -> None:
    conf_modules = (
        (default.GROUP_NAME, default.ALL_OPTS),
        (openstack.GROUP_NAME, openstack.ALL_OPTS),
        (setting.GROUP_NAME, setting.ALL_OPTS),
    )
    groups = [Group(*item) for item in conf_modules]
    CONF(groups)
    if setup:
        CONF.setup(project, os.environ.copy())


__all__ = ("CONF", "configure")
