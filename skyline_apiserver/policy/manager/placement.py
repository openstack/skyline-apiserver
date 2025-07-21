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
        name="admin_api",
        check_str=("role:admin"),
        description="Default rule for most placement APIs.",
    ),
    base.Rule(
        name="system_admin_api",
        check_str=("role:admin and system_scope:all"),
        description="Default rule for System Admin APIs.",
    ),
    base.Rule(
        name="system_reader_api",
        check_str=("role:reader and system_scope:all"),
        description="Default rule for System level read only APIs.",
    ),
    base.Rule(
        name="project_reader_api",
        check_str=("role:reader and project_id:%(project_id)s"),
        description="Default rule for Project level read only APIs.",
    ),
    base.Rule(
        name="system_or_project_reader",
        check_str=("rule:system_reader_api or rule:project_reader_api"),
        description="Default rule for System+Project read only APIs.",
    ),
    base.APIRule(
        name="placement:resource_providers:list",
        check_str=("rule:system_reader_api"),
        description="List resource providers.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers")],
    ),
    base.APIRule(
        name="placement:resource_providers:create",
        check_str=("rule:system_admin_api"),
        description="Create resource provider.",
        scope_types=["system"],
        operations=[Operation(method="POST", path="/resource_providers")],
    ),
    base.APIRule(
        name="placement:resource_providers:show",
        check_str=("rule:system_reader_api"),
        description="Show resource provider.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers/{uuid}")],
    ),
    base.APIRule(
        name="placement:resource_providers:update",
        check_str=("rule:system_admin_api"),
        description="Update resource provider.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/resource_providers/{uuid}")],
    ),
    base.APIRule(
        name="placement:resource_providers:delete",
        check_str=("rule:system_admin_api"),
        description="Delete resource provider.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/resource_providers/{uuid}")],
    ),
    base.APIRule(
        name="placement:resource_classes:list",
        check_str=("rule:system_reader_api"),
        description="List resource classes.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_classes")],
    ),
    base.APIRule(
        name="placement:resource_classes:create",
        check_str=("rule:system_admin_api"),
        description="Create resource class.",
        scope_types=["system"],
        operations=[Operation(method="POST", path="/resource_classes")],
    ),
    base.APIRule(
        name="placement:resource_classes:show",
        check_str=("rule:system_reader_api"),
        description="Show resource class.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_classes/{name}")],
    ),
    base.APIRule(
        name="placement:resource_classes:update",
        check_str=("rule:system_admin_api"),
        description="Update resource class.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/resource_classes/{name}")],
    ),
    base.APIRule(
        name="placement:resource_classes:delete",
        check_str=("rule:system_admin_api"),
        description="Delete resource class.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/resource_classes/{name}")],
    ),
    base.APIRule(
        name="placement:resource_providers:inventories:list",
        check_str=("rule:system_reader_api"),
        description="List resource provider inventories.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers/{uuid}/inventories")],
    ),
    base.APIRule(
        name="placement:resource_providers:inventories:create",
        check_str=("rule:system_admin_api"),
        description="Create one resource provider inventory.",
        scope_types=["system"],
        operations=[Operation(method="POST", path="/resource_providers/{uuid}/inventories")],
    ),
    base.APIRule(
        name="placement:resource_providers:inventories:show",
        check_str=("rule:system_reader_api"),
        description="Show resource provider inventory.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers/{uuid}/inventories/{resource_class}")],
    ),
    base.APIRule(
        name="placement:resource_providers:inventories:update",
        check_str=("rule:system_admin_api"),
        description="Update resource provider inventory.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/resource_providers/{uuid}/inventories"), Operation(method="PUT", path="/resource_providers/{uuid}/inventories/{resource_class}")],
    ),
    base.APIRule(
        name="placement:resource_providers:inventories:delete",
        check_str=("rule:system_admin_api"),
        description="Delete resource provider inventory.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/resource_providers/{uuid}/inventories"), Operation(method="DELETE", path="/resource_providers/{uuid}/inventories/{resource_class}")],
    ),
    base.APIRule(
        name="placement:resource_providers:aggregates:list",
        check_str=("rule:system_reader_api"),
        description="List resource provider aggregates.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers/{uuid}/aggregates")],
    ),
    base.APIRule(
        name="placement:resource_providers:aggregates:update",
        check_str=("rule:system_admin_api"),
        description="Update resource provider aggregates.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/resource_providers/{uuid}/aggregates")],
    ),
    base.APIRule(
        name="placement:resource_providers:usages",
        check_str=("rule:system_reader_api"),
        description="List resource provider usages.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers/{uuid}/usages")],
    ),
    base.APIRule(
        name="placement:usages",
        check_str=("rule:system_or_project_reader"),
        description="List total resource usages for a given project.",
        scope_types=["system", "project"],
        operations=[Operation(method="GET", path="/usages")],
    ),
    base.APIRule(
        name="placement:traits:list",
        check_str=("rule:system_reader_api"),
        description="List traits.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/traits")],
    ),
    base.APIRule(
        name="placement:traits:show",
        check_str=("rule:system_reader_api"),
        description="Show trait.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/traits/{name}")],
    ),
    base.APIRule(
        name="placement:traits:update",
        check_str=("rule:system_admin_api"),
        description="Update trait.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/traits/{name}")],
    ),
    base.APIRule(
        name="placement:traits:delete",
        check_str=("rule:system_admin_api"),
        description="Delete trait.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/traits/{name}")],
    ),
    base.APIRule(
        name="placement:resource_providers:traits:list",
        check_str=("rule:system_reader_api"),
        description="List resource provider traits.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers/{uuid}/traits")],
    ),
    base.APIRule(
        name="placement:resource_providers:traits:update",
        check_str=("rule:system_admin_api"),
        description="Update resource provider traits.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/resource_providers/{uuid}/traits")],
    ),
    base.APIRule(
        name="placement:resource_providers:traits:delete",
        check_str=("rule:system_admin_api"),
        description="Delete resource provider traits.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/resource_providers/{uuid}/traits")],
    ),
    base.APIRule(
        name="placement:allocations:manage",
        check_str=("rule:system_admin_api"),
        description="Manage allocations.",
        scope_types=["system"],
        operations=[Operation(method="POST", path="/allocations")],
    ),
    base.APIRule(
        name="placement:allocations:list",
        check_str=("rule:system_reader_api"),
        description="List allocations.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/allocations/{consumer_uuid}")],
    ),
    base.APIRule(
        name="placement:allocations:update",
        check_str=("rule:system_admin_api"),
        description="Update allocations.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/allocations/{consumer_uuid}")],
    ),
    base.APIRule(
        name="placement:allocations:delete",
        check_str=("rule:system_admin_api"),
        description="Delete allocations.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/allocations/{consumer_uuid}")],
    ),
    base.APIRule(
        name="placement:resource_providers:allocations:list",
        check_str=("rule:system_reader_api"),
        description="List resource provider allocations.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/resource_providers/{uuid}/allocations")],
    ),
    base.APIRule(
        name="placement:allocation_candidates:list",
        check_str=("rule:system_reader_api"),
        description="List allocation candidates.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/allocation_candidates")],
    ),
    base.APIRule(
        name="placement:reshaper:reshape",
        check_str=("rule:system_admin_api"),
        description="Reshape Inventory and Allocations.",
        scope_types=["system"],
        operations=[Operation(method="POST", path="/reshaper")],
    ),
)

__all__ = ("list_rules",)
