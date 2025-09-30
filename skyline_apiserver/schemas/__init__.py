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

# flake8: noqa: F401

from .common import (
    BadRequestMessage,
    ForbiddenMessage,
    InternalServerErrorMessage,
    Message,
    NotFoundMessage,
    UnauthorizedMessage,
)
from .contrib import KeystoneEndpoints
from .extension import (
    ComputeServicesResponse,
    PortDeviceOwner,
    PortSortKey,
    PortsResponse,
    PortStatus,
    RecycleServerSortKey,
    RecycleServersResponse,
    ServerSortKey,
    ServersResponse,
    ServerStatus,
    SortDir,
    VolumeSnapshotSortKey,
    VolumeSnapshotsResponse,
    VolumeSnapshotStatus,
    VolumeSortKey,
    VolumesResponse,
    VolumeStatus,
)
from .login import SSO, Config, Credential, Payload, Profile
from .policy import Policies, PoliciesRules
from .policy_manager import Operation, OperationsSchema, ScopeTypesSchema
from .prometheus import (
    PrometheusQueryData,
    PrometheusQueryRangeData,
    PrometheusQueryRangeResponse,
    PrometheusQueryRangeResult,
    PrometheusQueryResponse,
    PrometheusQueryResult,
)
from .setting import Setting, Settings, UpdateSetting
