# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from skyline_apiserver.client import utils


class TestGenerateSessionOriginalIP:
    @patch("skyline_apiserver.client.utils.CONF")
    @patch("skyline_apiserver.client.utils.Session")
    @patch("skyline_apiserver.client.utils.Token")
    @patch("skyline_apiserver.client.utils.get_endpoint")
    @patch("skyline_apiserver.client.utils.get_system_session")
    def test_passes_original_ip_to_user_and_system_sessions(
        self,
        mock_get_system_session,
        mock_get_endpoint,
        mock_token,
        mock_session_cls,
        mock_conf,
    ):
        profile = SimpleNamespace(
            region="RegionOne",
            keystone_token="token",
            project=SimpleNamespace(id="project-id"),
        )
        system_session = MagicMock()
        user_session = MagicMock()
        auth = MagicMock()
        user_session.auth = auth
        mock_get_system_session.return_value = system_session
        mock_get_endpoint.return_value = "https://keystone.example/v3"
        mock_token.return_value = auth
        mock_session_cls.return_value = user_session
        mock_conf.default.cafile = "/ca.pem"

        result = utils.generate_session(profile, original_ip="198.51.100.20")

        assert result is user_session
        mock_get_system_session.assert_called_once_with(original_ip="198.51.100.20")
        mock_get_endpoint.assert_called_once_with(
            region="RegionOne",
            service="identity",
            session=system_session,
        )
        mock_token.assert_called_once_with(
            auth_url="https://keystone.example/v3",
            token="token",
            project_id="project-id",
        )
        mock_session_cls.assert_called_once_with(
            auth=auth,
            original_ip="198.51.100.20",
            verify="/ca.pem",
            timeout=30,
        )
        auth.get_auth_ref.assert_called_once_with(user_session)


class TestSystemSessionOriginalIP:
    @patch("skyline_apiserver.client.utils.CONF")
    @patch("skyline_apiserver.client.utils.Session")
    def test_request_session_does_not_mutate_global_session(self, mock_session, mock_conf):
        auth = object()
        transport = object()
        global_session = SimpleNamespace(auth=auth, session=transport)
        request_session = MagicMock()
        mock_session.return_value = request_session
        mock_conf.default.cafile = "/ca.pem"

        with patch.object(utils, "SESSION", global_session):
            result = utils.get_system_session(original_ip="198.51.100.20")

        assert result is request_session
        assert not hasattr(global_session, "original_ip")
        mock_session.assert_called_once_with(
            auth=auth,
            session=transport,
            original_ip="198.51.100.20",
            verify="/ca.pem",
            timeout=30,
        )

    @patch("skyline_apiserver.client.utils.CONF")
    @patch("skyline_apiserver.client.utils.Session")
    def test_different_addresses_get_distinct_session_wrappers(self, mock_session, mock_conf):
        auth = object()
        transport = object()
        global_session = SimpleNamespace(auth=auth, session=transport)
        first_session = MagicMock()
        second_session = MagicMock()
        mock_session.side_effect = [first_session, second_session]
        mock_conf.default.cafile = ""

        with patch.object(utils, "SESSION", global_session):
            first = utils.get_system_session(original_ip="198.51.100.20")
            second = utils.get_system_session(original_ip="203.0.113.30")

        assert first is first_session
        assert second is second_session
        assert mock_session.call_args_list == [
            call(
                auth=auth,
                session=transport,
                original_ip="198.51.100.20",
                verify="",
                timeout=30,
            ),
            call(
                auth=auth,
                session=transport,
                original_ip="203.0.113.30",
                verify="",
                timeout=30,
            ),
        ]
