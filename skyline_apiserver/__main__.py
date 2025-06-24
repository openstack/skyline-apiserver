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
from pprint import pprint

import uvicorn

from skyline_apiserver.config import configure
from skyline_apiserver.log import setup


def main() -> None:
    configure("skyline")
    setup(StreamHandler())
    pprint("Run some debug code")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Start the FastAPI server
        uvicorn.run(
            "skyline_apiserver.main:app",
            host="0.0.0.0",
            port=28000,
            reload=True,
            log_level="debug",
        )
    else:
        # Run debug code
        main()
