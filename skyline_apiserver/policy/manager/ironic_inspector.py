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
        name="is_admin",
        check_str=("role:admin or role:administrator or role:baremetal_admin"),
        description="Full read/write API access",
    ),
    base.Rule(
        name="is_observer",
        check_str=("role:baremetal_observer"),
        description="Read-only API access",
    ),
    base.Rule(
        name="public_api",
        check_str=("is_public_api:True"),
        description="Internal flag for public API routes",
    ),
    base.Rule(
        name="default",
        check_str=("!"),
        description="Default API access policy",
    ),
    base.APIRule(
        name="introspection",
        check_str=("rule:public_api"),
        description="Access the API root for available versions information",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/")],
    ),
    base.APIRule(
        name="introspection:version",
        check_str=("rule:public_api"),
        description="Access the versioned API root for version information",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/{version}")],
    ),
    base.APIRule(
        name="introspection:continue",
        check_str=("rule:public_api"),
        description="Ramdisk callback to continue introspection",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/continue")],
    ),
    base.APIRule(
        name="introspection:status",
        check_str=("role:reader and system_scope:all"),
        description="Get introspection status",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/introspection"), Operation(method="GET", path="/introspection/{node_id}")],
    ),
    base.APIRule(
        name="introspection:start",
        check_str=("role:admin and system_scope:all"),
        description="Start introspection",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/introspection/{node_id}")],
    ),
    base.APIRule(
        name="introspection:abort",
        check_str=("role:admin and system_scope:all"),
        description="Abort introspection",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/introspection/{node_id}/abort")],
    ),
    base.APIRule(
        name="introspection:data",
        check_str=("role:admin and system_scope:all"),
        description="Get introspection data",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/introspection/{node_id}/data")],
    ),
    base.APIRule(
        name="introspection:reapply",
        check_str=("role:admin and system_scope:all"),
        description="Reapply introspection on stored data",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/introspection/{node_id}/data/unprocessed")],
    ),
    base.APIRule(
        name="introspection:rule:get",
        check_str=("role:admin and system_scope:all"),
        description="Get introspection rule(s)",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/rules"), Operation(method="GET", path="/rules/{rule_id}")],
    ),
    base.APIRule(
        name="introspection:rule:delete",
        check_str=("role:admin and system_scope:all"),
        description="Delete introspection rule(s)",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/rules"), Operation(method="DELETE", path="/rules/{rule_id}")],
    ),
    base.APIRule(
        name="introspection:rule:create",
        check_str=("role:admin and system_scope:all"),
        description="Create introspection rule",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/rules")],
    ),
)

__all__ = ("list_rules",)
