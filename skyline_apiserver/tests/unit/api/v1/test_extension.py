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

from unittest.mock import Mock, patch

import pytest

from skyline_apiserver.api.v1.extension import list_recycle_servers


class TestListRecycleServersReal:
    """Real test cases for list_recycle_servers function"""

    @pytest.fixture
    def mock_profile(self):
        """Mock profile with basic user info"""
        profile = Mock()
        profile.project.id = "test-project-id"
        profile.project.name = "test-project"
        return profile

    @pytest.fixture
    def mock_server_data(self):
        """Mock server data for testing"""
        return {
            "id": "test-server-id",
            "name": "test-server",
            "status": "soft_deleted",
            "image": "test-image-id",
            "volumes_attached": [{"id": "test-volume-id", "device": "/dev/vda"}],
            "updated_at": "2024-01-01T00:00:00Z",
            "project_id": "test-project-id",
        }

    @patch("skyline_apiserver.api.v1.extension.nova")
    @patch("skyline_apiserver.api.v1.extension.glance")
    @patch("skyline_apiserver.api.v1.extension.cinder")
    @patch("skyline_apiserver.api.v1.extension.keystone")
    @patch("skyline_apiserver.api.v1.extension.generate_session")
    @patch("skyline_apiserver.api.v1.extension.get_system_session")
    @patch("skyline_apiserver.api.v1.extension.OSServer")
    @patch("skyline_apiserver.api.v1.extension.Server")
    @patch("skyline_apiserver.api.v1.extension.RecycleServersResponseBase")
    @patch("skyline_apiserver.api.v1.extension.schemas")
    @patch("skyline_apiserver.api.v1.extension.CONF")
    def test_list_recycle_servers_basic(
        self,
        mock_conf,
        mock_schemas,
        mock_recycle_response_base,
        mock_server,
        mock_os_server,
        mock_get_system_session,
        mock_generate_session,
        mock_keystone,
        mock_cinder,
        mock_glance,
        mock_nova,
        mock_profile,
        mock_server_data,
    ):
        """Test basic functionality of list_recycle_servers function"""
        # Setup configuration mock
        mock_conf.openstack.reclaim_instance_interval = 86400

        # Setup mocks
        mock_system_session = Mock()
        mock_get_system_session.return_value = mock_system_session

        mock_current_session = Mock()
        mock_generate_session.return_value = mock_current_session

        # Mock server list response
        mock_server_obj = Mock()
        mock_server_obj.to_dict.return_value = mock_server_data
        mock_server.return_value = mock_server_obj

        mock_os_server_obj = Mock()
        mock_os_server_obj.to_dict.return_value = mock_server_data
        mock_os_server.return_value = mock_os_server_obj

        # Mock nova.list_servers response
        mock_nova.list_servers.return_value = [mock_server_obj]

        # Mock glance.list_images response (empty)
        mock_glance.list_images.return_value = []

        # Mock cinder.list_volumes response (empty)
        mock_cinder.list_volumes.return_value = []

        # Mock RecycleServersResponseBase
        mock_recycle_obj = Mock()
        mock_recycle_obj.id = "test-server-id"
        mock_recycle_obj.image = "test-image-id"
        mock_recycle_obj.updated_at = "2024-01-01T00:00:00Z"
        mock_recycle_obj.project_id = "test-project-id"
        mock_recycle_obj.host = "test-host"
        mock_recycle_response_base.parse_obj.return_value = mock_recycle_obj

        # Mock schemas.RecycleServersResponse
        mock_response = Mock()
        mock_response.recycle_servers = [mock_recycle_obj]
        mock_schemas.RecycleServersResponse.return_value = mock_response

        # Call the actual function
        result = list_recycle_servers(
            profile=mock_profile,
            x_openstack_request_id="test-request-id",
            all_projects=False,
            limit=None,
            marker=None,
            sort_dirs=None,
            sort_keys=None,
            project_id=None,
            project_name=None,
            name=None,
            uuid=None,
        )

        # Assertions
        assert result is not None
        assert hasattr(result, "recycle_servers")

        # Verify nova.list_servers was called with correct parameters
        mock_nova.list_servers.assert_called_once()
        call_args = mock_nova.list_servers.call_args
        assert call_args[1]["session"] == mock_system_session
        assert call_args[1]["search_opts"]["status"] == "soft_deleted"
        assert call_args[1]["search_opts"]["deleted"] is True
        assert call_args[1]["search_opts"]["all_tenants"] is True
        assert call_args[1]["search_opts"]["project_id"] == "test-project-id"

        # Verify other services were called
        mock_glance.list_images.assert_called()
        mock_cinder.list_volumes.assert_called()

        # Verify keystone was not called (since all_projects=False)
        mock_keystone.list_projects.assert_not_called()
