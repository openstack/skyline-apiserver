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

import sys
from logging import StreamHandler
from pathlib import Path, PurePath
from typing import Dict
from urllib.parse import urlparse

import click
from jinja2 import Template
from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session
from keystoneclient.client import Client as KeystoneClient
from pydantic import BaseModel
from skyline_console import static_path  # type: ignore [attr-defined, unused-ignore]

import skyline_apiserver
from skyline_apiserver.config import CONF, configure
from skyline_apiserver.log import LOG, setup
from skyline_apiserver.types import constants


class CommandException(Exception):
    EXIT_CODE = 1


class ProxyEndpoint(BaseModel):
    part: str
    location: str
    url: str
    host: str


def get_system_session() -> Session:
    auth = Password(
        auth_url=CONF.openstack.keystone_url,
        user_domain_name=CONF.openstack.system_user_domain,
        username=CONF.openstack.system_user_name,
        password=CONF.openstack.system_user_password,
        project_name=CONF.openstack.system_project,
        project_domain_name=CONF.openstack.system_project_domain,
        reauthenticate=True,
    )
    return Session(auth=auth, verify=CONF.default.cafile, timeout=30)


def get_proxy_endpoints() -> Dict[str, ProxyEndpoint]:
    ks_client = KeystoneClient(
        session=get_system_session(),
        interface=CONF.openstack.interface_type,
        region_name=CONF.openstack.default_region,
    )
    endpoints_list = ks_client.endpoints.list(interface=CONF.openstack.interface_type)
    service_list = ks_client.services.list()
    services = {s.id: s.type for s in service_list}

    endpoints = {}
    for endpoint in endpoints_list:
        proxy = ProxyEndpoint(part="", location="", url="", host="")
        region = endpoint.region
        service_type = services.get(endpoint.service_id)
        service = CONF.openstack.service_mapping.get(service_type)
        if service is None:
            continue
        if f"{region}-{service_type}" in endpoints:
            raise KeyError(
                f'Region "{region}" service type "{service_type}" conflict in endpoints.',
            )

        proxy.part = f"# {region} {service}"
        location = PurePath("/").joinpath(
            CONF.openstack.nginx_prefix,
            region.lower(),
            service,
        )
        proxy.location = f"{str(location)}/"

        raw_url = urlparse(endpoint.url)
        path = ""
        if raw_url.path:
            raw_path = PurePath(raw_url.path)
            if len(raw_path.parts) > 1:
                if raw_path.match("*[%$](*_id)s"):
                    # glob-style pattern: *, ?, [], [!], [-]
                    # The url of endpoint maybe like:
                    # 1. $(tenant_id)s or %(tenant_id)s
                    # 2. $(project_id)s or %(project_id)s
                    # 3. AUTH_$(tenant_id)s or AUTH_%(tenant_id)s
                    # 4. AUTH_$(project_id)s or AUTH_%(project_id)s
                    path = "" if str(raw_path.parents[1]) == "/" else str(raw_path.parents[1])
                elif raw_path.match("v[0-9]") or raw_path.match("v[0-9][.][0-9]"):
                    path = "" if str(raw_path.parents[0]) == "/" else str(raw_path.parents[0])
                else:
                    path = str(raw_path)
        url = raw_url._replace(path=f"{str(path)}/")
        proxy.url = url.geturl()
        proxy.host = url.netloc
        endpoints[f"{region}-{service_type}"] = proxy

    return dict(sorted(endpoints.items(), key=lambda d: d[0]))


@click.command(help="Generate nginx proxy config file.")
@click.option(
    "-o",
    "--output-file",
    "output_file_path",
    help=(
        "The path of the output file, this file is to generate a reverse proxy configuration "
        "file based on the openstack endpoint and should be used in the location part of nginx."
    ),
)
@click.option(
    "--ssl-certfile",
    "ssl_certfile",
    help=("SSL certificate file path."),
)
@click.option(
    "--ssl-keyfile",
    "ssl_keyfile",
    help=("SSL key file path."),
)
@click.option(
    "--listen-address",
    "listen_address",
    help=("nginx listen address."),
)
@click.option(
    "--log-dir",
    "log_dir",
    help="""Nginx log directory.

When specifying the log directory and access/error log files
paths, the following scenarios are possible:

1) --log-dir is specified (or not, then the default is used)
and --(access|error)-log-file is NOT specified. In this case the default
values for the file path is used

2) --log-dir is speficied (or not ...) and --(access|error)-log-file is also
specified as a relative path. In this case the resulting path will be
{log_dir}/{*_log_file}

3) --log-dir is specified (or not ...) and --(access|error)-log-file is also
specified as an absolute path. In this case the --log-dir is ignored and the
resulting path will be {*_log_file}
""",
)
@click.option(
    "--access-log-file",
    "access_log_file",
    help=("Nginx access log file."),
)
@click.option(
    "--error-log-file",
    "error_log_file",
    help=("Nginx error log file."),
)
def main(
    output_file_path: str,
    ssl_certfile: str,
    ssl_keyfile: str,
    listen_address: str,
    log_dir: str,
    access_log_file: str,
    error_log_file: str,
) -> None:
    try:
        configure("skyline")
        setup(StreamHandler(), debug=CONF.default.debug)

        template_file_path = (
            Path(skyline_apiserver.__file__)
            .parent.joinpath("templates")
            .joinpath("nginx.conf.j2")
        )
        content = ""
        with template_file_path.open() as f:
            content = f.read()
        template = Template(content)

        endpoints = get_proxy_endpoints()
        context = {
            "skyline_console_static_path": static_path,
            "endpoints": [i.model_dump() for i in endpoints.values()],
            "api_prefix": constants.API_PREFIX,
        }
        if ssl_certfile:
            context.update(ssl_certfile=ssl_certfile)
        if ssl_keyfile:
            context.update(ssl_keyfile=ssl_keyfile)
        if listen_address:
            context.update(listen_address=listen_address)
        _access_log_file = Path(log_dir or CONF.default.log_dir).joinpath(
            access_log_file or CONF.default.access_log_file
        )
        _error_log_file = Path(log_dir or CONF.default.log_dir).joinpath(
            error_log_file or CONF.default.error_log_file
        )
        context.update(
            access_log_file=_access_log_file,
            error_log_file=_error_log_file,
        )
        result = template.render(**context)

        if output_file_path:
            with open(output_file_path, mode="w") as f:
                f.write(result)
        else:
            print(result)

    except CommandException as e:
        LOG.error(e)
        sys.exit(e.EXIT_CODE)


if __name__ == "__main__":
    main()
