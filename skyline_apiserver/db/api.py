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

import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, Optional, Union

from sqlalchemy import Insert, Update, delete, func, insert, or_, select, update

from skyline_apiserver.types import Fn

from .base import DB, inject_db
from .models import (
    DeletedExternalMessageBanners,
    MessageBanners,
    RevokedToken,
    Settings,
)


MESSAGE_BANNER_COLUMNS = set(MessageBanners.c.keys())
MESSAGE_BANNER_UPDATE_COLUMNS = MESSAGE_BANNER_COLUMNS - {"id", "created_at"}


def check_db_connected(fn: Fn) -> Any:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        inject_db()
        db = DB.get()
        assert db is not None, "Database is not connected."
        return fn(*args, **kwargs)

    return wrapper


@check_db_connected
def check_token(token_id: str) -> bool:
    count_label = "revoked_count"
    query = (
        select(func.count(RevokedToken.c.uuid).label(count_label))
        .select_from(RevokedToken)
        .where(RevokedToken.c.uuid == token_id)
    )
    db = DB.get()
    with db.transaction():
        result = db.fetch_one(query)
    count = getattr(result, count_label, 0)
    return count > 0


@check_db_connected
def revoke_token(token_id: str, expire: int) -> Any:
    query = insert(RevokedToken)
    db = DB.get()
    with db.transaction():
        result = db.execute(query, {"uuid": token_id, "expire": expire})
    return result


@check_db_connected
def purge_revoked_token() -> Any:
    now = int(time.time()) - 1
    query = delete(RevokedToken).where(RevokedToken.c.expire < now)
    db = DB.get()
    with db.transaction():
        result = db.execute(query)
    return result


@check_db_connected
def list_settings() -> Any:
    query = select(Settings)
    db = DB.get()
    with db.transaction():
        result = db.fetch_all(query)
    return result


@check_db_connected
def get_setting(key: str) -> Any:
    query = select(Settings).where(Settings.c.key == key)
    db = DB.get()
    with db.transaction():
        result = db.fetch_one(query)
    return result


@check_db_connected
def update_setting(key: str, value: Any) -> Any:
    get_query = (
        select(Settings.c.key, Settings.c.value).where(Settings.c.key == key).with_for_update()
    )
    db = DB.get()
    with db.transaction():
        is_exist = db.fetch_one(get_query)
        stmt: Union[Insert, Update]
        if is_exist is None:
            stmt = insert(Settings).values(key=key, value=value)
        else:
            stmt = update(Settings).where(Settings.c.key == key).values(value=value)
        db.execute(stmt)
        result = db.fetch_one(get_query)
    return result


@check_db_connected
def delete_setting(key: str) -> Any:
    query = delete(Settings).where(Settings.c.key == key)
    db = DB.get()
    with db.transaction():
        result = db.execute(query)
    return result


def _project_region_conditions(
    project_id: Optional[str] = None,
    region: Optional[str] = None,
) -> list:
    conditions = []
    if project_id:
        conditions.append(
            or_(
                MessageBanners.c.project_id.is_(None),
                MessageBanners.c.project_id == project_id,
            )
        )
    if region:
        conditions.append(
            or_(
                MessageBanners.c.region.is_(None),
                MessageBanners.c.region == region,
            )
        )
    return conditions


@check_db_connected
def list_message_banners(
    project_id: Optional[str] = None,
    region: Optional[str] = None,
) -> Any:
    query = select(MessageBanners).order_by(MessageBanners.c.created_at.desc())
    conditions = _project_region_conditions(project_id=project_id, region=region)
    if conditions:
        query = query.where(*conditions)
    db = DB.get()
    with db.transaction():
        result = db.fetch_all(query)
    return result


@check_db_connected
def list_active_message_banners(
    project_id: Optional[str] = None,
    region: Optional[str] = None,
    message_type: Optional[str] = None,
    global_only: bool = False,
) -> Any:
    now = datetime.now(timezone.utc)
    conditions = [
        MessageBanners.c.enabled.is_(True),
        MessageBanners.c.expires_at > now,
    ]
    if message_type:
        conditions.append(MessageBanners.c.type == message_type)
    if global_only:
        conditions.append(MessageBanners.c.project_id.is_(None))
    elif project_id:
        conditions.extend(_project_region_conditions(project_id=project_id))
    if region:
        conditions.extend(_project_region_conditions(region=region))
    query = (
        select(MessageBanners)
        .where(*conditions)
        .order_by(MessageBanners.c.created_at.desc())
    )
    db = DB.get()
    with db.transaction():
        result = db.fetch_all(query)
    return result


@check_db_connected
def get_message_banner(banner_id: str) -> Any:
    query = select(MessageBanners).where(MessageBanners.c.id == banner_id)
    db = DB.get()
    with db.transaction():
        result = db.fetch_one(query)
    return result


@check_db_connected
def create_message_banner(values: Dict[str, Any]) -> Any:
    now = datetime.now(timezone.utc)
    banner_id = values.get("id") or str(uuid.uuid4())
    filtered_values = {
        key: value for key, value in values.items() if key in MESSAGE_BANNER_COLUMNS
    }
    data = {
        **filtered_values,
        "id": banner_id,
        "created_at": values.get("created_at") or now,
        "updated_at": values.get("updated_at") or now,
    }
    query = insert(MessageBanners).values(**data)
    get_query = select(MessageBanners).where(MessageBanners.c.id == banner_id)
    db = DB.get()
    with db.transaction():
        db.execute(query)
        result = db.fetch_one(get_query)
    return result


@check_db_connected
def update_message_banner(banner_id: str, values: Dict[str, Any]) -> Any:
    filtered_values = {
        key: value for key, value in values.items() if key in MESSAGE_BANNER_UPDATE_COLUMNS
    }
    data = {
        **filtered_values,
        "updated_at": datetime.now(timezone.utc),
    }
    query = (
        update(MessageBanners)
        .where(MessageBanners.c.id == banner_id)
        .values(**data)
    )
    get_query = select(MessageBanners).where(MessageBanners.c.id == banner_id)
    db = DB.get()
    with db.transaction():
        db.execute(query)
        result = db.fetch_one(get_query)
    return result


@check_db_connected
def delete_message_banner(banner_id: str) -> Any:
    get_query = select(MessageBanners).where(MessageBanners.c.id == banner_id)
    delete_query = delete(MessageBanners).where(MessageBanners.c.id == banner_id)
    db = DB.get()
    with db.transaction():
        result = db.fetch_one(get_query)
        if (
            result is not None
            and result.source != "manual"
            and result.source_id is not None
        ):
            deleted_query = select(DeletedExternalMessageBanners).where(
                DeletedExternalMessageBanners.c.source == result.source,
                DeletedExternalMessageBanners.c.source_id == result.source_id,
            )
            deleted_record = db.fetch_one(deleted_query)
            if deleted_record is None:
                db.execute(
                    insert(DeletedExternalMessageBanners).values(
                        source=result.source,
                        source_id=result.source_id,
                        region=result.region,
                        deleted_at=datetime.now(timezone.utc),
                    )
                )
        db.execute(delete_query)
    return result


@check_db_connected
def sync_servicenow_ext_message_banner(values: Dict[str, Any]) -> Any:
    source = values["source"]
    source_id = values["source_id"]
    deleted_query = select(DeletedExternalMessageBanners).where(
        DeletedExternalMessageBanners.c.source == source,
        DeletedExternalMessageBanners.c.source_id == source_id,
    )
    get_query = select(MessageBanners).where(
        MessageBanners.c.source == source,
        MessageBanners.c.source_id == source_id,
    )
    db = DB.get()
    with db.transaction():
        deleted_record = db.fetch_one(deleted_query)
        if deleted_record is not None:
            return None
        existing = db.fetch_one(get_query)
    if existing is None:
        return create_message_banner(values)
    values.pop("enabled", None)
    return update_message_banner(existing.id, values)
