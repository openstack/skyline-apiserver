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

from unittest.mock import MagicMock, Mock, patch

import pytest


def _missing_auth_methods(
    receipt="receipt-token",
    required_auth_methods=None,
    methods=None,
):
    from keystoneauth1 import exceptions as ks_exceptions

    response = MagicMock()
    response.headers = {"Openstack-Auth-Receipt": receipt} if receipt else {}
    response.json.return_value = {
        "receipt": {
            "methods": methods or ["password"],
            "expires_at": "2018-07-05T08:39:23.000000Z",
        },
        "required_auth_methods": required_auth_methods or [["password", "totp"]],
    }
    return ks_exceptions.MissingAuthMethods(response)


class TestGetUserRegions:
    """Tests for _get_user_regions function."""

    @patch("skyline_apiserver.api.v1.login.CONF")
    @patch("skyline_apiserver.api.v1.login.generate_session")
    @patch("skyline_apiserver.api.v1.login.utils")
    def test_returns_sorted_unique_region_ids(self, mock_utils, mock_generate_session, mock_conf):
        """Regions should be sorted and deduplicated."""
        mock_conf.openstack.interface_type = "public"
        mock_access = MagicMock()
        mock_access.service_catalog.get_endpoints.return_value = {
            "compute": [{"region_id": "RegionTwo"}, {"region_id": "RegionOne"}],
            "identity": [{"region_id": "RegionOne"}],
        }
        mock_utils.get_access.return_value = mock_access

        mock_profile = MagicMock()
        mock_profile.region = "RegionOne"
        mock_profile.keystone_token = "fake-token"

        # Import inside test to ensure fresh module reference
        from skyline_apiserver.api.v1.login import _get_user_regions

        result = _get_user_regions(mock_profile)

        assert result == ["RegionOne", "RegionTwo"]
        mock_generate_session.assert_called_once_with(mock_profile)

    @patch("skyline_apiserver.api.v1.login.generate_session")
    @patch("skyline_apiserver.api.v1.login.utils")
    def test_empty_on_exception(self, mock_utils, mock_generate_session):
        """Should return empty list on error."""
        mock_utils.get_access.side_effect = Exception("catalog error")

        mock_profile = Mock()
        mock_profile.region = "RegionOne"

        from skyline_apiserver.api.v1.login import _get_user_regions

        result = _get_user_regions(mock_profile)

        assert result == []


class TestPatchProfileDomainName:
    """Tests for domain_name being added to projects in _patch_profile."""

    @patch("skyline_apiserver.api.v1.login.get_endpoints")
    @patch("skyline_apiserver.api.v1.login.get_projects")
    @patch("skyline_apiserver.api.v1.login._get_default_project_id")
    @patch("skyline_apiserver.api.v1.login.get_system_session")
    @patch("skyline_apiserver.api.v1.login._get_user_regions")
    def test_projects_include_domain_name(
        self,
        mock_get_user_regions,
        mock_get_sys_session,
        mock_get_default_project_id,
        mock_get_projects,
        mock_get_endpoints,
    ):
        """Each project dict should include domain_name from i.domain.name."""
        mock_project = MagicMock()
        mock_project.id = "project-uuid-123"
        mock_project.name = "test-project"
        mock_project.enabled = True
        mock_project.domain_id = "domain-uuid-456"
        mock_project.domain.name = "admin"
        mock_project.description = "test desc"

        mock_get_projects.return_value = [mock_project]
        mock_get_endpoints.return_value = {"compute": "/api/openstack/regionone/compute"}
        mock_get_default_project_id.return_value = "project-uuid-123"
        mock_get_user_regions.return_value = ["RegionOne"]

        mock_profile = MagicMock()
        mock_profile.user.id = "user-id"
        mock_profile.region = "RegionOne"
        mock_profile.keystone_token = "keystone-token"

        from skyline_apiserver.api.v1.login import _patch_profile

        result = _patch_profile(mock_profile, "global-request-id")

        assert result.projects is not None
        project_dict = result.projects["project-uuid-123"]
        assert "domain_name" in project_dict
        assert project_dict["domain_name"] == "admin"
        assert project_dict["domain_id"] == "domain-uuid-456"

    @patch("skyline_apiserver.api.v1.login.get_endpoints")
    @patch("skyline_apiserver.api.v1.login.get_projects")
    @patch("skyline_apiserver.api.v1.login._get_default_project_id")
    @patch("skyline_apiserver.api.v1.login.get_system_session")
    @patch("skyline_apiserver.api.v1.login._get_user_regions")
    def test_projects_include_domain_name_from_keystone(
        self,
        mock_get_user_regions,
        mock_get_sys_session,
        mock_get_default_project_id,
        mock_get_projects,
        mock_get_endpoints,
    ):
        """domain_name should come from the Keystone project object's domain.name."""
        mock_project_a = MagicMock()
        mock_project_a.id = "proj-a"
        mock_project_a.name = "project-a"
        mock_project_a.enabled = True
        mock_project_a.domain_id = "domain-a"
        mock_project_a.domain.name = "domainA"
        mock_project_a.description = ""

        mock_project_b = MagicMock()
        mock_project_b.id = "proj-b"
        mock_project_b.name = "project-b"
        mock_project_b.enabled = False
        mock_project_b.domain_id = "domain-b"
        mock_project_b.domain.name = "domainB"
        mock_project_b.description = ""

        mock_get_projects.return_value = [mock_project_a, mock_project_b]
        mock_get_endpoints.return_value = {}
        mock_get_default_project_id.return_value = "proj-a"
        mock_get_user_regions.return_value = ["RegionOne"]

        mock_profile = MagicMock()
        mock_profile.user.id = "user-1"
        mock_profile.region = "RegionOne"
        mock_profile.keystone_token = "token"

        from skyline_apiserver.api.v1.login import _patch_profile

        result = _patch_profile(mock_profile, "req-id")

        assert result.projects is not None
        assert result.projects["proj-a"]["domain_name"] == "domainA"
        assert result.projects["proj-b"]["domain_name"] == "domainB"


class TestSwitchRegion:
    """Tests for switch_region endpoint."""

    @patch("skyline_apiserver.api.v1.login.CONF")
    @patch("skyline_apiserver.api.v1.login.generate_profile")
    @patch("skyline_apiserver.api.v1.login._patch_profile")
    @patch("skyline_apiserver.api.v1.login.deps")
    def test_switch_region_updates_profile_region(
        self, mock_deps, mock_patch_profile, mock_gen_profile, mock_conf
    ):
        """switch_region should generate new profile with target region."""
        mock_conf.default.session_name = "session_id"
        mock_profile = MagicMock()
        mock_profile.keystone_token = "keystone-token-xyz"
        mock_profile.region = "RegionOne"
        mock_profile.projects = {"proj-1": {}}
        mock_profile.regions = ["RegionOne", "RegionTwo"]
        mock_deps.get_profile.return_value = mock_profile

        new_profile = MagicMock()
        mock_gen_profile.return_value = new_profile
        mock_patch_profile.return_value = new_profile

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_header = ""

        from skyline_apiserver.api.v1.login import switch_region

        result = switch_region(
            region="RegionTwo",
            request=mock_request,
            response=mock_response,
            x_openstack_request_id=mock_header,
        )

        mock_gen_profile.assert_called_once_with(
            keystone_token="keystone-token-xyz",
            region="RegionTwo",
        )
        assert result == new_profile

    @patch("skyline_apiserver.api.v1.login.generate_profile")
    @patch("skyline_apiserver.api.v1.login._patch_profile")
    @patch("skyline_apiserver.api.v1.login.deps")
    def test_switch_region_rejects_invalid_region(
        self, mock_deps, mock_patch_profile, mock_gen_profile
    ):
        """Region not in profile.regions should return 401."""
        from fastapi.exceptions import HTTPException

        mock_profile = MagicMock()
        mock_profile.keystone_token = "token"
        mock_profile.region = "RegionOne"
        mock_profile.regions = ["RegionOne"]
        mock_deps.get_profile.return_value = mock_profile

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_header = ""

        from skyline_apiserver.api.v1.login import switch_region

        with pytest.raises(HTTPException) as exc_info:
            switch_region(
                region="RegionTwo",
                request=mock_request,
                response=mock_response,
                x_openstack_request_id=mock_header,
            )

        assert exc_info.value.status_code == 401
        assert "Region not accessible" in exc_info.value.detail
        mock_gen_profile.assert_not_called()

    @patch("skyline_apiserver.api.v1.login.CONF")
    @patch("skyline_apiserver.api.v1.login.generate_profile")
    @patch("skyline_apiserver.api.v1.login._patch_profile")
    @patch("skyline_apiserver.api.v1.login.deps")
    def test_switch_region_no_re_scope(
        self, mock_deps, mock_patch_profile, mock_gen_profile, mock_conf
    ):
        """switch_region should NOT call get_project_scope_token."""
        mock_conf.default.session_name = "session_id"
        mock_profile = MagicMock()
        mock_profile.keystone_token = "token"
        mock_profile.region = "RegionOne"
        mock_profile.projects = {"proj-1": {}}
        mock_profile.regions = ["RegionOne", "RegionTwo"]
        mock_deps.get_profile.return_value = mock_profile

        new_profile = MagicMock()
        mock_gen_profile.return_value = new_profile
        mock_patch_profile.return_value = new_profile

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_header = ""

        with patch("skyline_apiserver.api.v1.login.get_project_scope_token") as mock_scope:
            from skyline_apiserver.api.v1.login import switch_region

            result = switch_region(
                region="RegionTwo",
                request=mock_request,
                response=mock_response,
                x_openstack_request_id=mock_header,
            )
            mock_scope.assert_not_called()
            assert result == new_profile

    @patch("skyline_apiserver.api.v1.login.CONF")
    @patch("skyline_apiserver.api.v1.login.generate_profile")
    @patch("skyline_apiserver.api.v1.login._patch_profile")
    @patch("skyline_apiserver.api.v1.login.deps")
    def test_switch_region_writes_new_cookie(
        self, mock_deps, mock_patch_profile, mock_gen_profile, mock_conf
    ):
        """switch_region should set new JWT cookie in response."""
        mock_conf.default.session_name = "session_id"
        mock_profile = MagicMock()
        mock_profile.keystone_token = "token"
        mock_profile.region = "RegionOne"
        mock_profile.projects = {"proj-1": {}}
        mock_profile.regions = ["RegionOne", "RegionTwo"]
        mock_deps.get_profile.return_value = mock_profile

        new_profile = MagicMock()
        new_profile.exp = 9999999999
        new_profile.toJWTPayload.return_value = "new-jwt-payload"
        mock_gen_profile.return_value = new_profile
        mock_patch_profile.return_value = new_profile

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_header = ""

        from skyline_apiserver.api.v1.login import switch_region

        switch_region(
            region="RegionTwo",
            request=mock_request,
            response=mock_response,
            x_openstack_request_id=mock_header,
        )

        mock_response.set_cookie.assert_called()


class TestSwitchProjectValidation:
    """Tests for switch_project pre-validation."""

    @patch("skyline_apiserver.api.v1.login.CONF")
    @patch("skyline_apiserver.api.v1.login.generate_profile")
    @patch("skyline_apiserver.api.v1.login._patch_profile")
    @patch("skyline_apiserver.api.v1.login.get_project_scope_token")
    @patch("skyline_apiserver.api.v1.login.deps")
    def test_accepts_valid_project(
        self,
        mock_deps,
        mock_scope_token,
        mock_patch,
        mock_gen_profile,
        mock_conf,
    ):
        """Project in profile.projects should succeed."""
        mock_conf.default.session_name = "session_id"
        mock_profile = MagicMock()
        mock_profile.keystone_token = "token"
        mock_profile.region = "RegionOne"
        mock_profile.projects = {"valid-proj": {"name": "proj"}}
        mock_deps.get_profile.return_value = mock_profile

        mock_scope_token.return_value = "new-scoped-token"
        mock_new_profile = MagicMock()
        mock_gen_profile.return_value = mock_new_profile
        mock_patch.return_value = mock_new_profile

        mock_request = MagicMock()
        mock_response = MagicMock()

        from skyline_apiserver.api.v1.login import switch_project

        result = switch_project(
            project_id="valid-proj",
            request=mock_request,
            response=mock_response,
            x_openstack_request_id="",
        )

        mock_scope_token.assert_called_once()
        assert result == mock_new_profile

    @patch("skyline_apiserver.api.v1.login.deps")
    def test_rejects_unknown_project(self, mock_deps):
        """Project not in profile.projects should return 401."""
        from fastapi.exceptions import HTTPException

        mock_profile = MagicMock()
        mock_profile.keystone_token = "token"
        mock_profile.region = "RegionOne"
        mock_profile.projects = {"proj-a": {}, "proj-b": {}}
        mock_deps.get_profile.return_value = mock_profile

        mock_request = MagicMock()
        mock_response = MagicMock()

        from skyline_apiserver.api.v1.login import switch_project

        with pytest.raises(HTTPException) as exc_info:
            switch_project(
                project_id="unknown-project",
                request=mock_request,
                response=mock_response,
                x_openstack_request_id="",
            )

        assert exc_info.value.status_code == 401
        assert "Project not accessible" in exc_info.value.detail

    @patch("skyline_apiserver.api.v1.login.CONF")
    @patch("skyline_apiserver.api.v1.login.deps")
    def test_accepts_when_projects_none(self, mock_deps, mock_conf):
        """If profile.projects is None, allow the request (backward compat)."""
        mock_conf.default.session_name = "session_id"
        mock_profile = MagicMock()
        mock_profile.keystone_token = "token"
        mock_profile.region = "RegionOne"
        mock_profile.projects = None
        mock_deps.get_profile.return_value = mock_profile

        mock_request = MagicMock()
        mock_response = MagicMock()

        with patch("skyline_apiserver.api.v1.login.get_project_scope_token") as mock_scope, patch(
            "skyline_apiserver.api.v1.login.generate_profile"
        ) as mock_gen, patch("skyline_apiserver.api.v1.login._patch_profile") as mock_patch:
            mock_scope.return_value = "new-token"
            mock_gen.return_value = MagicMock()
            mock_patch.return_value = MagicMock()
            from skyline_apiserver.api.v1.login import switch_project

            result = switch_project(
                project_id="any-project",
                request=mock_request,
                response=mock_response,
                x_openstack_request_id="",
            )
            assert result is not None


class TestCredentialSchema:
    """Tests for Credential schema changes."""

    def test_domain_is_optional(self):
        """domain field should be Optional."""
        from skyline_apiserver.schemas import login as schemas

        cred = schemas.Credential(
            username="admin",
            password="password",
        )
        assert cred.domain is None

    def test_region_still_optional(self):
        """region field should still be Optional."""
        from skyline_apiserver.schemas import login as schemas

        cred = schemas.Credential(
            username="admin",
            password="password",
            region=None,
        )
        assert cred.region is None

    def test_full_credential_with_domain(self):
        """Credential with domain should work."""
        from skyline_apiserver.schemas import login as schemas

        cred = schemas.Credential(
            username="admin",
            password="password",
            domain="admin",
        )
        assert cred.domain == "admin"


class TestProfileSchema:
    """Tests for Profile schema new fields."""

    def test_profile_has_regions_field(self):
        """Profile should have optional regions field."""
        from skyline_apiserver.schemas import login as schemas

        profile = schemas.Profile(
            keystone_token="token",
            region="RegionOne",
            exp=9999999999,
            uuid="uuid-123",
            project=schemas.Project(
                id="proj-id",
                name="proj",
                domain=schemas.Domain(id="dom-id", name="domain"),
            ),
            user=schemas.User(
                id="user-id",
                name="user",
                domain=schemas.Domain(id="dom-id", name="domain"),
            ),
            roles=[],
            keystone_token_exp="exp",
            version="1.0.0",
            regions=["RegionOne", "RegionTwo"],
        )
        assert profile.regions == ["RegionOne", "RegionTwo"]

    def test_profile_regions_default_none(self):
        """regions should default to None."""
        from skyline_apiserver.schemas import login as schemas

        profile = schemas.Profile(
            keystone_token="token",
            region="RegionOne",
            exp=9999999999,
            uuid="uuid-123",
            project=schemas.Project(
                id="proj-id",
                name="proj",
                domain=schemas.Domain(id="dom-id", name="domain"),
            ),
            user=schemas.User(
                id="user-id",
                name="user",
                domain=schemas.Domain(id="dom-id", name="domain"),
            ),
            roles=[],
            keystone_token_exp="exp",
            version="1.0.0",
        )
        assert profile.regions is None


class TestConfigSchema:
    """Tests for Config schema new field."""

    def test_config_has_default_region(self):
        """Config should include default_region."""
        from skyline_apiserver.schemas import login as schemas

        cfg = schemas.Config(
            default_domain="Default",
            default_region="RegionOne",
        )
        assert cfg.default_region == "RegionOne"
        assert cfg.default_domain == "Default"


class TestRequiresTotpStep:
    """Tests for TOTP MFA detection helpers."""

    def test_requires_totp_when_receipt_and_totp_rule(self):
        from skyline_apiserver.api.v1.login import _requires_totp_step

        exc = _missing_auth_methods()

        assert _requires_totp_step(exc) is True

    def test_requires_totp_false_for_totp_only_rule(self):
        from skyline_apiserver.api.v1.login import _requires_totp_step

        exc = _missing_auth_methods(required_auth_methods=[["totp"]])

        assert _requires_totp_step(exc) is False

    def test_requires_totp_false_without_receipt(self):
        from skyline_apiserver.api.v1.login import _requires_totp_step

        exc = _missing_auth_methods(receipt=None)

        assert _requires_totp_step(exc) is False

    def test_requires_totp_false_without_totp_in_rules(self):
        from skyline_apiserver.api.v1.login import _requires_totp_step

        exc = _missing_auth_methods(required_auth_methods=[["password", "custom-auth-method"]])

        assert _requires_totp_step(exc) is False


class TestRaiseForMissingAuthMethods:
    """Tests for MissingAuthMethods HTTP translation."""

    def test_raises_totp_required_payload(self):
        from fastapi.exceptions import HTTPException

        from skyline_apiserver.api.v1.login import _raise_for_missing_auth_methods

        exc = _missing_auth_methods(receipt="abc-receipt")

        with pytest.raises(HTTPException) as exc_info:
            _raise_for_missing_auth_methods(exc)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == {
            "totp_required": True,
            "receipt": "abc-receipt",
        }

    def test_raises_generic_message_for_other_mfa(self):
        from fastapi.exceptions import HTTPException

        from skyline_apiserver.api.v1.login import _raise_for_missing_auth_methods

        exc = _missing_auth_methods(required_auth_methods=[["password", "custom-auth-method"]])

        with pytest.raises(HTTPException) as exc_info:
            _raise_for_missing_auth_methods(exc)

        assert exc_info.value.status_code == 401
        assert "try again later" in exc_info.value.detail


class TestIsReceiptAuthError:
    """Tests for receipt expiration / invalid receipt detection."""

    def test_missing_auth_methods_without_receipt(self):
        from skyline_apiserver.api.v1.login import _is_receipt_auth_error

        exc = _missing_auth_methods(receipt=None)

        assert _is_receipt_auth_error(exc) is True

    def test_http_error_with_receipt_expired_code(self):
        from keystoneauth1.exceptions import http

        from skyline_apiserver.api.v1.login import _is_receipt_auth_error

        response = MagicMock()
        response.headers = {}
        response.json.return_value = {
            "error": {
                "code": "auth_receipt_expired",
                "message": "Auth receipt expired",
            }
        }
        exc = http.Unauthorized(response=response)

        assert _is_receipt_auth_error(exc) is True

    def test_unauthorized_without_receipt_signal_is_not_receipt_error(self):
        from keystoneauth1.exceptions import http

        from skyline_apiserver.api.v1.login import _is_receipt_auth_error

        response = MagicMock()
        response.headers = {}
        response.json.return_value = {
            "error": {
                "code": "401",
                "message": "Invalid passcode",
            }
        }
        exc = http.Unauthorized(response=response)

        assert _is_receipt_auth_error(exc) is False


class TestGetProjectsAndUnscopeTokenTotp:
    """Tests for TOTP detection during password authentication."""

    @patch("skyline_apiserver.api.v1.login.KeystoneClient")
    @patch("skyline_apiserver.api.v1.login.Session")
    @patch("skyline_apiserver.api.v1.login.Password")
    @patch("skyline_apiserver.api.v1.login.utils.get_endpoint")
    @patch("skyline_apiserver.api.v1.login.get_system_session")
    @patch("skyline_apiserver.api.v1.login.CONF")
    def test_password_login_raises_totp_required(
        self,
        mock_conf,
        mock_get_system_session,
        mock_get_endpoint,
        mock_password,
        mock_session_cls,
        mock_keystone_client,
    ):
        from fastapi.exceptions import HTTPException

        from skyline_apiserver.api.v1.login import _get_projects_and_unscope_token

        mock_conf.default.cafile = None
        mock_conf.openstack.interface_type = "public"
        mock_get_endpoint.return_value = "http://keystone/v3"

        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get_token.side_effect = _missing_auth_methods(receipt="step-one-receipt")

        with pytest.raises(HTTPException) as exc_info:
            _get_projects_and_unscope_token(
                region="RegionOne",
                domain="Default",
                username="admin",
                password="secret",
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["totp_required"] is True
        assert exc_info.value.detail["receipt"] == "step-one-receipt"
        mock_keystone_client.assert_not_called()


class TestLoginTotpEndpoint:
    """Tests for login_totp endpoint."""

    @patch("skyline_apiserver.api.v1.login._finish_login")
    @patch("skyline_apiserver.api.v1.login._get_totp_session")
    @patch("skyline_apiserver.api.v1.login.CONF")
    def test_login_totp_success(self, mock_conf, mock_get_totp_session, mock_finish_login):
        mock_conf.openstack.default_region = "RegionOne"
        mock_conf.openstack.user_default_domain = "Default"

        mock_session = MagicMock()
        mock_session.get_token.return_value = "unscoped-token"
        mock_get_totp_session.return_value = mock_session

        mock_profile = MagicMock()
        mock_finish_login.return_value = mock_profile

        mock_request = MagicMock()
        mock_response = MagicMock()
        credential = MagicMock()
        credential.region = None
        credential.domain = None
        credential.username = "admin"
        credential.passcode = "123456"
        credential.receipt = "receipt-token"

        from skyline_apiserver.api.v1.login import login_totp

        result = login_totp(
            request=mock_request,
            response=mock_response,
            credential=credential,
            x_openstack_request_id="req-id",
        )

        mock_get_totp_session.assert_called_once_with(
            region="RegionOne",
            domain="Default",
            username="admin",
            passcode="123456",
            receipt="receipt-token",
        )
        mock_finish_login.assert_called_once_with(
            unscope_token="unscoped-token",
            region="RegionOne",
            response=mock_response,
            x_openstack_request_id="req-id",
            project_enabled=True,
        )
        assert result == mock_profile

    @patch("skyline_apiserver.api.v1.login._get_totp_session")
    @patch("skyline_apiserver.api.v1.login.CONF")
    def test_login_totp_invalid_passcode(self, mock_conf, mock_get_totp_session):
        from fastapi.exceptions import HTTPException
        from keystoneauth1.exceptions import http

        mock_conf.openstack.default_region = "RegionOne"
        mock_conf.openstack.user_default_domain = "Default"

        mock_session = MagicMock()
        response = MagicMock()
        response.headers = {}
        response.json.return_value = {
            "error": {
                "code": "401",
                "message": "Invalid passcode",
            }
        }
        mock_session.get_token.side_effect = http.Unauthorized(response=response)
        mock_get_totp_session.return_value = mock_session

        credential = MagicMock()
        credential.region = "RegionOne"
        credential.domain = "Default"
        credential.username = "admin"
        credential.passcode = "000000"
        credential.receipt = "receipt-token"

        from skyline_apiserver.api.v1.login import login_totp

        with pytest.raises(HTTPException) as exc_info:
            login_totp(
                request=MagicMock(),
                response=MagicMock(),
                credential=credential,
                x_openstack_request_id="req-id",
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "invalid_totp"

    @patch("skyline_apiserver.api.v1.login._get_totp_session")
    @patch("skyline_apiserver.api.v1.login.CONF")
    def test_login_totp_receipt_expired(self, mock_conf, mock_get_totp_session):
        from fastapi.exceptions import HTTPException
        from keystoneauth1.exceptions import http

        mock_conf.openstack.default_region = "RegionOne"
        mock_conf.openstack.user_default_domain = "Default"

        mock_session = MagicMock()
        response = MagicMock()
        response.headers = {}
        response.json.return_value = {
            "error": {
                "code": "auth_receipt_expired",
                "message": "Auth receipt expired",
            }
        }
        mock_session.get_token.side_effect = http.Unauthorized(response=response)
        mock_get_totp_session.return_value = mock_session

        credential = MagicMock()
        credential.region = "RegionOne"
        credential.domain = "Default"
        credential.username = "admin"
        credential.passcode = "123456"
        credential.receipt = "expired-receipt"

        from skyline_apiserver.api.v1.login import login_totp

        with pytest.raises(HTTPException) as exc_info:
            login_totp(
                request=MagicMock(),
                response=MagicMock(),
                credential=credential,
                x_openstack_request_id="req-id",
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "receipt_expired"


class TestTOTPCredentialSchema:
    """Tests for TOTPCredential schema."""

    def test_domain_is_optional(self):
        from skyline_apiserver.schemas import login as schemas

        cred = schemas.TOTPCredential(
            username="admin",
            passcode="123456",
            receipt="receipt-token",
        )
        assert cred.domain is None

    def test_passcode_must_be_six_digits(self):
        from pydantic import ValidationError

        from skyline_apiserver.schemas import login as schemas

        with pytest.raises(ValidationError):
            schemas.TOTPCredential(
                username="admin",
                passcode="12345",
                receipt="receipt-token",
            )

    def test_totp_required_detail_schema(self):
        from skyline_apiserver.schemas import login as schemas

        detail = schemas.TOTPRequiredDetail(
            totp_required=True,
            receipt="abc",
        )
        assert detail.model_dump() == {
            "totp_required": True,
            "receipt": "abc",
        }
