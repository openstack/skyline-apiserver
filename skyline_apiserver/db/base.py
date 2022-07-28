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

from contextvars import ContextVar

from databases import Database, DatabaseURL, core

from skyline_apiserver.config import CONF

DATABASE = None
DB: ContextVar = ContextVar("skyline_db")


class ParallelDatabase(Database):
    def connection(self) -> core.Connection:
        return core.Connection(self._backend)


async def setup():
    db_url = DatabaseURL(CONF.default.database_url)
    global DATABASE
    if db_url.scheme == "mysql":
        DATABASE = ParallelDatabase(
            db_url,
            minsize=1,
            maxsize=100,
            echo=CONF.default.debug,
            charset="utf8",
            client_flag=0,
        )
    elif db_url.scheme == "sqlite":
        DATABASE = ParallelDatabase(db_url)
    else:
        raise ValueError("Unsupported database backend")
    await DATABASE.connect()


async def inject_db():
    global DATABASE
    DB.set(DATABASE)
