# Copyright 2025 99cloud
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

from __future__ import annotations

import six
from oslo_config import cfg
from oslo_context import context
from oslo_log import log
from oslo_utils import timeutils

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class RequestContext(context.RequestContext):
    def __init__(
        self,
        user_id=None,
        project_id=None,
        is_admin=False,
        project_name=None,
        timestamp=None,
        user_domain_id=None,
        project_domain_id=None,
        **kwargs,
    ):
        kwargs.setdefault("user_id", user_id)
        kwargs.setdefault("project_id", project_id)
        kwargs.setdefault("user_domain_id", user_domain_id)
        kwargs.setdefault("project_domain_id", project_domain_id)

        super(RequestContext, self).__init__(**kwargs)
        self.project_name = project_name

        if not timestamp:
            timestamp = timeutils.utcnow()
        elif isinstance(timestamp, six.string_types):
            timestamp = timeutils.parse_isotime(timestamp)
        self.timestamp = timestamp

        self.is_admin = is_admin
        # Note: policy check functions are not available in skyline-apiserver
        # so we'll rely on the roles passed in kwargs
        if not self.is_admin and "admin" in self.roles:
            self.is_admin = True
        elif self.is_admin and "admin" not in self.roles:
            self.roles.append("admin")

    def to_dict(self):
        result = super(RequestContext, self).to_dict()
        result["user_id"] = self.user_id
        result["project_id"] = self.project_id
        result["project_name"] = self.project_name
        result["domain_id"] = self.domain_id
        result["timestamp"] = self.timestamp.isoformat()
        result["request_id"] = self.request_id
        return result

    @classmethod
    def from_dict(cls, values):
        return cls(
            user_id=values.get("user_id"),
            project_id=values.get("project_id"),
            project_name=values.get("project_name"),
            domain_id=values.get("domain_id"),
            read_deleted=values.get("read_deleted"),
            remote_address=values.get("remote_address"),
            timestamp=values.get("timestamp"),
            quota_class=values.get("quota_class"),
            service_catalog=values.get("service_catalog"),
            request_id=values.get("request_id"),
            global_request_id=values.get("global_request_id"),
            is_admin=values.get("is_admin"),
            roles=values.get("roles"),
            auth_token=values.get("auth_token"),
            user_domain_id=values.get("user_domain"),
            project_domain_id=values.get("project_domain"),
            user_domain=values.get("user_domain"),
            project_domain=values.get("project_domain"),
        )

    def authorize(self, action, target=None, target_obj=None, fatal=True):
        """Verify that the given action is valid on the target in this context.

        :param action: string representing the action to be checked.
        :param target: dictionary representing the object of the action
            for object creation this should be a dictionary representing the
            location of the object e.g. ``{'project_id': context.project_id}``.
            If None, then this default target will be considered:
            {'project_id': self.project_id, 'user_id': self.user_id}
        :param target_obj: dictionary representing the object which will be
            used to update target.
        :param fatal: if False, will return False when an
            exception.PolicyNotAuthorized occurs.

        :raises skyline_apiserver.exception.NotAuthorized: if verification fails and fatal
            is True.

        :return: returns a non-False value (not necessarily "True") if
            authorized and False if not authorized and fatal is False.
        """
        if target is None:
            target = {"project_id": self.project_id, "user_id": self.user_id}
        target.update(target_obj or {})

        # Note: skyline-apiserver doesn't have policy.authorize function
        # For now, we'll just return True for admin users
        if self.is_admin:
            return True

        # For non-admin users, check if they have access to the target project
        if target.get("project_id") == self.project_id:
            return True

        if fatal:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action {action} not authorized",
            )
        return False

    def to_policy_values(self):
        policy = super(RequestContext, self).to_policy_values()

        policy["is_admin"] = self.is_admin

        return policy

    @property
    def is_system_reader(self):
        # Note: skyline-apiserver doesn't have policy.check_is_system_reader
        # For now, we'll check if user has reader role
        return "reader" in self.roles

    @property
    def is_system_reader_with_no_admin(self):
        if not self.is_admin:
            return self.is_system_reader
        return False
