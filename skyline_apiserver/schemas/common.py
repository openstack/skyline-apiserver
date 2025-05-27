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

from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str = Field(..., description="Message")
    code: int = Field(default=200, description="Code")
    title: str = Field(default="OK", description="Title")


class ErrorMessageBase(BaseModel):
    detail: str = Field(..., description="Detail message")


class BadRequestMessage(ErrorMessageBase):
    """"""


class UnauthorizedMessage(ErrorMessageBase):
    """"""


class ForbiddenMessage(ErrorMessageBase):
    """"""


class NotFoundMessage(ErrorMessageBase):
    """"""


class InternalServerErrorMessage(ErrorMessageBase):
    """"""
