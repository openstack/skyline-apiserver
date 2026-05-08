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

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)

METADATA = MetaData()


RevokedToken = Table(
    "revoked_token",
    METADATA,
    Column("uuid", String(length=128), nullable=False, index=True, unique=False),
    Column("expire", Integer, nullable=False),
)

Settings = Table(
    "settings",
    METADATA,
    Column("key", String(length=128), nullable=False, index=True, unique=True),
    Column("value", JSON, nullable=True),
)

MessageBanners = Table(
    "message_banners",
    METADATA,
    Column("id", String(length=36), nullable=False, primary_key=True),
    Column("type", String(length=32), nullable=False, index=True),
    Column("title", String(length=255), nullable=True),
    Column("message", Text, nullable=False),
    Column("impacted_service", String(length=255), nullable=True),
    Column("start_at", DateTime(timezone=True), nullable=True, index=True),
    Column("expires_at", DateTime(timezone=True), nullable=False, index=True),
    Column("project_id", String(length=128), nullable=True, index=True),
    Column("region", String(length=255), nullable=True, index=True),
    Column("source", String(length=32), nullable=False, index=True),
    Column("source_id", String(length=255), nullable=True, index=True),
    Column("source_url", String(length=1024), nullable=True),
    Column("enabled", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

DeletedExternalMessageBanners = Table(
    "deleted_external_message_banners",
    METADATA,
    Column("source", String(length=32), nullable=False, primary_key=True),
    Column("source_id", String(length=255), nullable=False, primary_key=True),
    Column("region", String(length=255), nullable=True, index=True),
    Column("deleted_at", DateTime(timezone=True), nullable=False),
)
