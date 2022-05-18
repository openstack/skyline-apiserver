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

from fastapi import APIRouter

from skyline_apiserver.api.v1 import contrib, extension, login, policy, prometheus, setting

api_router = APIRouter()
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(extension.router, tags=["Extension"])
api_router.include_router(prometheus.router, tags=["Prometheus"])
api_router.include_router(contrib.router, tags=["Contrib"])
api_router.include_router(policy.router, tags=["Policy"])
api_router.include_router(setting.router, tags=["Setting"])
