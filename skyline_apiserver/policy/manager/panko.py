# flake8: noqa
# fmt: off

from . import base

list_rules = (
    base.Rule(
        name="context_is_admin",
        check_str=("role:admin"),
        description="No description",
    ),
    base.APIRule(
        name="segregation",
        check_str=("role:admin and system_scope:all"),
        description="Return the user and project the requestshould be limited to",
        scope_types=["system"],
        operations=[{"method": "GET", "path": "/v2/events"}, {"method": "GET", "path": "/v2/events/{message_id}"}],
    ),
    base.APIRule(
        name="telemetry:events:index",
        check_str=(""),
        description="Return all events matching the query filters.",
        scope_types=["system", "project"],
        operations=[{"method": "GET", "path": "/v2/events"}],
    ),
    base.APIRule(
        name="telemetry:events:show",
        check_str=(""),
        description="Return a single event with the given message id.",
        scope_types=["system", "project"],
        operations=[{"method": "GET", "path": "/v2/events/{message_id}"}],
    ),
)

__all__ = ("list_rules",)
