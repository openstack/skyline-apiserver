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
