# Copyright 2021 99cloud
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

"""Domain manager support: domain-scoped token in the session, profile, policies and config."""

from unittest.mock import Mock, patch

import pytest

from skyline_apiserver import schemas
from skyline_apiserver.api.v1 import login as login_api, policy as policy_api
from skyline_apiserver.config import openstack as openstack_config
from skyline_apiserver.core import security

DOMAIN = {"id": "d0m41n", "name": "acme"}
PROJECT = {"id": "pr0j3ct", "name": "main", "domain": DOMAIN}
USER = {"id": "u53r", "name": "ana", "domain": DOMAIN}
PROJECT_ROLES = [{"id": "r1", "name": "member"}, {"id": "r2", "name": "reader"}]
DOMAIN_ROLES = [{"id": "r3", "name": "manager"}, {"id": "r1", "name": "member"}]


def _token_data(scope: dict, roles: list, expires: str = "2030-01-01T00:00:00.000000Z") -> dict:
    return {"token": {"user": USER, "roles": roles, "expires_at": expires, **scope}}


def _profile(domain_scope_token=None, with_domain=True) -> schemas.Profile:
    kwargs = {}
    if domain_scope_token:
        kwargs = {
            "domain_scope_token": domain_scope_token,
            "domain": DOMAIN if with_domain else None,
            "domain_roles": DOMAIN_ROLES,
            "domain_scope_token_exp": "2030-01-01T00:00:00.000000Z",
        }
    return schemas.Profile(
        keystone_token="ptok",
        region="RegionOne",
        exp=1,
        uuid="uuid",
        project=PROJECT,
        user=USER,
        roles=PROJECT_ROLES,
        keystone_token_exp="2030-01-01T00:00:00.000000Z",
        version="test",
        **kwargs,
    )


class TestSessionPayload:
    def test_payload_carries_domain_scope_token(self):
        payload = schemas.Payload(
            keystone_token="ptok", region="r", exp=1, uuid="u", domain_scope_token="dtok"
        )
        assert payload.toDict()["domain_scope_token"] == "dtok"

    def test_payload_without_domain_scope_token_is_backward_compatible(self):
        payload = schemas.Payload(keystone_token="ptok", region="r", exp=1, uuid="u")
        assert payload.toDict()["domain_scope_token"] is None

    def test_profile_to_payload_keeps_domain_scope_token(self):
        profile = _profile(domain_scope_token="dtok")
        assert profile.toPayLoad().domain_scope_token == "dtok"

    @patch("skyline_apiserver.core.security.CONF")
    @patch("skyline_apiserver.core.security.jwt")
    def test_parse_access_token_reads_optional_domain_scope_token(self, mock_jwt, _conf):
        mock_jwt.decode.return_value = {
            "keystone_token": "ptok",
            "region": "r",
            "exp": 1,
            "uuid": "u",
        }
        assert security.parse_access_token("jwt").domain_scope_token is None
        mock_jwt.decode.return_value["domain_scope_token"] = "dtok"
        assert security.parse_access_token("jwt").domain_scope_token == "dtok"


class TestGenerateProfile:
    @patch("skyline_apiserver.core.security.CONF")
    @patch("skyline_apiserver.core.security.get_system_session")
    @patch("skyline_apiserver.core.security.utils.keystone_client")
    def test_domain_scoped_token_fills_domain_fields(self, mock_kc, _session, mock_conf):
        mock_conf.openstack.base_domains = []
        mock_conf.default.access_token_expire = 3600
        mock_kc.return_value.tokens.get_token_data.side_effect = [
            _token_data({"project": PROJECT}, PROJECT_ROLES),
            _token_data({"domain": DOMAIN}, DOMAIN_ROLES),
        ]
        profile = security.generate_profile("ptok", "RegionOne", domain_scope_token="dtok")
        assert profile.domain_scope_token == "dtok"
        assert profile.domain.id == DOMAIN["id"]
        assert [r.name for r in profile.domain_roles] == ["manager", "member"]
        assert profile.domain_scope_token_exp == "2030-01-01T00:00:00.000000Z"
        # project scope untouched
        assert profile.project.id == PROJECT["id"]
        assert [r.name for r in profile.roles] == ["member", "reader"]

    @patch("skyline_apiserver.core.security.CONF")
    @patch("skyline_apiserver.core.security.get_system_session")
    @patch("skyline_apiserver.core.security.utils.keystone_client")
    def test_unusable_domain_scoped_token_is_dropped_silently(self, mock_kc, _session, mock_conf):
        mock_conf.openstack.base_domains = []
        mock_conf.default.access_token_expire = 3600
        mock_kc.return_value.tokens.get_token_data.side_effect = [
            _token_data({"project": PROJECT}, PROJECT_ROLES),
            Exception("token revoked"),
        ]
        profile = security.generate_profile("ptok", "RegionOne", domain_scope_token="dtok")
        assert profile.domain_scope_token is None
        assert profile.domain is None
        assert profile.domain_roles is None
        assert profile.project.id == PROJECT["id"]

    @patch("skyline_apiserver.core.security.CONF")
    @patch("skyline_apiserver.core.security.get_system_session")
    @patch("skyline_apiserver.core.security.utils.keystone_client")
    def test_no_domain_scoped_token_means_no_extra_keystone_call(
        self, mock_kc, _session, mock_conf
    ):
        mock_conf.openstack.base_domains = []
        mock_conf.default.access_token_expire = 3600
        mock_kc.return_value.tokens.get_token_data.return_value = _token_data(
            {"project": PROJECT}, PROJECT_ROLES
        )
        profile = security.generate_profile("ptok", "RegionOne")
        assert profile.domain_scope_token is None
        assert mock_kc.return_value.tokens.get_token_data.call_count == 1


class TestLoginDomainScope:
    @staticmethod
    def _domain(name, id_, enabled=True):
        d = Mock()
        d.name = name
        d.id = id_
        d.enabled = enabled
        return d

    @patch("skyline_apiserver.api.v1.login.get_domain_scope_token", return_value="dtok")
    @patch("skyline_apiserver.api.v1.login.get_scope_domains")
    def test_user_with_domain_assignment_gets_token_for_own_domain(
        self, mock_domains, mock_token
    ):
        mock_domains.return_value = [self._domain("other", "o1"), self._domain("acme", "d0m41n")]
        assert login_api._get_domain_scope_token("utok", "RegionOne", "acme") == "dtok"
        mock_token.assert_called_once_with(
            keystone_token="utok", region="RegionOne", domain_id="d0m41n", original_ip=None
        )

    @patch("skyline_apiserver.api.v1.login.get_domain_scope_token", return_value="dtok")
    @patch("skyline_apiserver.api.v1.login.get_scope_domains")
    def test_user_without_domain_assignment_gets_none(self, mock_domains, mock_token):
        mock_domains.return_value = []
        assert login_api._get_domain_scope_token("utok", "RegionOne", "acme") is None
        mock_token.assert_not_called()

    @patch("skyline_apiserver.api.v1.login.get_domain_scope_token", return_value="dtok")
    @patch("skyline_apiserver.api.v1.login.get_scope_domains")
    def test_assignment_only_on_another_domain_gets_none(self, mock_domains, mock_token):
        mock_domains.return_value = [self._domain("other", "o1")]
        assert login_api._get_domain_scope_token("utok", "RegionOne", "acme") is None
        mock_token.assert_not_called()

    @patch("skyline_apiserver.api.v1.login.get_domain_scope_token", return_value="dtok")
    @patch("skyline_apiserver.api.v1.login.get_scope_domains")
    def test_disabled_domain_is_ignored(self, mock_domains, mock_token):
        mock_domains.return_value = [self._domain("acme", "d0m41n", enabled=False)]
        assert login_api._get_domain_scope_token("utok", "RegionOne", "acme") is None

    @patch("skyline_apiserver.api.v1.login.get_scope_domains", side_effect=Exception("boom"))
    def test_keystone_failure_never_blocks_login(self, _mock_domains):
        assert login_api._get_domain_scope_token("utok", "RegionOne", "acme") is None

    @patch("skyline_apiserver.api.v1.login.CONF")
    def test_config_exposes_domain_manager_roles(self, mock_conf):
        mock_conf.openstack.user_default_domain = "Default"
        mock_conf.openstack.default_region = "RegionOne"
        mock_conf.openstack.domain_manager_roles = ["manager", "domain_admin"]
        config = login_api.get_config(Mock())
        assert config.domain_manager_roles == ["manager", "domain_admin"]


class TestPolicyDomainScope:
    def test_default_domain_manager_roles(self):
        assert openstack_config.domain_manager_roles.default == ["manager"]

    @patch("skyline_apiserver.api.v1.policy.CONF")
    def test_domain_target_points_everything_to_the_domain(self, mock_conf):
        mock_conf.openstack.enforce_new_defaults = True
        target = policy_api._generate_domain_target(_profile(domain_scope_token="dtok"))
        for key in (
            "target.user.domain_id",
            "target.project.domain_id",
            "target.domain.id",
            "target.domain_id",
            "target.role.domain_id",
            "target.group.domain_id",
            "domain_id",
        ):
            assert target[key] == DOMAIN["id"]
        assert target["target.role.name"] == "member"
        assert target["user_id"] == USER["id"]

    def test_no_domain_scoped_token_means_no_domain_context(self):
        assert policy_api._domain_user_context(_profile()) is None
        assert policy_api._domain_user_context(_profile("dtok", with_domain=False)) is None

    @patch("skyline_apiserver.policy.base.CONF")
    @patch("skyline_apiserver.api.v1.policy.CONF")
    @patch("skyline_apiserver.api.v1.policy.Session")
    @patch("skyline_apiserver.api.v1.policy.Token")
    @patch("skyline_apiserver.api.v1.policy.get_system_session")
    @patch("skyline_apiserver.api.v1.policy.get_endpoint", return_value="http://ks/v3")
    def test_domain_context_keeps_domain_scope_and_nested_token_creds(
        self, _endpoint, _system, mock_token, mock_session, mock_conf, mock_base_conf
    ):
        mock_conf.default.cafile = ""
        mock_base_conf.openstack.system_admin_roles = ["admin"]
        mock_base_conf.openstack.system_reader_roles = ["system_reader"]
        access = Mock()
        access.domain_id = DOMAIN["id"]
        access.role_names = ["manager", "member", "reader"]
        access.system = None
        mock_session.return_value.auth.get_auth_ref.return_value = access

        context = policy_api._domain_user_context(_profile(domain_scope_token="dtok"))

        # re-auth must ask for the domain scope, otherwise Keystone re-scopes to the project
        mock_token.assert_called_once_with("http://ks/v3", "dtok", domain_id=DOMAIN["id"])
        assert context["domain_id"] == DOMAIN["id"]
        assert context["roles"] == ["manager", "member", "reader"]
        # oslo.policy resolves ``token.domain.id`` through nested lookups
        assert context["token"]["domain"]["id"] == DOMAIN["id"]

    def test_authorize_falls_back_to_domain_scope_for_keystone_only(self):
        enforcer = Mock()
        enforcer.authorize.side_effect = lambda rule, target, ctx: ctx is DOMAIN_CTX
        allowed = policy_api._authorize(
            "keystone", enforcer, "identity:create_user", {}, PROJECT_CTX, {}, DOMAIN_CTX
        )
        assert allowed is True
        enforcer.authorize.reset_mock()
        allowed = policy_api._authorize(
            "nova", enforcer, "os_compute_api:servers:create", {}, PROJECT_CTX, {}, DOMAIN_CTX
        )
        assert allowed is False
        enforcer.authorize.assert_called_once()

    def test_authorize_without_domain_context_is_unchanged(self):
        enforcer = Mock()
        enforcer.authorize.return_value = False
        allowed = policy_api._authorize(
            "keystone", enforcer, "identity:create_user", {}, PROJECT_CTX, None, None
        )
        assert allowed is False
        enforcer.authorize.assert_called_once()


PROJECT_CTX = object()
DOMAIN_CTX = object()


@pytest.fixture(autouse=True)
def _no_network():
    """Guard: nothing here may reach a real Keystone."""
    yield
