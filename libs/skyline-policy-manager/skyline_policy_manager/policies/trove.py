from . import base

list_rules = (
    base.Rule(
        name="admin",
        check_str=("role:admin or is_admin:True"),
        description="Must be an administrator.",
    ),
    base.Rule(
        name="admin_or_owner",
        check_str=("rule:admin or tenant:%(tenant)s"),
        description="Must be an administrator or owner of the object.",
    ),
    base.Rule(
        name="default",
        check_str=("rule:admin_or_owner"),
        description="Must be an administrator or owner of the object.",
    ),
    base.APIRule(
        name="trove:instance:create",
        check_str=("rule:admin_or_owner"),
        description="Create a database instance.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/instances"}],
    ),
    base.APIRule(
        name="trove:instance:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete a database instance.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/instances/{instance_id}"}],
    ),
    base.APIRule(
        name="trove:instance:force_delete",
        check_str=("rule:admin_or_owner"),
        description="Forcibly delete a database instance.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/instances/{instance_id}"}],
    ),
    base.APIRule(
        name="trove:instance:index",
        check_str=("rule:admin_or_owner"),
        description="List database instances.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/instances"}],
    ),
    base.APIRule(
        name="trove:instance:detail",
        check_str=("rule:admin_or_owner"),
        description="List database instances with details.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/instances/detail"}],
    ),
    base.APIRule(
        name="trove:instance:show",
        check_str=("rule:admin_or_owner"),
        description="Get details of a specific database instance.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}"}],
    ),
    base.APIRule(
        name="trove:instance:update",
        check_str=("rule:admin_or_owner"),
        description="Update a database instance to attach/detach configuration",
        scope_types=["project"],
        operations=[
            {"method": "PUT", "path": "/v1.0/{account_id}/instances/{instance_id}"},
            {"method": "POST", "path": "/v1.0/{account_id}/instances"},
        ],
    ),
    base.APIRule(
        name="trove:instance:edit",
        check_str=("rule:admin_or_owner"),
        description="Updates the instance to set or unset one or more attributes.",
        scope_types=["project"],
        operations=[{"method": "PATCH", "path": "/v1.0/{account_id}/instances/{instance_id}"}],
    ),
    base.APIRule(
        name="trove:instance:restart",
        check_str=("rule:admin_or_owner"),
        description="Restart a database instance.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/v1.0/{account_id}/instances/{instance_id}/action (restart)",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:resize_volume",
        check_str=("rule:admin_or_owner"),
        description="Resize a database instance volume.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/v1.0/{account_id}/instances/{instance_id}/action (resize)",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:resize_flavor",
        check_str=("rule:admin_or_owner"),
        description="Resize a database instance flavor.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/v1.0/{account_id}/instances/{instance_id}/action (resize)",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:reset_status",
        check_str=("rule:admin"),
        description="Reset the status of a database instance to ERROR.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/v1.0/{account_id}/instances/{instance_id}/action (reset_status)",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:promote_to_replica_source",
        check_str=("rule:admin_or_owner"),
        description="Promote instance to replica source.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/v1.0/{account_id}/instances/{instance_id}/action"
                + "(promote_to_replica_source)",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:eject_replica_source",
        check_str=("rule:admin_or_owner"),
        description="Eject the replica source from its replica set.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/v1.0/{account_id}/instances/{instance_id}/action (eject_replica_source)",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:configuration",
        check_str=("rule:admin_or_owner"),
        description="Get the default configuration template applied to the instance.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/configuration"},
        ],
    ),
    base.APIRule(
        name="trove:instance:guest_log_list",
        check_str=("rule:admin_or_owner"),
        description="Get all informations about all logs of a database instance.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/log"}],
    ),
    base.APIRule(
        name="trove:instance:backups",
        check_str=("rule:admin_or_owner"),
        description="Get all backups of a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/backups"},
        ],
    ),
    base.APIRule(
        name="trove:instance:module_list",
        check_str=("rule:admin_or_owner"),
        description="Get informations about modules on a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/modules"},
        ],
    ),
    base.APIRule(
        name="trove:instance:module_apply",
        check_str=("rule:admin_or_owner"),
        description="Apply modules to a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/v1.0/{account_id}/instances/{instance_id}/modules"},
            {"method": "POST", "path": "/v1.0/{account_id}/instances"},
        ],
    ),
    base.APIRule(
        name="trove:instance:module_remove",
        check_str=("rule:admin_or_owner"),
        description="Remove a module from a database instance.",
        scope_types=["project"],
        operations=[
            {
                "method": "DELETE",
                "path": "/v1.0/{account_id}/instances/{instance_id}/modules/{module_id}",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:root:create",
        check_str=("rule:admin_or_owner"),
        description="Enable the root user of a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/v1.0/{account_id}/instances/{instance_id}/root"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:root:delete",
        check_str=("rule:admin_or_owner"),
        description="Disable the root user of a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "DELETE", "path": "/v1.0/{account_id}/instances/{instance_id}/root"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:root:index",
        check_str=("rule:admin_or_owner"),
        description="Show whether the root user of a database instance has been ever enabled.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/root"}],
    ),
    base.APIRule(
        name="trove:cluster:extension:root:create",
        check_str=("rule:admin_or_owner"),
        description="Enable the root user of the instances in a cluster.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/clusters/{cluster}/root"}],
    ),
    base.APIRule(
        name="trove:cluster:extension:root:delete",
        check_str=("rule:admin_or_owner"),
        description="Enable the root user of the instances in a cluster.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/clusters/{cluster}/root"}],
    ),
    base.APIRule(
        name="trove:cluster:extension:root:index",
        check_str=("rule:admin_or_owner"),
        description="Disable the root of the instances in a cluster.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/clusters/{cluster}/root"}],
    ),
    base.APIRule(
        name="trove:instance:extension:user:create",
        check_str=("rule:admin_or_owner"),
        description="Create users for a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/v1.0/{account_id}/instances/{instance_id}/users"},
            {"method": "POST", "path": "/v1.0/{account_id}/instances"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete a user from a database instance.",
        scope_types=["project"],
        operations=[
            {
                "method": "DELETE",
                "path": "/v1.0/{account_id}/instances/{instance_id}/users/{user}",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user:index",
        check_str=("rule:admin_or_owner"),
        description="Get all users of a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/users"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user:show",
        check_str=("rule:admin_or_owner"),
        description="Get the information of a single user of a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/users/{user}"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user:update",
        check_str=("rule:admin_or_owner"),
        description="Update attributes for a user of a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "PUT", "path": "/v1.0/{account_id}/instances/{instance_id}/users/{user}"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user:update_all",
        check_str=("rule:admin_or_owner"),
        description="Update the password for one or more users a database instance.",
        scope_types=["project"],
        operations=[
            {"method": "PUT", "path": "/v1.0/{account_id}/instances/{instance_id}/users"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user_access:update",
        check_str=("rule:admin_or_owner"),
        description="Grant access for a user to one or more databases.",
        scope_types=["project"],
        operations=[
            {
                "method": "PUT",
                "path": "/v1.0/{account_id}/instances/{instance_id}/users/{user}/databases",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user_access:delete",
        check_str=("rule:admin_or_owner"),
        description="Revoke access for a user to a databases.",
        scope_types=["project"],
        operations=[
            {
                "method": "DELETE",
                "path": "/v1.0/{account_id}/instances/{instance_id}/users/{user}"
                + "/databases/{database}",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:user_access:index",
        check_str=("rule:admin_or_owner"),
        description="Get permissions of a user",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/instances/{instance_id}/users/{user}/databases",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:database:create",
        check_str=("rule:admin_or_owner"),
        description="Create a set of Schemas",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/v1.0/{account_id}/instances/{instance_id}/databases"},
            {"method": "POST", "path": "/v1.0/{account_id}/instances"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:database:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete a schema from a database.",
        scope_types=["project"],
        operations=[
            {
                "method": "DELETE",
                "path": "/v1.0/{account_id}/instances/{instance_id}/databases/{database}",
            },
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:database:index",
        check_str=("rule:admin_or_owner"),
        description="List all schemas from a database.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/instances/{instance_id}/databases"},
        ],
    ),
    base.APIRule(
        name="trove:instance:extension:database:show",
        check_str=("rule:admin_or_owner"),
        description="Get informations of a schema(Currently Not Implemented).",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/instances/{instance_id}/databases/{database}",
            },
        ],
    ),
    base.APIRule(
        name="trove:cluster:create",
        check_str=("rule:admin_or_owner"),
        description="Create a cluster.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/clusters"}],
    ),
    base.APIRule(
        name="trove:cluster:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete a cluster.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/clusters/{cluster}"}],
    ),
    base.APIRule(
        name="trove:cluster:force_delete",
        check_str=("rule:admin_or_owner"),
        description="Forcibly delete a cluster.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/v1.0/{account_id}/clusters/{cluster} (reset-status)"},
        ],
    ),
    base.APIRule(
        name="trove:cluster:index",
        check_str=("rule:admin_or_owner"),
        description="List all clusters",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/clusters"}],
    ),
    base.APIRule(
        name="trove:cluster:show",
        check_str=("rule:admin_or_owner"),
        description="Get informations of a cluster.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/clusters/{cluster}"}],
    ),
    base.APIRule(
        name="trove:cluster:show_instance",
        check_str=("rule:admin_or_owner"),
        description="Get informations of a instance in a cluster.",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/clusters/{cluster}/instances/{instance}",
            },
        ],
    ),
    base.APIRule(
        name="trove:cluster:action",
        check_str=("rule:admin_or_owner"),
        description="Commit an action against a cluster",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/clusters/{cluster}"}],
    ),
    base.APIRule(
        name="trove:cluster:reset-status",
        check_str=("rule:admin"),
        description="Reset the status of a cluster to NONE.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/v1.0/{account_id}/clusters/{cluster} (reset-status)"},
        ],
    ),
    base.APIRule(
        name="trove:backup:create",
        check_str=("rule:admin_or_owner"),
        description="Create a backup of a database instance.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/backups"}],
    ),
    base.APIRule(
        name="trove:backup:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete a backup of a database instance.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/backups/{backup}"}],
    ),
    base.APIRule(
        name="trove:backup:index",
        check_str=("rule:admin_or_owner"),
        description="List all backups.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/backups"}],
    ),
    base.APIRule(
        name="trove:backup:index:all_projects",
        check_str=("role:admin"),
        description="List backups for all the projects.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/backups"}],
    ),
    base.APIRule(
        name="trove:backup:show",
        check_str=("rule:admin_or_owner"),
        description="Get informations of a backup.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/backups/{backup}"}],
    ),
    base.APIRule(
        name="trove:backup_strategy:create",
        check_str=("rule:admin_or_owner"),
        description="Create a backup strategy.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/backup_strategies"}],
    ),
    base.APIRule(
        name="trove:backup_strategy:index",
        check_str=("rule:admin_or_owner"),
        description="List all backup strategies.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/backup_strategies"}],
    ),
    base.APIRule(
        name="trove:backup_strategy:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete backup strategies.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/backup_strategies"}],
    ),
    base.APIRule(
        name="trove:configuration:create",
        check_str=("rule:admin_or_owner"),
        description="Create a configuration group.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/configurations"}],
    ),
    base.APIRule(
        name="trove:configuration:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete a configuration group.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/configurations/{config}"}],
    ),
    base.APIRule(
        name="trove:configuration:index",
        check_str=("rule:admin_or_owner"),
        description="List all configuration groups.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/configurations"}],
    ),
    base.APIRule(
        name="trove:configuration:show",
        check_str=("rule:admin_or_owner"),
        description="Get informations of a configuration group.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/configurations/{config}"}],
    ),
    base.APIRule(
        name="trove:configuration:instances",
        check_str=("rule:admin_or_owner"),
        description="List all instances which a configuration group has be assigned to.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/configurations/{config}/instances"},
        ],
    ),
    base.APIRule(
        name="trove:configuration:update",
        check_str=("rule:admin_or_owner"),
        description="Update a configuration group(the configuration group will be replaced"
        + "completely).",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/v1.0/{account_id}/configurations/{config}"}],
    ),
    base.APIRule(
        name="trove:configuration:edit",
        check_str=("rule:admin_or_owner"),
        description="Patch a configuration group.",
        scope_types=["project"],
        operations=[{"method": "PATCH", "path": "/v1.0/{account_id}/configurations/{config}"}],
    ),
    base.APIRule(
        name="trove:configuration-parameter:index",
        check_str=("rule:admin_or_owner"),
        description="List all parameters bind to a datastore version.",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/datastores/{datastore}/versions/{version}/parameters",
            },
        ],
    ),
    base.APIRule(
        name="trove:configuration-parameter:show",
        check_str=("rule:admin_or_owner"),
        description="Get a paramter of a datastore version.",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/datastores/{datastore}/versions/{version}/parameters"
                + "/{param}",
            },
        ],
    ),
    base.APIRule(
        name="trove:configuration-parameter:index_by_version",
        check_str=("rule:admin_or_owner"),
        description="List all paramters bind to a datastore version by the id of the"
        + "version(datastore is not provided).",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/datastores/versions/{version}/paramters",
            },
        ],
    ),
    base.APIRule(
        name="trove:configuration-parameter:show_by_version",
        check_str=("rule:admin_or_owner"),
        description="Get a paramter of a datastore version by it names and the id of the"
        + "version(datastore is not provided).",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/datastores/versions/{version}/paramters/{param}",
            },
        ],
    ),
    base.APIRule(
        name="trove:datastore:index",
        check_str=(""),
        description="List all datastores.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/datastores"}],
    ),
    base.APIRule(
        name="trove:datastore:show",
        check_str=(""),
        description="Get informations of a datastore.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/datastores/{datastore}"}],
    ),
    base.APIRule(
        name="trove:datastore:delete",
        check_str=("rule:admin"),
        description="Delete a datastore.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/datastores/{datastore}"}],
    ),
    base.APIRule(
        name="trove:datastore:version_show",
        check_str=(""),
        description="Get a version of a datastore by the version id.",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/datastores/{datastore}/versions/{version}",
            },
        ],
    ),
    base.APIRule(
        name="trove:datastore:version_show_by_uuid",
        check_str=(""),
        description="Get a version of a datastore by the version"
        + "id(without providing the datastore id).",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/datastores/versions/{version}"},
        ],
    ),
    base.APIRule(
        name="trove:datastore:version_index",
        check_str=(""),
        description="Get all versions of a datastore.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/v1.0/{account_id}/datastores/{datastore}/versions"},
        ],
    ),
    base.APIRule(
        name="trove:datastore:list_associated_flavors",
        check_str=(""),
        description="List all flavors associated with a datastore version.",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/datastores/{datastore}/versions/{version}/flavors",
            },
        ],
    ),
    base.APIRule(
        name="trove:datastore:list_associated_volume_types",
        check_str=(""),
        description="List all volume-types associated with a datastore version.",
        scope_types=["project"],
        operations=[
            {
                "method": "GET",
                "path": "/v1.0/{account_id}/datastores/{datastore}/versions/{version}"
                + "/volume-types",
            },
        ],
    ),
    base.APIRule(
        name="trove:flavor:index",
        check_str=(""),
        description="List all flavors.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/flavors"}],
    ),
    base.APIRule(
        name="trove:flavor:show",
        check_str=(""),
        description="Get information of a flavor.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/flavors/{flavor}"}],
    ),
    base.APIRule(
        name="trove:limits:index",
        check_str=("rule:admin_or_owner"),
        description="List all absolute and rate limit informations.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/limits"}],
    ),
    base.APIRule(
        name="trove:module:create",
        check_str=("rule:admin_or_owner"),
        description="Create a module.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/v1.0/{account_id}/modules"}],
    ),
    base.APIRule(
        name="trove:module:delete",
        check_str=("rule:admin_or_owner"),
        description="Delete a module.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/v1.0/{account_id}/modules/{module}"}],
    ),
    base.APIRule(
        name="trove:module:index",
        check_str=("rule:admin_or_owner"),
        description="List all modules.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/modules"}],
    ),
    base.APIRule(
        name="trove:module:show",
        check_str=("rule:admin_or_owner"),
        description="Get informations of a module.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/modules/{module}"}],
    ),
    base.APIRule(
        name="trove:module:instances",
        check_str=("rule:admin_or_owner"),
        description="List all instances to which a module is applied.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/v1.0/{account_id}/modules/{module}/instances"}],
    ),
    base.APIRule(
        name="trove:module:update",
        check_str=("rule:admin_or_owner"),
        description="Update a module.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/v1.0/{account_id}/modules/{module}"}],
    ),
    base.APIRule(
        name="trove:module:reapply",
        check_str=("rule:admin_or_owner"),
        description="Reapply a module to all instances.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/v1.0/{account_id}/modules/{module}/instances"}],
    ),
)

__all__ = ("list_rules",)
