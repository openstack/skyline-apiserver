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
        description="No description",
    ),
    base.Rule(
        name="admin_or_owner",
        check_str=("is_admin:True or (role:admin and is_admin_project:True) or project_id:%(project_id)s"),
        description="No description",
    ),
    base.Rule(
        name="default",
        check_str=(""),
        description="No description",
    ),
    base.Rule(
        name="project_member_api",
        check_str=("role:member and project_id:%(project_id)s"),
        description="Default rule for Project level non admin APIs.",
    ),
    base.Rule(
        name="project_reader_api",
        check_str=("role:reader and project_id:%(project_id)s"),
        description="Default rule for Project level read only APIs.",
    ),
    base.Rule(
        name="project_member_or_admin",
        check_str=("rule:project_member_api or rule:context_is_admin"),
        description="Default rule for Project Member or admin APIs.",
    ),
    base.Rule(
        name="project_reader_or_admin",
        check_str=("rule:project_reader_api or rule:context_is_admin"),
        description="Default rule for Project reader or admin APIs.",
    ),
    base.APIRule(
        name="collector:list_mappings",
        check_str=("role:admin"),
        description="Return the list of every services mapped to a collector.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/collector/mappings")],
    ),
    base.APIRule(
        name="collector:get_mapping",
        check_str=("role:admin"),
        description="Return a service to collector mapping.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/collector/mappings/{service_id}")],
    ),
    base.APIRule(
        name="collector:manage_mapping",
        check_str=("role:admin"),
        description="Manage a service to collector mapping.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/collector/mappings"), Operation(method="DELETE", path="/v1/collector/mappings/{service_id}")],
    ),
    base.APIRule(
        name="collector:get_state",
        check_str=("role:admin"),
        description="Query the enable state of a collector.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/collector/states/{collector_id}")],
    ),
    base.APIRule(
        name="collector:update_state",
        check_str=("role:admin"),
        description="Set the enable state of a collector.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v1/collector/states/{collector_id}")],
    ),
    base.APIRule(
        name="info:list_services_info",
        check_str=(""),
        description="List available services information in Cloudkitty.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/info/services")],
    ),
    base.APIRule(
        name="info:get_service_info",
        check_str=(""),
        description="Get specified service information.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/info/services/{metric_id}")],
    ),
    base.APIRule(
        name="info:list_metrics_info",
        check_str=(""),
        description="List available metrics information in Cloudkitty.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/info/metrics")],
    ),
    base.APIRule(
        name="info:get_metric_info",
        check_str=(""),
        description="Get specified metric information.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/info/metrics/{metric_id}")],
    ),
    base.APIRule(
        name="info:get_config",
        check_str=(""),
        description="Get current configuration in Cloudkitty.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/info/config")],
    ),
    base.APIRule(
        name="rating:list_modules",
        check_str=("role:admin"),
        description="Return the list of loaded modules in Cloudkitty.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/rating/modules")],
    ),
    base.APIRule(
        name="rating:get_module",
        check_str=("role:admin"),
        description="Get specified module.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/rating/modules/{module_id}")],
    ),
    base.APIRule(
        name="rating:update_module",
        check_str=("role:admin"),
        description="Change the state and priority of a module.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v1/rating/modules/{module_id}")],
    ),
    base.APIRule(
        name="rating:quote",
        check_str=(""),
        description="Get an instant quote based on multiple resource descriptions.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/rating/quote")],
    ),
    base.APIRule(
        name="rating:module_config",
        check_str=("role:admin"),
        description="Trigger a rating module list reload.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/rating/reload_modules")],
    ),
    base.APIRule(
        name="report:list_tenants",
        check_str=("role:admin"),
        description="Return the list of rated tenants.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/report/tenants")],
    ),
    base.APIRule(
        name="report:get_summary",
        check_str=("rule:project_reader_or_admin"),
        description="Return the summary to pay for a given period.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/report/summary")],
    ),
    base.APIRule(
        name="report:get_total",
        check_str=("rule:project_reader_or_admin"),
        description="Return the amount to pay for a given period.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/report/total")],
    ),
    base.APIRule(
        name="storage:list_data_frames",
        check_str=("rule:project_reader_or_admin"),
        description="Return a list of rated resources for a time period and a tenant.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/storage/dataframes")],
    ),
    base.APIRule(
        name="dataframes:add",
        check_str=("role:admin"),
        description="Add one or several DataFrames",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/dataframes")],
    ),
    base.APIRule(
        name="dataframes:get",
        check_str=("rule:project_reader_or_admin"),
        description="Get DataFrames",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/dataframes")],
    ),
    base.APIRule(
        name="v2_rating:list_modules",
        check_str=("role:admin"),
        description="Returns the list of loaded modules in Cloudkitty.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/rating/modules")],
    ),
    base.APIRule(
        name="v2_rating:get_module",
        check_str=("role:admin"),
        description="Get specified module.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/rating/modules/{module_id}")],
    ),
    base.APIRule(
        name="v2_rating:update_module",
        check_str=("role:admin"),
        description="Change the state and priority of a module.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v2/rating/modules/{module_id}")],
    ),
    base.APIRule(
        name="scope:get_state",
        check_str=("role:admin"),
        description="Get the state of one or several scopes",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/scope")],
    ),
    base.APIRule(
        name="scope:reset_state",
        check_str=("role:admin"),
        description="Reset the state of one or several scopes",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v2/scope")],
    ),
    base.APIRule(
        name="scope:patch_state",
        check_str=("role:admin"),
        description="Enables operators to patch a storage scope",
        scope_types=["project"],
        operations=[Operation(method="PATCH", path="/v2/scope")],
    ),
    base.APIRule(
        name="scope:post_state",
        check_str=("role:admin"),
        description="Enables operators to create a storage scope",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/scope")],
    ),
    base.APIRule(
        name="summary:get_summary",
        check_str=("rule:project_reader_or_admin"),
        description="Get a rating summary",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/summary")],
    ),
    base.APIRule(
        name="schedule:task_reprocesses",
        check_str=("role:admin"),
        description="Schedule a scope for reprocessing",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/task/reprocesses")],
    ),
    base.APIRule(
        name="schedule:get_task_reprocesses",
        check_str=("role:admin"),
        description="Get reprocessing schedule tasks for scopes.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/task/reprocesses")],
    ),
)

__all__ = ("list_rules",)
