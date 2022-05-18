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

from typing import Any, Dict, List

from pydantic.types import StrictStr

from skyline_apiserver.config.base import Opt

base_settings = Opt(
    name="base_settings",
    description="base settings list",
    schema=List[StrictStr],
    default=[
        "flavor_families",
        "gpu_models",
        "usb_models",
    ],
)

flavor_families = Opt(
    name="flavor_families",
    description="Flavor families",
    schema=List[Dict[str, Any]],
    default=[
        {
            "architecture": "x86_architecture",
            "categories": [
                {"name": "general_purpose", "properties": []},
                {"name": "compute_optimized", "properties": []},
                {"name": "memory_optimized", "properties": []},
                # {"name": "big_data", "properties": []},
                # {"name": "local_ssd", "properties": []},
                {"name": "high_clock_speed", "properties": []},
            ],
        },
        {
            "architecture": "heterogeneous_computing",
            "categories": [
                {"name": "compute_optimized_type_with_gpu", "properties": []},
                {"name": "visualization_compute_optimized_type_with_gpu", "properties": []},
                # {"name": "compute_optimized_type", "properties": []},
            ],
        },
        # {
        #     "architecture": "arm_architecture",
        #     "categories": [
        #         {"name": "general_purpose", "properties": []},
        #         {"name": "compute_optimized", "properties": []},
        #         {"name": "memory_optimized", "properties": []},
        #         {"name": "big_data", "properties": []},
        #         {"name": "local_ssd", "properties": []},
        #         {"name": "high_clock_speed", "properties": []},
        #     ],
        # },
    ],
)

gpu_models = Opt(
    name="gpu_models",
    description="gpu_models",
    schema=List[StrictStr],
    default=["nvidia_t4"],
)

usb_models = Opt(
    name="usb_models",
    description="usb_models",
    schema=List[StrictStr],
    default=["usb_c"],
)


GROUP_NAME = __name__.split(".")[-1]
ALL_OPTS = (
    base_settings,
    flavor_families,
    gpu_models,
    usb_models,
)

__all__ = ("GROUP_NAME", "ALL_OPTS")
