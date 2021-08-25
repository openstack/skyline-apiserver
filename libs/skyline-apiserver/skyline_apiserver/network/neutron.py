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

from __future__ import annotations

from typing import Any, Dict

import six
from six.moves.urllib import parse

from skyline_apiserver.types import constants
from skyline_apiserver.utils.httpclient import get_assert_200


async def get_ports(
    neutron_endpoint: str,
    keystone_token: str,
    global_request_id: str,
    search_opts: Dict[str, Any],
) -> Dict[str, Any]:
    """Get the ports in the environment .

    :param neutron_endpoint: Nova endpoint in specified region.
    :type neutron_endpoint: str
    :param keystone_token: Keystone token.
    :type keystone_token: str
    :param search_opts: Search opts.
    :type search_opts: dict
    :return: ports.
    :rtype: Dict[str, Any]
    """
    url = neutron_endpoint + constants.NEUTRON_PORTS_API
    qparams = {}
    for opt, val in search_opts.items():
        if val:
            if isinstance(val, six.text_type):
                val = val.encode("utf-8")
            if isinstance(val, list):
                val = [v.encode("utf-8") for v in val]
            qparams[opt] = val
    url += "?%s" % parse.urlencode(qparams, doseq=True)
    resp = await get_assert_200(
        url,
        headers={"X-Auth-Token": keystone_token, constants.INBOUND_HEADER: global_request_id},
    )
    return resp.json()
