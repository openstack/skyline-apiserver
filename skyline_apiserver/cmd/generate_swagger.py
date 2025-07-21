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
import traceback

import click

from skyline_apiserver.main import app


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
def main(output_file_path: str) -> None:
    try:
        swagger_dict = app.openapi()
        with open(output_file_path, mode="w") as f:
            f.write(json.dumps(swagger_dict, indent=4))

    except Exception as e:
        print(f"Generate swagger file failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
