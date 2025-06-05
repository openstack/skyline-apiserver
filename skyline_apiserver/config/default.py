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

from typing import List

from pydantic import StrictBool, StrictInt, StrictStr

from skyline_apiserver.config.base import Opt

debug = Opt(
    name="debug",
    description="Enable debug",
    schema=StrictBool,
    default=False,
)

log_dir = Opt(
    name="log_dir",
    description="Log directory",
    schema=StrictStr,
    default="/var/log/skyline",
)

log_file = Opt(
    name="log_file",
    description="Log file",
    schema=StrictStr,
    default="skyline.log",
)

access_log_file = Opt(
    name="access_log_file",
    description="Nginx access log file",
    schema=StrictStr,
    default="skyline-nginx-access.log",
)

error_log_file = Opt(
    name="error_log_file",
    description="Nginx error log file",
    schema=StrictStr,
    default="skyline-nginx-error.log",
)

secret_key = Opt(
    name="secret_key",
    description="Secret key",
    schema=StrictStr,
    default="aCtmgbcUqYUy_HNVg5BDXCaeJgJQzHJXwqbXr0Nmb2o",
)

access_token_expire = Opt(
    name="access_token_expire",
    description="Access token expire seconds",
    schema=StrictInt,
    default=60 * 60,
)

access_token_renew = Opt(
    name="access_token_renew",
    description="access token renew seconds",
    schema=StrictInt,
    default=30 * 60,
)

cors_allow_origins = Opt(
    name="cors_allow_origins",
    description="CORS allow origins",
    schema=List[StrictStr],
    default=[],
)

session_name = Opt(
    name="session_name",
    description="Session name",
    schema=StrictStr,
    default="session",
)

database_url = Opt(
    name="database_url",
    description="Database url. For mariadb, set as 'mysql://root:root@localhost:3306/skyline'",
    schema=StrictStr,
    default="sqlite:////tmp/skyline.db",
)

prometheus_endpoint = Opt(
    name="prometheus_endpoint",
    description="Prometheus Endpoint",
    schema=StrictStr,
    default="http://localhost:9091",
)

prometheus_enable_basic_auth = Opt(
    name="prometheus_enable_basic_auth",
    description="Start Prometheus Basic Auth",
    schema=StrictBool,
    default=False,
)

prometheus_basic_auth_user = Opt(
    name="prometheus_basic_auth_user",
    description="Prometheus Basic Auth username",
    schema=StrictStr,
    default="",
)

prometheus_basic_auth_password = Opt(
    name="prometheus_basic_auth_password",
    description="Prometheus Basic Auth password",
    schema=StrictStr,
    default="",
)

ssl_enabled = Opt(
    name="ssl_enabled",
    description="Enable ssl",
    schema=StrictBool,
    default=True,
)

cafile = Opt(
    name="cafile",
    description="A path to a CA file",
    schema=StrictStr,
    default="",
)

policy_file_suffix = Opt(
    name="policy_file_suffix",
    description="policy file suffix",
    schema=StrictStr,
    default="policy.yaml",
)

policy_file_path = Opt(
    name="policy_file_path",
    description="A path to policy file",
    schema=StrictStr,
    default="/etc/skyline/policy",
)


GROUP_NAME = __name__.split(".")[-1]
ALL_OPTS = (
    debug,
    log_dir,
    log_file,
    access_log_file,
    error_log_file,
    secret_key,
    access_token_expire,
    access_token_renew,
    cors_allow_origins,
    session_name,
    ssl_enabled,
    cafile,
    database_url,
    prometheus_endpoint,
    prometheus_enable_basic_auth,
    prometheus_basic_auth_user,
    prometheus_basic_auth_password,
    policy_file_suffix,
    policy_file_path,
)

__all__ = ("GROUP_NAME", "ALL_OPTS")
