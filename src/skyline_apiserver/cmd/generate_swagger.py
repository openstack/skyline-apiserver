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

import json
import sys
from logging import StreamHandler

import aiofiles
import click
from skyline_log import LOG, setup as log_setup

from skyline_apiserver.config import configure
from skyline_apiserver.main import app
from skyline_apiserver.utils.coroutine import sync_run


class CommandException(Exception):
    EXIT_CODE = 1


@click.command(help="Generate swagger file.")
@click.option(
    "-o",
    "--output-file",
    "output_file_path",
    default="swagger.json",
    help=(
        "The path of the output file, this file is used to generate a OpenAPI file for "
        "use in the development process. (Default value: swagger.json)"
    ),
)
@sync_run
async def main(output_file_path: str) -> None:
    try:
        configure("skyline-apiserver")
        log_setup(StreamHandler())

        swagger_dict = app.openapi()
        async with aiofiles.open(output_file_path, mode="w") as f:
            await f.write(json.dumps(swagger_dict, indent=4))

    except CommandException as e:
        LOG.error(e)
        sys.exit(e.EXIT_CODE)


if __name__ == "__main__":
    main()
