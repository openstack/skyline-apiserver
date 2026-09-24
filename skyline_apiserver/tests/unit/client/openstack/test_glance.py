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
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.exceptions import HTTPException
from keystoneauth1.exceptions.http import Unauthorized

from skyline_apiserver.client.openstack import glance


class TestListImages:
    @patch("skyline_apiserver.client.openstack.glance.utils.image_client")
    def test_passes_filters_as_direct_query_kwargs(self, mock_image_client):
        profile = SimpleNamespace(region="RegionOne")
        session = MagicMock()
        image_one = MagicMock()
        image_two = MagicMock()
        connection = MagicMock()
        # Lazy generator, as returned by openstacksdk's image.images().
        connection.image.images.return_value = (img for img in (image_one, image_two))
        mock_image_client.return_value = connection

        result = glance.list_images(
            profile=profile,
            session=session,
            global_request_id="req-test",
            filters={"id": "in:image-1,image-2"},
        )

        assert result == [image_one, image_two]
        mock_image_client.assert_called_once_with(
            session=session,
            region="RegionOne",
            global_request_id="req-test",
        )
        connection.image.images.assert_called_once_with(id="in:image-1,image-2")
        # Regression guard: nested filters= is silently dropped by openstacksdk.
        assert "filters" not in connection.image.images.call_args.kwargs

    @patch("skyline_apiserver.client.openstack.glance.utils.image_client")
    def test_calls_images_without_kwargs_when_filters_omitted(self, mock_image_client):
        profile = SimpleNamespace(region="RegionOne")
        connection = MagicMock()
        connection.image.images.return_value = iter([])
        mock_image_client.return_value = connection

        result = glance.list_images(
            profile=profile,
            session=MagicMock(),
            global_request_id="req-test",
        )

        assert result == []
        connection.image.images.assert_called_once_with()

    @patch("skyline_apiserver.client.openstack.glance.utils.image_client")
    def test_maps_unauthorized_while_materialising_results(self, mock_image_client):
        profile = SimpleNamespace(region="RegionOne")
        connection = MagicMock()

        def failing_images():
            raise Unauthorized(message="token expired")
            yield  # pragma: no cover - keep this a lazy generator

        connection.image.images.return_value = failing_images()
        mock_image_client.return_value = connection

        with pytest.raises(HTTPException) as exc_info:
            glance.list_images(
                profile=profile,
                session=MagicMock(),
                global_request_id="req-test",
                filters={"id": "in:image-1"},
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
