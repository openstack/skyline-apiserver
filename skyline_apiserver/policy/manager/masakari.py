# Copyright 2022 99cloud
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

# flake8: noqa
# fmt: off

from skyline_apiserver.schemas.policy_manager import Operation

from . import base

list_rules = (
    base.Rule(
        name="context_is_admin",
        check_str=("role:admin"),
        description="Decides what is required for the 'is_admin:True' check to succeed.",
    ),
    base.Rule(
        name="admin_or_owner",
        check_str=("is_admin:True or project_id:%(project_id)s"),
        description="Default rule for most non-Admin APIs.",
    ),
    base.Rule(
        name="admin_api",
        check_str=("is_admin:True"),
        description="Default rule for most Admin APIs.",
    ),
    base.Rule(
        name="os_masakari_api:extensions:discoverable",
        check_str=("rule:admin_api"),
        description="Extension Info API extensions to change the API.",
    ),
    base.Rule(
        name="os_masakari_api:os-hosts:discoverable",
        check_str=("rule:admin_api"),
        description="Host API extensions to change the API.",
    ),
    base.Rule(
        name="os_masakari_api:notifications:discoverable",
        check_str=("rule:admin_api"),
        description="Notification API extensions to change the API.",
    ),
    base.Rule(
        name="os_masakari_api:segments:discoverable",
        check_str=("rule:admin_api"),
        description="Segment API extensions to change the API.",
    ),
    base.Rule(
        name="os_masakari_api:versions:discoverable",
        check_str=("@"),
        description="Version API extensions to change the API.",
    ),
    base.Rule(
        name="os_masakari_api:vmoves:discoverable",
        check_str=("rule:admin_api"),
        description="VM moves API extensions to change the API.",
    ),
    base.APIRule(
        name="os_masakari_api:extensions:index",
        check_str=("rule:admin_api"),
        description="List available extensions.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/extensions")],
    ),
    base.APIRule(
        name="os_masakari_api:extensions:detail",
        check_str=("rule:admin_api"),
        description="Shows information for an extension.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/extensions/{extensions_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:os-hosts:index",
        check_str=("rule:admin_api"),
        description="Lists IDs, names, type, reserved, on_maintenance for all hosts.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/segments/{segment_id}/hosts")],
    ),
    base.APIRule(
        name="os_masakari_api:os-hosts:detail",
        check_str=("rule:admin_api"),
        description="Shows details for a host.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/segments/{segment_id}/hosts/{host_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:os-hosts:create",
        check_str=("rule:admin_api"),
        description="Creates a host under given segment.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/segments/{segment_id}/hosts")],
    ),
    base.APIRule(
        name="os_masakari_api:os-hosts:update",
        check_str=("rule:admin_api"),
        description="Updates the editable attributes of an existing host.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/segments/{segment_id}/hosts/{host_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:os-hosts:delete",
        check_str=("rule:admin_api"),
        description="Deletes a host from given segment.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/segments/{segment_id}/hosts/{host_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:notifications:index",
        check_str=("rule:admin_api"),
        description="Lists IDs, notification types, host_name, generated_time, payload and status for all notifications.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/notifications")],
    ),
    base.APIRule(
        name="os_masakari_api:notifications:detail",
        check_str=("rule:admin_api"),
        description="Shows details for a notification.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/notifications/{notification_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:notifications:create",
        check_str=("rule:admin_api"),
        description="Creates a notification.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/notifications")],
    ),
    base.APIRule(
        name="os_masakari_api:segments:index",
        check_str=("rule:admin_api"),
        description="Lists IDs, names, description, recovery_method, service_type for all segments.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/segments")],
    ),
    base.APIRule(
        name="os_masakari_api:segments:detail",
        check_str=("rule:admin_api"),
        description="Shows details for a segment.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/segments/{segment_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:segments:create",
        check_str=("rule:admin_api"),
        description="Creates a segment.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/segments")],
    ),
    base.APIRule(
        name="os_masakari_api:segments:update",
        check_str=("rule:admin_api"),
        description="Updates the editable attributes of an existing host.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/segments/{segment_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:segments:delete",
        check_str=("rule:admin_api"),
        description="Deletes a segment.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/segments/{segment_id}")],
    ),
    base.APIRule(
        name="os_masakari_api:versions:index",
        check_str=("@"),
        description="List all versions.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/")],
    ),
    base.APIRule(
        name="os_masakari_api:vmoves:index",
        check_str=("rule:admin_api"),
        description="Lists IDs, notification_id, instance_id, source_host, dest_host, status and type for all VM moves.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/notifications/{notification_id}/vmoves")],
    ),
    base.APIRule(
        name="os_masakari_api:vmoves:detail",
        check_str=("rule:admin_api"),
        description="Shows details for one VM move.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/notifications/{notification_id}/vmoves/{vmove_id}")],
    ),
)

__all__ = ("list_rules",)
