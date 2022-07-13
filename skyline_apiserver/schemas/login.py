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
from pydantic import BaseModel, Field

from skyline_apiserver import config
from skyline_apiserver.types import constants


class Credential(BaseModel):
    region: str = Field(..., description="Credential user region")
    domain: str = Field(..., description="Credential user domain")
    username: str = Field(..., description="Credential username")
    password: str = Field(..., description="Credential password for user")

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
    id: str = Field(..., description="Domain ID")
    name: str = Field(..., description="Domain name")


class Role(BaseModel):
    id: str = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")


class Project(BaseModel):
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    domain: Domain = Field(..., description="Project domain")


class User(BaseModel):
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    domain: Domain = Field(..., description="User domain")


class PayloadBase(BaseModel):
    keystone_token: str = Field(..., description="Keystone token")
    region: str = Field(..., description="User region")
    exp: int = Field(..., description="Token expiration time")
    uuid: str = Field(..., description="UUID")


class Payload(PayloadBase):
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


class Profile(PayloadBase):
    project: Project = Field(..., description="User project")
    user: User = Field(..., description="User")
    roles: List[Role] = Field(..., description="User roles")
    keystone_token_exp: str = Field(..., description="Keystone token expiration time")
    base_roles: Optional[List[str]] = Field(None, description="User base roles")
    base_domains: Optional[List[str]] = Field(None, description="User base domains")
    endpoints: Optional[Dict[str, Any]] = Field(None, description="Keystone endpoints")
    projects: Optional[Dict[str, Any]] = Field(None, description="User projects")
    version: str = Field(..., description="Version")

    def toPayLoad(self) -> Payload:
        return Payload(
            keystone_token=self.keystone_token,
            region=self.region,
            exp=self.exp,
            uuid=self.uuid,
        )

    def toJWTPayload(self) -> str:
        return self.toPayLoad().toJWTPayload()
