# flake8: noqa

from . import base

list_rules = (
    base.Rule(
        name="context_is_admin",
        check_str=("role:admin"),
        description="Decides what is required for the 'is_admin:True' check to succeed.",
    ),
    base.Rule(
        name="admin_or_owner",
        check_str=(
            "is_admin:True or (role:admin and is_admin_project:True) or project_id:%(project_id)s"
        ),
        description="Default rule for most non-Admin APIs.",
    ),
    base.Rule(
        name="admin_api",
        check_str=("is_admin:True or (role:admin and is_admin_project:True)"),
        description="Default rule for most Admin APIs.",
    ),
    base.Rule(
        name="system_or_domain_or_project_admin",
        check_str=(
            "(role:admin and system_scope:all) or (role:admin and domain_id:%(domain_id)s) or (role:admin and project_id:%(project_id)s)"
        ),
        description="Default rule for admins of cloud, domain or a project.",
    ),
    base.APIRule(
        name="volume:attachment_create",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create attachment.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/attachments"}],
    ),
    base.APIRule(
        name="volume:attachment_update",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update attachment.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/attachments/{attachment_id}"}],
    ),
    base.APIRule(
        name="volume:attachment_delete",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete attachment.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/attachments/{attachment_id}"}],
    ),
    base.APIRule(
        name="volume:attachment_complete",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Mark a volume attachment process as completed (in-use)",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/attachments/{attachment_id}/action (os-complete)"},
        ],
    ),
    base.APIRule(
        name="volume:multiattach_bootable_volume",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Allow multiattach of bootable volumes.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/attachments"}],
    ),
    base.APIRule(
        name="message:get_all",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List messages.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/messages"}],
    ),
    base.APIRule(
        name="message:get",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show message.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/messages/{message_id}"}],
    ),
    base.APIRule(
        name="message:delete",
        check_str=("rule:admin_or_owner"),
        basic_check_str=("role:admin"),
        description="Delete message.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/messages/{message_id}"}],
    ),
    base.APIRule(
        name="clusters:get_all",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List clusters.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/clusters"},
            {"method": "GET", "path": "/clusters/detail"},
        ],
    ),
    base.APIRule(
        name="clusters:get",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="Show cluster.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/clusters/{cluster_id}"}],
    ),
    base.APIRule(
        name="clusters:update",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Update cluster.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/clusters/{cluster_id}"}],
    ),
    base.APIRule(
        name="workers:cleanup",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Clean up workers.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/workers/cleanup"}],
    ),
    base.APIRule(
        name="volume:get_snapshot_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show snapshot's metadata or one specified metadata with a given key.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/snapshots/{snapshot_id}/metadata"},
            {"method": "GET", "path": "/snapshots/{snapshot_id}/metadata/{key}"},
        ],
    ),
    base.APIRule(
        name="volume:update_snapshot_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update snapshot's metadata or one specified metadata with a given key.",
        scope_types=["project"],
        operations=[
            {"method": "PUT", "path": "/snapshots/{snapshot_id}/metadata"},
            {"method": "PUT", "path": "/snapshots/{snapshot_id}/metadata/{key}"},
        ],
    ),
    base.APIRule(
        name="volume:delete_snapshot_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete snapshot's specified metadata with a given key.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/snapshots/{snapshot_id}/metadata/{key}"}],
    ),
    base.APIRule(
        name="volume:get_all_snapshots",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List snapshots.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/snapshots"},
            {"method": "GET", "path": "/snapshots/detail"},
        ],
    ),
    base.APIRule(
        name="volume_extension:extended_snapshot_attributes",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List or show snapshots with extended attributes.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/snapshots/{snapshot_id}"},
            {"method": "GET", "path": "/snapshots/detail"},
        ],
    ),
    base.APIRule(
        name="volume:create_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create snapshot.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/snapshots"}],
    ),
    base.APIRule(
        name="volume:get_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show snapshot.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/snapshots/{snapshot_id}"}],
    ),
    base.APIRule(
        name="volume:update_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update snapshot.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/snapshots/{snapshot_id}"}],
    ),
    base.APIRule(
        name="volume:delete_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete snapshot.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/snapshots/{snapshot_id}"}],
    ),
    base.APIRule(
        name="volume_extension:snapshot_admin_actions:reset_status",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Reset status of a snapshot.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/snapshots/{snapshot_id}/action (os-reset_status)"},
        ],
    ),
    base.APIRule(
        name="snapshot_extension:snapshot_actions:update_snapshot_status",
        check_str=(""),
        basic_check_str=("@"),
        description="Update database fields of snapshot.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/snapshots/{snapshot_id}/action (update_snapshot_status)",
            },
        ],
    ),
    base.APIRule(
        name="volume_extension:snapshot_admin_actions:force_delete",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Force delete a snapshot.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/snapshots/{snapshot_id}/action (os-force_delete)"},
        ],
    ),
    base.APIRule(
        name="snapshot_extension:list_manageable",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List (in detail) of snapshots which are available to manage.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/manageable_snapshots"},
            {"method": "GET", "path": "/manageable_snapshots/detail"},
        ],
    ),
    base.APIRule(
        name="snapshot_extension:snapshot_manage",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Manage an existing snapshot.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/manageable_snapshots"}],
    ),
    base.APIRule(
        name="snapshot_extension:snapshot_unmanage",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Stop managing a snapshot.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/snapshots/{snapshot_id}/action (os-unmanage)"}],
    ),
    base.APIRule(
        name="backup:get_all",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List backups.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/backups"},
            {"method": "GET", "path": "/backups/detail"},
        ],
    ),
    base.APIRule(
        name="backup:backup_project_attribute",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List backups or show backup with project attributes.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/backups/{backup_id}"},
            {"method": "GET", "path": "/backups/detail"},
        ],
    ),
    base.APIRule(
        name="backup:create",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create backup.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/backups"}],
    ),
    base.APIRule(
        name="backup:get",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show backup.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/backups/{backup_id}"}],
    ),
    base.APIRule(
        name="backup:update",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update backup.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/backups/{backup_id}"}],
    ),
    base.APIRule(
        name="backup:delete",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete backup.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/backups/{backup_id}"}],
    ),
    base.APIRule(
        name="backup:restore",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Restore backup.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/backups/{backup_id}/restore"}],
    ),
    base.APIRule(
        name="backup:backup-import",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Import backup.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/backups/{backup_id}/import_record"}],
    ),
    base.APIRule(
        name="backup:export-import",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Export backup.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/backups/{backup_id}/export_record"}],
    ),
    base.APIRule(
        name="volume_extension:backup_admin_actions:reset_status",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Reset status of a backup.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/backups/{backup_id}/action (os-reset_status)"}],
    ),
    base.APIRule(
        name="volume_extension:backup_admin_actions:force_delete",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Force delete a backup.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/backups/{backup_id}/action (os-force_delete)"}],
    ),
    base.APIRule(
        name="group:get_all",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List groups.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/groups"},
            {"method": "GET", "path": "/groups/detail"},
        ],
    ),
    base.APIRule(
        name="group:create",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create group.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/groups"}],
    ),
    base.APIRule(
        name="group:get",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show group.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/groups/{group_id}"}],
    ),
    base.APIRule(
        name="group:update",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update group.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/groups/{group_id}"}],
    ),
    base.APIRule(
        name="group:group_project_attribute",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List groups or show group with project attributes.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/groups/{group_id}"},
            {"method": "GET", "path": "/groups/detail"},
        ],
    ),
    base.APIRule(
        name="group:group_types_manage",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Create, update or delete a group type.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/group_types/"},
            {"method": "PUT", "path": "/group_types/{group_type_id}"},
            {"method": "DELETE", "path": "/group_types/{group_type_id}"},
        ],
    ),
    base.APIRule(
        name="group:access_group_types_specs",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="Show group type with type specs attributes.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/group_types/{group_type_id}"}],
    ),
    base.APIRule(
        name="group:group_types_specs",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Create, show, update and delete group type spec.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/group_types/{group_type_id}/group_specs/{g_spec_id}"},
            {"method": "GET", "path": "/group_types/{group_type_id}/group_specs"},
            {"method": "POST", "path": "/group_types/{group_type_id}/group_specs"},
            {"method": "PUT", "path": "/group_types/{group_type_id}/group_specs/{g_spec_id}"},
            {"method": "DELETE", "path": "/group_types/{group_type_id}/group_specs/{g_spec_id}"},
        ],
    ),
    base.APIRule(
        name="group:get_all_group_snapshots",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List group snapshots.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/group_snapshots"},
            {"method": "GET", "path": "/group_snapshots/detail"},
        ],
    ),
    base.APIRule(
        name="group:create_group_snapshot",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create group snapshot.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/group_snapshots"}],
    ),
    base.APIRule(
        name="group:get_group_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show group snapshot.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/group_snapshots/{group_snapshot_id}"}],
    ),
    base.APIRule(
        name="group:delete_group_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete group snapshot.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/group_snapshots/{group_snapshot_id}"}],
    ),
    base.APIRule(
        name="group:update_group_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update group snapshot.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/group_snapshots/{group_snapshot_id}"}],
    ),
    base.APIRule(
        name="group:group_snapshot_project_attribute",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List group snapshots or show group snapshot with project attributes.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/group_snapshots/{group_snapshot_id}"},
            {"method": "GET", "path": "/group_snapshots/detail"},
        ],
    ),
    base.APIRule(
        name="group:reset_group_snapshot_status",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Reset status of group snapshot.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/group_snapshots/{g_snapshot_id}/action (reset_status)"},
        ],
    ),
    base.APIRule(
        name="group:delete",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete group.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/groups/{group_id}/action (delete)"}],
    ),
    base.APIRule(
        name="group:reset_status",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Reset status of group.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/groups/{group_id}/action (reset_status)"}],
    ),
    base.APIRule(
        name="group:enable_replication",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Enable replication.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/groups/{group_id}/action (enable_replication)"}],
    ),
    base.APIRule(
        name="group:disable_replication",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Disable replication.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/groups/{group_id}/action (disable_replication)"},
        ],
    ),
    base.APIRule(
        name="group:failover_replication",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Fail over replication.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/groups/{group_id}/action (failover_replication)"},
        ],
    ),
    base.APIRule(
        name="group:list_replication_targets",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="List failover replication.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/groups/{group_id}/action (list_replication_targets)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:qos_specs_manage:get_all",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List qos specs or list all associations.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/qos-specs"},
            {"method": "GET", "path": "/qos-specs/{qos_id}/associations"},
        ],
    ),
    base.APIRule(
        name="volume_extension:qos_specs_manage:get",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="Show qos specs.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/qos-specs/{qos_id}"}],
    ),
    base.APIRule(
        name="volume_extension:qos_specs_manage:create",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Create qos specs.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/qos-specs"}],
    ),
    base.APIRule(
        name="volume_extension:qos_specs_manage:update",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Update qos specs (including updating association).",
        scope_types=["project"],
        operations=[
            {"method": "PUT", "path": "/qos-specs/{qos_id}"},
            {"method": "GET", "path": "/qos-specs/{qos_id}/disassociate_all"},
            {"method": "GET", "path": "/qos-specs/{qos_id}/associate"},
            {"method": "GET", "path": "/qos-specs/{qos_id}/disassociate"},
        ],
    ),
    base.APIRule(
        name="volume_extension:qos_specs_manage:delete",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="delete qos specs or unset one specified qos key.",
        scope_types=["project"],
        operations=[
            {"method": "DELETE", "path": "/qos-specs/{qos_id}"},
            {"method": "PUT", "path": "/qos-specs/{qos_id}/delete_keys"},
        ],
    ),
    base.APIRule(
        name="volume_extension:quota_classes",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Show or update project quota class.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/os-quota-class-sets/{project_id}"},
            {"method": "PUT", "path": "/os-quota-class-sets/{project_id}"},
        ],
    ),
    base.APIRule(
        name="volume_extension:quotas:show",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show project quota (including usage and default).",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/os-quota-sets/{project_id}"},
            {"method": "GET", "path": "/os-quota-sets/{project_id}/default"},
            {"method": "GET", "path": "/os-quota-sets/{project_id}?usage=True"},
        ],
    ),
    base.APIRule(
        name="volume_extension:quotas:update",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Update project quota.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/os-quota-sets/{project_id}"}],
    ),
    base.APIRule(
        name="volume_extension:quotas:delete",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Delete project quota.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/os-quota-sets/{project_id}"}],
    ),
    base.APIRule(
        name="volume_extension:capabilities",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="Show backend capabilities.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/capabilities/{host_name}"}],
    ),
    base.APIRule(
        name="volume_extension:services:index",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List all services.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/os-services"}],
    ),
    base.APIRule(
        name="volume_extension:services:update",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Update service, including failover_host, thaw, freeze, disable, enable, set-log and get-log actions.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/os-services/{action}"}],
    ),
    base.APIRule(
        name="volume:freeze_host",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Freeze a backend host.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/os-services/freeze"}],
    ),
    base.APIRule(
        name="volume:thaw_host",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Thaw a backend host.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/os-services/thaw"}],
    ),
    base.APIRule(
        name="volume:failover_host",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Failover a backend host.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/os-services/failover_host"}],
    ),
    base.APIRule(
        name="scheduler_extension:scheduler_stats:get_pools",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List all backend pools.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/scheduler-stats/get_pools"}],
    ),
    base.APIRule(
        name="volume_extension:hosts",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="List, update or show hosts for a project.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/os-hosts"},
            {"method": "PUT", "path": "/os-hosts/{host_name}"},
            {"method": "GET", "path": "/os-hosts/{host_id}"},
        ],
    ),
    base.APIRule(
        name="limits_extension:used_limits",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show limits with used limit attributes.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/limits"}],
    ),
    base.APIRule(
        name="volume_extension:list_manageable",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List (in detail) of volumes which are available to manage.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/manageable_volumes"},
            {"method": "GET", "path": "/manageable_volumes/detail"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_manage",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Manage existing volumes.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/manageable_volumes"}],
    ),
    base.APIRule(
        name="volume_extension:volume_unmanage",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Stop managing a volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-unmanage)"}],
    ),
    base.APIRule(
        name="volume_extension:types_manage",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Create, update and delete volume type.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/types"},
            {"method": "PUT", "path": "/types"},
            {"method": "DELETE", "path": "/types"},
        ],
    ),
    base.APIRule(
        name="volume_extension:type_get",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Get one specific volume type.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/types/{type_id}"}],
    ),
    base.APIRule(
        name="volume_extension:type_get_all",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List volume types.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/types/"}],
    ),
    base.APIRule(
        name="volume_extension:volume_type_encryption",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Base policy for all volume type encryption type operations.  This can be used to set the policies for a volume type's encryption type create, show, update, and delete actions in one place, or any of those may be set individually using the following policy targets for finer grained control.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/types/{type_id}/encryption"},
            {"method": "PUT", "path": "/types/{type_id}/encryption/{encryption_id}"},
            {"method": "GET", "path": "/types/{type_id}/encryption"},
            {"method": "GET", "path": "/types/{type_id}/encryption/{key}"},
            {"method": "DELETE", "path": "/types/{type_id}/encryption/{encryption_id}"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_type_encryption:create",
        check_str=("rule:volume_extension:volume_type_encryption"),
        basic_check_str=("role:admin"),
        description="Create volume type encryption.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/types/{type_id}/encryption"}],
    ),
    base.APIRule(
        name="volume_extension:volume_type_encryption:get",
        check_str=("rule:volume_extension:volume_type_encryption"),
        basic_check_str=("role:admin or role:reader"),
        description="Show a volume type's encryption type, show an encryption specs item.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/types/{type_id}/encryption"},
            {"method": "GET", "path": "/types/{type_id}/encryption/{key}"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_type_encryption:update",
        check_str=("rule:volume_extension:volume_type_encryption"),
        basic_check_str=("role:admin"),
        description="Update volume type encryption.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/types/{type_id}/encryption/{encryption_id}"}],
    ),
    base.APIRule(
        name="volume_extension:volume_type_encryption:delete",
        check_str=("rule:volume_extension:volume_type_encryption"),
        basic_check_str=("role:admin"),
        description="Delete volume type encryption.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/types/{type_id}/encryption/{encryption_id}"}],
    ),
    base.APIRule(
        name="volume_extension:access_types_extra_specs",
        check_str=("rule:admin_api"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List or show volume type with access type extra specs attribute.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/types/{type_id}"},
            {"method": "GET", "path": "/types"},
        ],
    ),
    base.APIRule(
        name="volume_extension:access_types_qos_specs_id",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List or show volume type with access type qos specs id attribute.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/types/{type_id}"},
            {"method": "GET", "path": "/types"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_type_access",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Volume type access related APIs.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/types"},
            {"method": "GET", "path": "/types/detail"},
            {"method": "GET", "path": "/types/{type_id}"},
            {"method": "POST", "path": "/types"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_type_access:addProjectAccess",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Add volume type access for project.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/types/{type_id}/action (addProjectAccess)"}],
    ),
    base.APIRule(
        name="volume_extension:volume_type_access:removeProjectAccess",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Remove volume type access for project.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/types/{type_id}/action (removeProjectAccess)"}],
    ),
    base.APIRule(
        name="volume:extend",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Extend a volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-extend)"}],
    ),
    base.APIRule(
        name="volume:extend_attached_volume",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Extend a attached volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-extend)"}],
    ),
    base.APIRule(
        name="volume:revert_to_snapshot",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Revert a volume to a snapshot.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (revert)"}],
    ),
    base.APIRule(
        name="volume_extension:volume_admin_actions:reset_status",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Reset status of a volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-reset_status)"}],
    ),
    base.APIRule(
        name="volume:retype",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Retype a volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-retype)"}],
    ),
    base.APIRule(
        name="volume:update_readonly_flag",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update a volume's readonly flag.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-update_readonly_flag)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_admin_actions:force_delete",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Force delete a volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-force_delete)"}],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:upload_public",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Upload a volume to image with public visibility.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-volume_upload_image)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:upload_image",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Upload a volume to image.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-volume_upload_image)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_admin_actions:force_detach",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Force detach a volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-force_detach)"}],
    ),
    base.APIRule(
        name="volume_extension:volume_admin_actions:migrate_volume",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="migrate a volume to a specified host.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-migrate_volume)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_admin_actions:migrate_volume_completion",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Complete a volume migration.",
        scope_types=["project"],
        operations=[
            {
                "method": "POST",
                "path": "/volumes/{volume_id}/action (os-migrate_volume_completion)",
            },
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:initialize_connection",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Initialize volume attachment.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-initialize_connection)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:terminate_connection",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Terminate volume attachment.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-terminate_connection)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:roll_detaching",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Roll back volume status to 'in-use'.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-roll_detaching)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:reserve",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Mark volume as reserved.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-reserve)"}],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:unreserve",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Unmark volume as reserved.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-unreserve)"}],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:begin_detaching",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Begin detach volumes.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-begin_detaching)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:attach",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Add attachment metadata.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-attach)"}],
    ),
    base.APIRule(
        name="volume_extension:volume_actions:detach",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Clear attachment metadata.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/action (os-detach)"}],
    ),
    base.APIRule(
        name="volume:get_all_transfers",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List volume transfer.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/os-volume-transfer"},
            {"method": "GET", "path": "/os-volume-transfer/detail"},
            {"method": "GET", "path": "/volume_transfers"},
            {"method": "GET", "path": "/volume-transfers/detail"},
        ],
    ),
    base.APIRule(
        name="volume:create_transfer",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create a volume transfer.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/os-volume-transfer"},
            {"method": "POST", "path": "/volume_transfers"},
        ],
    ),
    base.APIRule(
        name="volume:get_transfer",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show one specified volume transfer.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/os-volume-transfer/{transfer_id}"},
            {"method": "GET", "path": "/volume-transfers/{transfer_id}"},
        ],
    ),
    base.APIRule(
        name="volume:accept_transfer",
        check_str=(""),
        basic_check_str=("@"),
        description="Accept a volume transfer.",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/os-volume-transfer/{transfer_id}/accept"},
            {"method": "POST", "path": "/volume-transfers/{transfer_id}/accept"},
        ],
    ),
    base.APIRule(
        name="volume:delete_transfer",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete volume transfer.",
        scope_types=["project"],
        operations=[
            {"method": "DELETE", "path": "/os-volume-transfer/{transfer_id}"},
            {"method": "DELETE", "path": "/volume-transfers/{transfer_id}"},
        ],
    ),
    base.APIRule(
        name="volume:get_volume_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show volume's metadata or one specified metadata with a given key.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/volumes/{volume_id}/metadata"},
            {"method": "GET", "path": "/volumes/{volume_id}/metadata/{key}"},
        ],
    ),
    base.APIRule(
        name="volume:create_volume_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create volume metadata.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes/{volume_id}/metadata"}],
    ),
    base.APIRule(
        name="volume:update_volume_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update volume's metadata or one specified metadata with a given key.",
        scope_types=["project"],
        operations=[
            {"method": "PUT", "path": "/volumes/{volume_id}/metadata"},
            {"method": "PUT", "path": "/volumes/{volume_id}/metadata/{key}"},
        ],
    ),
    base.APIRule(
        name="volume:delete_volume_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete volume's specified metadata with a given key.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/volumes/{volume_id}/metadata/{key}"}],
    ),
    base.APIRule(
        name="volume_extension:volume_image_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Volume's image metadata related operation, create, delete, show and list.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/volumes/detail"},
            {"method": "GET", "path": "/volumes/{volume_id}"},
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-set_image_metadata)"},
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-unset_image_metadata)"},
        ],
    ),
    base.APIRule(
        name="volume:update_volume_admin_metadata",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Update volume admin metadata. It's used in `attach` and `os-update_readonly_flag` APIs",
        scope_types=["project"],
        operations=[
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-update_readonly_flag)"},
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-attach)"},
        ],
    ),
    base.APIRule(
        name="volume_extension:types_extra_specs:index",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List type extra specs.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/types/{type_id}/extra_specs"}],
    ),
    base.APIRule(
        name="volume_extension:types_extra_specs:create",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Create type extra specs.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/types/{type_id}/extra_specs"}],
    ),
    base.APIRule(
        name="volume_extension:types_extra_specs:show",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="Show one specified type extra specs.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/types/{type_id}/extra_specs/{extra_spec_key}"}],
    ),
    base.APIRule(
        name="volume_extension:types_extra_specs:update",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Update type extra specs.",
        scope_types=["project"],
        operations=[{"method": "PUT", "path": "/types/{type_id}/extra_specs/{extra_spec_key}"}],
    ),
    base.APIRule(
        name="volume_extension:types_extra_specs:delete",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin"),
        description="Delete type extra specs.",
        scope_types=["project"],
        operations=[
            {"method": "DELETE", "path": "/types/{type_id}/extra_specs/{extra_spec_key}"},
        ],
    ),
    base.APIRule(
        name="volume:create",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes"}],
    ),
    base.APIRule(
        name="volume:create_from_image",
        check_str=(""),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create volume from image.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes"}],
    ),
    base.APIRule(
        name="volume:get",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show volume.",
        scope_types=["project"],
        operations=[{"method": "GET", "path": "/volumes/{volume_id}"}],
    ),
    base.APIRule(
        name="volume:get_all",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List volumes or get summary of volumes.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/volumes"},
            {"method": "GET", "path": "/volumes/detail"},
            {"method": "GET", "path": "/volumes/summary"},
        ],
    ),
    base.APIRule(
        name="volume:update",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Update volume or update a volume's bootable status.",
        scope_types=["project"],
        operations=[
            {"method": "PUT", "path": "/volumes"},
            {"method": "POST", "path": "/volumes/{volume_id}/action (os-set_bootable)"},
        ],
    ),
    base.APIRule(
        name="volume:delete",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Delete volume.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/volumes/{volume_id}"}],
    ),
    base.APIRule(
        name="volume:force_delete",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Force Delete a volume.",
        scope_types=["project"],
        operations=[{"method": "DELETE", "path": "/volumes/{volume_id}"}],
    ),
    base.APIRule(
        name="volume_extension:volume_host_attribute",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader"),
        description="List or show volume with host attribute.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/volumes/{volume_id}"},
            {"method": "GET", "path": "/volumes/detail"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_tenant_attribute",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="List or show volume with tenant attribute.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/volumes/{volume_id}"},
            {"method": "GET", "path": "/volumes/detail"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_mig_status_attribute",
        check_str=("rule:admin_api"),
        basic_check_str=("role:admin or role:reader or role:admin and project_id:%(project_id)s"),
        description="List or show volume with migration status attribute.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/volumes/{volume_id}"},
            {"method": "GET", "path": "/volumes/detail"},
        ],
    ),
    base.APIRule(
        name="volume_extension:volume_encryption_metadata",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:reader or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s or role:reader and project_id:%(project_id)s"
        ),
        description="Show volume's encryption metadata.",
        scope_types=["project"],
        operations=[
            {"method": "GET", "path": "/volumes/{volume_id}/encryption"},
            {"method": "GET", "path": "/volumes/{volume_id}/encryption/{encryption_key}"},
        ],
    ),
    base.APIRule(
        name="volume:multiattach",
        check_str=("rule:admin_or_owner"),
        basic_check_str=(
            "role:admin or role:admin and project_id:%(project_id)s or role:member and project_id:%(project_id)s"
        ),
        description="Create multiattach capable volume.",
        scope_types=["project"],
        operations=[{"method": "POST", "path": "/volumes"}],
    ),
    base.APIRule(
        name="volume_extension:default_set_or_update",
        check_str=("rule:system_or_domain_or_project_admin"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Set or update default volume type.",
        scope_types=["system"],
        operations=[{"method": "PUT", "path": "/default-types"}],
    ),
    base.APIRule(
        name="volume_extension:default_get",
        check_str=("rule:system_or_domain_or_project_admin"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Get default types.",
        scope_types=["system"],
        operations=[{"method": "GET", "path": "/default-types/{project-id}"}],
    ),
    base.APIRule(
        name="volume_extension:default_get_all",
        check_str=("role:admin and system_scope:all"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Get all default types. WARNING: Changing this might open up too much information regarding cloud deployment.",
        scope_types=["system"],
        operations=[{"method": "GET", "path": "/default-types/"}],
    ),
    base.APIRule(
        name="volume_extension:default_unset",
        check_str=("rule:system_or_domain_or_project_admin"),
        basic_check_str=("role:admin or role:admin and project_id:%(project_id)s"),
        description="Unset default type.",
        scope_types=["system"],
        operations=[{"method": "DELETE", "path": "/default-types/{project-id}"}],
    ),
)

__all__ = ("list_rules",)
