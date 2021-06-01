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

from typing import Any, Dict, List, Optional

from jose import jwt
from pydantic import BaseModel

from skyline_apiserver import config
from skyline_apiserver.types import constants


class Credential(BaseModel):
    region: str
    domain: str
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "region": "RegionOne",
                "username": "admin",
                "domain": "default",
                "password": "admin",
            },
        }


class Domain(BaseModel):
    id: str
    name: str


class License(BaseModel):
    name: str
    summary: str
    macs: List[str]
    features: List[Dict[str, Any]]
    start: str
    end: str


class Region(BaseModel):
    id: str


class Role(BaseModel):
    id: str
    name: str


class Project(BaseModel):
    id: str
    name: str
    domain: Domain


class User(BaseModel):
    id: str
    name: str
    domain: Domain


class Payload(BaseModel):
    keystone_token: str
    region: str
    exp: int
    uuid: str

    def toDict(self) -> Dict[str, Any]:
        return {
            "keystone_token": self.keystone_token,
            "region": self.region,
            "exp": self.exp,
            "uuid": self.uuid,
        }

    def toJWTPayload(self) -> str:
        return jwt.encode(
            self.toDict(),
            config.CONF.default.secret_key,
            algorithm=constants.ALGORITHM,
        )


class Profile(BaseModel):
    keystone_token: str
    region: str
    project: Project
    user: User
    roles: List[Role]
    keystone_token_exp: str
    base_roles: Optional[List[str]]
    base_domains: Optional[List[str]]
    endpoints: Optional[Dict[str, Any]]
    projects: Optional[Dict[str, Any]]
    exp: int
    uuid: str
    version: str
    license: Optional[License]
    currency: Optional[Dict[str, str]]

    def toPayLoad(self) -> Payload:
        return Payload(
            keystone_token=self.keystone_token,
            region=self.region,
            exp=self.exp,
            uuid=self.uuid,
        )

    def toJWTPayload(self) -> str:
        return self.toPayLoad().toJWTPayload()
