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
        name="system_reader",
        check_str=("role:reader and system_scope:all"),
        description="No description",
    ),
    base.Rule(
        name="system_admin",
        check_str=("role:admin and system_scope:all"),
        description="No description",
    ),
    base.Rule(
        name="secret_project_match",
        check_str=("project_id:%(target.secret.project_id)s"),
        description="No description",
    ),
    base.Rule(
        name="secret_project_reader",
        check_str=("role:reader and rule:secret_project_match"),
        description="No description",
    ),
    base.Rule(
        name="secret_project_member",
        check_str=("(role:member or role:_member_) and rule:secret_project_match"),
        description="No description",
    ),
    base.Rule(
        name="secret_project_admin",
        check_str=("role:admin and rule:secret_project_match"),
        description="No description",
    ),
    base.Rule(
        name="secret_owner",
        check_str=("user_id:%(target.secret.creator_id)s"),
        description="No description",
    ),
    base.Rule(
        name="secret_is_not_private",
        check_str=("True:%(target.secret.read_project_access)s"),
        description="No description",
    ),
    base.Rule(
        name="secret_acl_read",
        check_str=("'read':%(target.secret.read)s"),
        description="No description",
    ),
    base.Rule(
        name="container_project_match",
        check_str=("project_id:%(target.container.project_id)s"),
        description="No description",
    ),
    base.Rule(
        name="container_project_member",
        check_str=("(role:member or role:_member_) and rule:container_project_match"),
        description="No description",
    ),
    base.Rule(
        name="container_project_admin",
        check_str=("role:admin and rule:container_project_match"),
        description="No description",
    ),
    base.Rule(
        name="container_owner",
        check_str=("user_id:%(target.container.creator_id)s"),
        description="No description",
    ),
    base.Rule(
        name="container_is_not_private",
        check_str=("True:%(target.container.read_project_access)s"),
        description="No description",
    ),
    base.Rule(
        name="container_acl_read",
        check_str=("'read':%(target.container.read)s"),
        description="No description",
    ),
    base.Rule(
        name="order_project_match",
        check_str=("project_id:%(target.order.project_id)s"),
        description="No description",
    ),
    base.Rule(
        name="order_project_member",
        check_str=("(role:member or role:_member_) and rule:order_project_match"),
        description="No description",
    ),
    base.Rule(
        name="audit",
        check_str=("role:audit"),
        description="No description",
    ),
    base.Rule(
        name="observer",
        check_str=("role:observer"),
        description="No description",
    ),
    base.Rule(
        name="creator",
        check_str=("role:creator"),
        description="No description",
    ),
    base.Rule(
        name="admin",
        check_str=("role:admin"),
        description="No description",
    ),
    base.Rule(
        name="service_admin",
        check_str=("role:key-manager:service-admin"),
        description="No description",
    ),
    base.Rule(
        name="all_users",
        check_str=("rule:admin or rule:observer or rule:creator or rule:audit or rule:service_admin"),
        description="No description",
    ),
    base.Rule(
        name="all_but_audit",
        check_str=("rule:admin or rule:observer or rule:creator"),
        description="No description",
    ),
    base.Rule(
        name="admin_or_creator",
        check_str=("rule:admin or rule:creator"),
        description="No description",
    ),
    base.Rule(
        name="secret_creator_user",
        check_str=("user_id:%(target.secret.creator_id)s"),
        description="No description",
    ),
    base.Rule(
        name="secret_private_read",
        check_str=("'False':%(target.secret.read_project_access)s"),
        description="No description",
    ),
    base.Rule(
        name="secret_non_private_read",
        check_str=("rule:all_users and rule:secret_project_match and not rule:secret_private_read"),
        description="No description",
    ),
    base.Rule(
        name="secret_decrypt_non_private_read",
        check_str=("rule:all_but_audit and rule:secret_project_match and not rule:secret_private_read"),
        description="No description",
    ),
    base.Rule(
        name="secret_project_creator",
        check_str=("rule:creator and rule:secret_project_match and rule:secret_creator_user"),
        description="No description",
    ),
    base.Rule(
        name="secret_project_creator_role",
        check_str=("rule:creator and rule:secret_project_match"),
        description="No description",
    ),
    base.Rule(
        name="container_private_read",
        check_str=("'False':%(target.container.read_project_access)s"),
        description="No description",
    ),
    base.Rule(
        name="container_creator_user",
        check_str=("user_id:%(target.container.creator_id)s"),
        description="No description",
    ),
    base.Rule(
        name="container_non_private_read",
        check_str=("rule:all_users and rule:container_project_match and not rule:container_private_read"),
        description="No description",
    ),
    base.Rule(
        name="container_project_creator",
        check_str=("rule:creator and rule:container_project_match and rule:container_creator_user"),
        description="No description",
    ),
    base.Rule(
        name="container_project_creator_role",
        check_str=("rule:creator and rule:container_project_match"),
        description="No description",
    ),
    base.APIRule(
        name="secret_acls:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="Retrieve the ACL settings for a given secret.If no ACL is defined for that secret, then Default ACL is returned.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/secrets/{secret-id}/acl")],
    ),
    base.APIRule(
        name="secret_acls:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="Delete the ACL settings for a given secret.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/secrets/{secret-id}/acl")],
    ),
    base.APIRule(
        name="secret_acls:put_patch",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="Create new, replaces, or updates existing ACL for a given secret.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v1/secrets/{secret-id}/acl"), Operation(method="PATCH", path="/v1/secrets/{secret-id}/acl")],
    ),
    base.APIRule(
        name="container_acls:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private))"),
        description="Retrieve the ACL settings for a given container.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/containers/{container-id}/acl")],
    ),
    base.APIRule(
        name="container_acls:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private))"),
        description="Delete ACL for a given container. No content is returned in the case of successful deletion.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/containers/{container-id}/acl")],
    ),
    base.APIRule(
        name="container_acls:put_patch",
        check_str=("True:%(enforce_new_defaults)s and (rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private))"),
        description="Create new or replaces existing ACL for a given container.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v1/containers/{container-id}/acl"), Operation(method="PATCH", path="/v1/containers/{container-id}/acl")],
    ),
    base.APIRule(
        name="consumer:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:system_admin or rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private) or rule:container_acl_read)"),
        description="DEPRECATED: show information for a specific consumer",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/containers/{container-id}/consumers/{consumer-id}")],
    ),
    base.APIRule(
        name="container_consumers:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:system_admin or rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private) or rule:container_acl_read)"),
        description="List a containers consumers.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/containers/{container-id}/consumers")],
    ),
    base.APIRule(
        name="container_consumers:post",
        check_str=("True:%(enforce_new_defaults)s and (rule:system_admin or rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private) or rule:container_acl_read)"),
        description="Creates a consumer.",
        scope_types=["project", "system"],
        operations=[Operation(method="POST", path="/v1/containers/{container-id}/consumers")],
    ),
    base.APIRule(
        name="container_consumers:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:system_admin or rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private) or rule:container_acl_read)"),
        description="Deletes a consumer.",
        scope_types=["project", "system"],
        operations=[Operation(method="DELETE", path="/v1/containers/{container-id}/consumers")],
    ),
    base.APIRule(
        name="secret_consumers:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:system_admin or rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private) or rule:secret_acl_read)"),
        description="List consumers for a secret.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/secrets/{secret-id}/consumers")],
    ),
    base.APIRule(
        name="secret_consumers:post",
        check_str=("True:%(enforce_new_defaults)s and (rule:system_admin or rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private) or rule:secret_acl_read)"),
        description="Creates a consumer.",
        scope_types=["project", "system"],
        operations=[Operation(method="POST", path="/v1/secrets/{secrets-id}/consumers")],
    ),
    base.APIRule(
        name="secret_consumers:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:system_admin or rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private) or rule:secret_acl_read)"),
        description="Deletes a consumer.",
        scope_types=["project", "system"],
        operations=[Operation(method="DELETE", path="/v1/secrets/{secrets-id}/consumers")],
    ),
    base.APIRule(
        name="containers:post",
        check_str=("True:%(enforce_new_defaults)s and (role:member or role:_member_)"),
        description="Creates a container.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/containers")],
    ),
    base.APIRule(
        name="containers:get",
        check_str=("True:%(enforce_new_defaults)s and (role:member or role:_member_)"),
        description="Lists a projects containers.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/containers")],
    ),
    base.APIRule(
        name="container:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private) or rule:container_acl_read or rule:creator)"),
        description="Retrieves a single container.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/containers/{container-id}")],
    ),
    base.APIRule(
        name="container:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private) or rule:creator)"),
        description="Deletes a container.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/containers/{uuid}")],
    ),
    base.APIRule(
        name="container_secret:post",
        check_str=("True:%(enforce_new_defaults)s and (rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private))"),
        description="Add a secret to an existing container.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/containers/{container-id}/secrets")],
    ),
    base.APIRule(
        name="container_secret:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:container_project_admin or (rule:container_project_member and rule:container_owner) or (rule:container_project_member and  rule:container_is_not_private))"),
        description="Remove a secret from a container.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/containers/{container-id}/secrets/{secret-id}")],
    ),
    base.APIRule(
        name="orders:get",
        check_str=("True:%(enforce_new_defaults)s and (role:member or role:_member_)"),
        description="Gets list of all orders associated with a project.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/orders")],
    ),
    base.APIRule(
        name="orders:post",
        check_str=("True:%(enforce_new_defaults)s and (role:member or role:_member_)"),
        description="Creates an order.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/orders")],
    ),
    base.APIRule(
        name="orders:put",
        check_str=("True:%(enforce_new_defaults)s and (role:member or role:_member_)"),
        description="Unsupported method for the orders API.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v1/orders")],
    ),
    base.APIRule(
        name="order:get",
        check_str=("True:%(enforce_new_defaults)s and rule:order_project_member"),
        description="Retrieves an orders metadata.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/orders/{order-id}")],
    ),
    base.APIRule(
        name="order:delete",
        check_str=("True:%(enforce_new_defaults)s and rule:order_project_member"),
        description="Deletes an order.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/orders/{order-id}")],
    ),
    base.APIRule(
        name="quotas:get",
        check_str=("True:%(enforce_new_defaults)s and role:reader"),
        description="List quotas for the project the user belongs to.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/quotas")],
    ),
    base.APIRule(
        name="project_quotas:get",
        check_str=("True:%(enforce_new_defaults)s and rule:system_reader"),
        description="List quotas for the specified project.",
        scope_types=["system"],
        operations=[Operation(method="GET", path="/v1/project-quotas"), Operation(method="GET", path="/v1/project-quotas/{uuid}")],
    ),
    base.APIRule(
        name="project_quotas:put",
        check_str=("True:%(enforce_new_defaults)s and rule:system_admin"),
        description="Create or update the configured project quotas for the project with the specified UUID.",
        scope_types=["system"],
        operations=[Operation(method="PUT", path="/v1/project-quotas/{uuid}")],
    ),
    base.APIRule(
        name="project_quotas:delete",
        check_str=("True:%(enforce_new_defaults)s and rule:system_admin"),
        description="Delete the project quotas configuration for the project with the requested UUID.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/v1/quotas}")],
    ),
    base.APIRule(
        name="secret_meta:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private) or rule:secret_acl_read)"),
        description="metadata/: Lists a secrets user-defined metadata. || metadata/{key}: Retrieves a secrets user-added metadata.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/secrets/{secret-id}/metadata"), Operation(method="GET", path="/v1/secrets/{secret-id}/metadata/{meta-key}")],
    ),
    base.APIRule(
        name="secret_meta:post",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="Adds a new key/value pair to the secrets user-defined metadata.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/secrets/{secret-id}/metadata/{meta-key}")],
    ),
    base.APIRule(
        name="secret_meta:put",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="metadata/: Sets the user-defined metadata for a secret || metadata/{key}: Updates an existing key/value pair in the secrets user-defined metadata.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v1/secrets/{secret-id}/metadata"), Operation(method="PUT", path="/v1/secrets/{secret-id}/metadata/{meta-key}")],
    ),
    base.APIRule(
        name="secret_meta:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="Delete secret user-defined metadata by key.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/secrets/{secret-id}/metadata/{meta-key}")],
    ),
    base.APIRule(
        name="secret:decrypt",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private) or rule:secret_acl_read)"),
        description="Retrieve a secrets payload.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/secrets/{uuid}/payload")],
    ),
    base.APIRule(
        name="secret:get",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private) or rule:secret_acl_read)"),
        description="Retrieves a secrets metadata.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/secrets/{secret-id}")],
    ),
    base.APIRule(
        name="secret:put",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="Add the payload to an existing metadata-only secret.",
        scope_types=["project"],
        operations=[Operation(method="PUT", path="/v1/secrets/{secret-id}")],
    ),
    base.APIRule(
        name="secret:delete",
        check_str=("True:%(enforce_new_defaults)s and (rule:secret_project_admin or (rule:secret_project_member and rule:secret_owner) or (rule:secret_project_member and rule:secret_is_not_private))"),
        description="Delete a secret by uuid.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/secrets/{secret-id}")],
    ),
    base.APIRule(
        name="secrets:post",
        check_str=("True:%(enforce_new_defaults)s and (role:member or role:_member_)"),
        description="Creates a Secret entity.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/secrets")],
    ),
    base.APIRule(
        name="secrets:get",
        check_str=("True:%(enforce_new_defaults)s and (role:member or role:_member_)"),
        description="Lists a projects secrets.",
        scope_types=["project"],
        operations=[Operation(method="GET", path="/v1/secrets")],
    ),
    base.APIRule(
        name="secretstores:get",
        check_str=("True:%(enforce_new_defaults)s and role:reader"),
        description="Get list of available secret store backends.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/secret-stores")],
    ),
    base.APIRule(
        name="secretstores:get_global_default",
        check_str=("True:%(enforce_new_defaults)s and role:reader"),
        description="Get a reference to the secret store that is used as default secret store backend for the deployment.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/secret-stores/global-default")],
    ),
    base.APIRule(
        name="secretstores:get_preferred",
        check_str=("True:%(enforce_new_defaults)s and role:reader"),
        description="Get a reference to the preferred secret store if assigned previously.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/secret-stores/preferred")],
    ),
    base.APIRule(
        name="secretstore_preferred:post",
        check_str=("True:%(enforce_new_defaults)s and role:admin"),
        description="Set a secret store backend to be preferred store backend for their project.",
        scope_types=["project"],
        operations=[Operation(method="POST", path="/v1/secret-stores/{ss-id}/preferred")],
    ),
    base.APIRule(
        name="secretstore_preferred:delete",
        check_str=("True:%(enforce_new_defaults)s and role:admin"),
        description="Remove preferred secret store backend setting for their project.",
        scope_types=["project"],
        operations=[Operation(method="DELETE", path="/v1/secret-stores/{ss-id}/preferred")],
    ),
    base.APIRule(
        name="secretstore:get",
        check_str=("True:%(enforce_new_defaults)s and role:reader"),
        description="Get details of secret store by its ID.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/secret-stores/{ss-id}")],
    ),
    base.APIRule(
        name="transport_key:get",
        check_str=("True:%(enforce_new_defaults)s and role:reader"),
        description="Get a specific transport key.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/transport_keys/{key-id}}")],
    ),
    base.APIRule(
        name="transport_key:delete",
        check_str=("True:%(enforce_new_defaults)s and rule:system_admin"),
        description="Delete a specific transport key.",
        scope_types=["system"],
        operations=[Operation(method="DELETE", path="/v1/transport_keys/{key-id}")],
    ),
    base.APIRule(
        name="transport_keys:get",
        check_str=("True:%(enforce_new_defaults)s and role:reader"),
        description="Get a list of all transport keys.",
        scope_types=["project", "system"],
        operations=[Operation(method="GET", path="/v1/transport_keys")],
    ),
    base.APIRule(
        name="transport_keys:post",
        check_str=("True:%(enforce_new_defaults)s and rule:system_admin"),
        description="Create a new transport key.",
        scope_types=["system"],
        operations=[Operation(method="POST", path="/v1/transport_keys")],
    ),
)

__all__ = ("list_rules",)
