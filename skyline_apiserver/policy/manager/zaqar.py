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
        check_str=("is_admin:True or project_id:%(project_id)s"),
        description="No description",
    ),
    base.APIRule(
        name="claims:create",
        check_str=(""),
        description="Claims a set of messages from the specified queue.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/queues/{queue_name}/claims")],
    ),
    base.APIRule(
        name="claims:get",
        check_str=(""),
        description="Queries the specified claim for the specified queue.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues/{queue_name}/claims/{claim_id}")],
    ),
    base.APIRule(
        name="claims:delete",
        check_str=(""),
        description="Releases the specified claim for the specified queue.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/queues/{queue_name}/claims/{claim_id}")],
    ),
    base.APIRule(
        name="claims:update",
        check_str=(""),
        description="Updates the specified claim for the specified queue.",
        scope_types=["project"],
        operations=[Operation(method="PATCH", path="/v2/queues/{queue_name}/claims/{claim_id}")],
    ),
    base.APIRule(
        name="flavors:get_all",
        check_str=(""),
        description="Lists flavors.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/flavors")],
    ),
    base.APIRule(
        name="flavors:create",
        check_str=("role:admin"),
        description="Creates a new flavor.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v2/flavors/{flavor_name}")],
    ),
    base.APIRule(
        name="flavors:get",
        check_str=(""),
        description="Shows details for a flavor.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/flavors/{flavor_name}")],
    ),
    base.APIRule(
        name="flavors:delete",
        check_str=("role:admin"),
        description="Deletes the specified flavor.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/flavors/{flavor_name}")],
    ),
    base.APIRule(
        name="flavors:update",
        check_str=("role:admin"),
        description="Update flavor.",
        scope_types=["project"],
        operations=[Operation(method="PATCH", path="/v2/flavors/{flavor_name}")],
    ),
    base.APIRule(
        name="ping:get",
        check_str=(""),
        description="Simple health check for end user(ping).",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/ping")],
    ),
    base.APIRule(
        name="health:get",
        check_str=("role:admin"),
        description="Detailed health check for cloud operator/admin.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/health")],
    ),
    base.APIRule(
        name="messages:get_all",
        check_str=(""),
        description="List all message in a message queue.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues/{queue_name}/messages")],
    ),
    base.APIRule(
        name="messages:create",
        check_str=(""),
        description="Create a message in a message queue.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/queues/{queue_name}/messages")],
    ),
    base.APIRule(
        name="messages:get",
        check_str=(""),
        description="Retrieve a specific message from a message queue.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues/{queue_name}/messages/{message_id}")],
    ),
    base.APIRule(
        name="messages:delete",
        check_str=(""),
        description="Delete a specific message from a message queue.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/queues/{queue_name}/messages/{message_id}")],
    ),
    base.APIRule(
        name="messages:delete_all",
        check_str=(""),
        description="Delete all messages from a message queue.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/queues/{queue_name}/messages")],
    ),
    base.APIRule(
        name="pools:get_all",
        check_str=("role:admin"),
        description="Lists pools.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/pools")],
    ),
    base.APIRule(
        name="pools:create",
        check_str=("role:admin"),
        description="Creates a pool.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v2/pools/{pool_name}")],
    ),
    base.APIRule(
        name="pools:get",
        check_str=("role:admin"),
        description="Shows details for a pool.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/pools/{pool_name}")],
    ),
    base.APIRule(
        name="pools:delete",
        check_str=("role:admin"),
        description="Delete pool.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/pools/{pool_name}")],
    ),
    base.APIRule(
        name="pools:update",
        check_str=("role:admin"),
        description="Update pool.",
        scope_types=["project"],
        operations=[Operation(method="PATCH", path="/v2/pools/{pool_name}")],
    ),
    base.APIRule(
        name="queues:get_all",
        check_str=(""),
        description="List all message queues.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues")],
    ),
    base.APIRule(
        name="queues:create",
        check_str=(""),
        description="Create a message queue.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v2/queues/{queue_name}")],
    ),
    base.APIRule(
        name="queues:get",
        check_str=(""),
        description="Get details about a specific message queue.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues/{queue_name}")],
    ),
    base.APIRule(
        name="queues:delete",
        check_str=(""),
        description="Delete a message queue.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/queues/{queue_name}")],
    ),
    base.APIRule(
        name="queues:update",
        check_str=(""),
        description="Update a message queue.",
        scope_types=["project"],
        operations=[Operation(method="PATCH", path="/v2/queues/{queue_name}")],
    ),
    base.APIRule(
        name="queues:stats",
        check_str=(""),
        description="Get statistics about a specific message queue.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues/{queue_name}/stats")],
    ),
    base.APIRule(
        name="queues:share",
        check_str=(""),
        description="Create a pre-signed URL for a given message queue.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/queues/{queue_name}/share")],
    ),
    base.APIRule(
        name="queues:purge",
        check_str=(""),
        description="Purge resources from a particular message queue.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/queues/{queue_name}/purge")],
    ),
    base.APIRule(
        name="subscription:get_all",
        check_str=(""),
        description="Lists a queue subscriptions.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues/{queue_name}/subscriptions")],
    ),
    base.APIRule(
        name="subscription:create",
        check_str=(""),
        description="Creates a subscription.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/queues/{queue_name}/subscriptions")],
    ),
    base.APIRule(
        name="subscription:get",
        check_str=(""),
        description="Shows details for a subscription.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/queues/{queue_name}/subscriptions/{subscription_id}")],
    ),
    base.APIRule(
        name="subscription:delete",
        check_str=(""),
        description="Deletes the specified subscription.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/queues/{queue_name}/subscriptions/{subscription_id}")],
    ),
    base.APIRule(
        name="subscription:update",
        check_str=(""),
        description="Updates a subscription.",
        scope_types=["project"],
        operations=[Operation(method="PATCH", path="/v2/queues/{queue_name}/subscriptions/{subscription_id}")],
    ),
    base.APIRule(
        name="subscription:confirm",
        check_str=(""),
        description="Confirms a subscription.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v2/queues/{queue_name}/subscriptions/{subscription_id}/confirm")],
    ),
    base.APIRule(
        name="topics:get_all",
        check_str=(""),
        description="List all topics.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/topics")],
    ),
    base.APIRule(
        name="topics:create",
        check_str=(""),
        description="Create a topic.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v2/topics/{topic_name}")],
    ),
    base.APIRule(
        name="topics:get",
        check_str=(""),
        description="Get details about a specific topic.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/topics/{topic_name}")],
    ),
    base.APIRule(
        name="topics:delete",
        check_str=(""),
        description="Delete a topic.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v2/topics/{topic_name}")],
    ),
    base.APIRule(
        name="topics:update",
        check_str=(""),
        description="Update a topic.",
        scope_types=["project"],
        operations=[Operation(method="PATCH", path="/v2/topics/{topic_name}")],
    ),
    base.APIRule(
        name="topics:stats",
        check_str=(""),
        description="Get statistics about a specific topic.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v2/topics/{topic_name}/stats")],
    ),
    base.APIRule(
        name="topics:purge",
        check_str=(""),
        description="Purge resources from a particular topic.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v2/topic/{topic_name}/purge")],
    ),
)

__all__ = ("list_rules",)
