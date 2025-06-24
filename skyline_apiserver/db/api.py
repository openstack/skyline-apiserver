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
from functools import wraps
from typing import Any, Union

from sqlalchemy import Insert, Update, delete, func, insert, select, update

from skyline_apiserver.types import Fn

from .base import DB, inject_db
from .models import RevokedToken, Settings


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
