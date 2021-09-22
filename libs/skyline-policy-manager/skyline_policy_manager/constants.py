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

POLICY_NS = "oslo.policy.policies"

SUPPORTED_SERVICE_EPS = {
    # openstack_service: [<entry_point_name>, <entry_point_name>,]
    "cinder": ["cinder"],
    "glance": ["glance"],
    "heat": ["heat"],
    "ironic": ["ironic.api", "ironic_inspector.api"],
    "keystone": ["keystone"],
    "neutron": ["neutron", "neutron-vpnaas"],
    "nova": ["nova"],
    "octavia": ["octavia"],
    "panko": ["panko"],
    "placement": ["placement"],
}
