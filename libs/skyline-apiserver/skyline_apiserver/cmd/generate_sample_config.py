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

import click
import yaml

from skyline_apiserver.config import CONF, configure


@click.command(help="Generate skyline-apiserver sample config file.")
@click.option(
    "-o",
    "--output-file",
    "output_file_path",
    default="skyline.yaml.sample",
    help=(
        "The path of the output file, this file is used to generate a sample config file "
        "for use. (Default value: skyline.yaml.sample)"
    ),
)
def main(output_file_path: str) -> None:
    try:
        configure("skyline", setup=False)

        result = {}
        for group_name, group in CONF.items():
            result[group_name] = {i.name: i.default for i in group.values()}
        with open(output_file_path, mode="w") as f:
            f.write(yaml.safe_dump(result, allow_unicode=True))

    except Exception as e:
        print(f"Generate skyline-apiserver sample config file failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
