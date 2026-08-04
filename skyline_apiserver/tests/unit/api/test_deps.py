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

from unittest.mock import patch

from starlette.requests import Request

from skyline_apiserver.api import deps


def _request(headers=None, client=("192.0.2.10", 1234)):
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": headers or [],
            "client": client,
            "server": ("testserver", 80),
        }
    )


class TestGetOriginalIP:
    @patch("skyline_apiserver.api.deps.CONF")
    def test_uses_direct_client_when_header_is_unset(self, mock_conf):
        mock_conf.default.secure_proxy_addr_header = None
        request = _request(headers=[(b"x-real-ip", b"198.51.100.20")])

        assert deps.get_original_ip(request) == "192.0.2.10"

    @patch("skyline_apiserver.api.deps.CONF")
    def test_uses_configured_single_address_header(self, mock_conf):
        mock_conf.default.secure_proxy_addr_header = "X-Real-IP"
        request = _request(headers=[(b"x-real-ip", b"198.51.100.20")])

        assert deps.get_original_ip(request) == "198.51.100.20"

    @patch("skyline_apiserver.api.deps.CONF")
    def test_falls_back_when_configured_header_is_absent(self, mock_conf):
        mock_conf.default.secure_proxy_addr_header = "X-Real-IP"

        assert deps.get_original_ip(_request()) == "192.0.2.10"

    @patch("skyline_apiserver.api.deps.CONF")
    def test_does_not_forward_address_chain(self, mock_conf):
        mock_conf.default.secure_proxy_addr_header = "X-Forwarded-For"
        request = _request(headers=[(b"x-forwarded-for", b"198.51.100.20, 192.0.2.15")])

        assert deps.get_original_ip(request) == "192.0.2.10"

    @patch("skyline_apiserver.api.deps.CONF")
    def test_falls_back_for_duplicate_configured_headers(self, mock_conf):
        mock_conf.default.secure_proxy_addr_header = "X-Real-IP"
        request = _request(
            headers=[
                (b"x-real-ip", b"198.51.100.20"),
                (b"x-real-ip", b"203.0.113.30"),
            ]
        )

        assert deps.get_original_ip(request) == "192.0.2.10"

    @patch("skyline_apiserver.api.deps.CONF")
    def test_returns_none_without_client_information(self, mock_conf):
        mock_conf.default.secure_proxy_addr_header = None

        assert deps.get_original_ip(_request(client=None)) is None
