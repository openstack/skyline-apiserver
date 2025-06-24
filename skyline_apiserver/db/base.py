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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from skyline_apiserver.config import CONF

DATABASE = None
DB: ContextVar = ContextVar("skyline_db")


class DBWrapper:
    def __init__(self, engine):
        self.engine = engine

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def transaction(self):
        session = self.get_session()
        return Transaction(session)

    def execute(self, query, params=None):
        session = self.get_session()
        with session.begin():
            if params:
                result = session.execute(query, params)
            else:
                result = session.execute(query)
        session.close()
        return result

    def fetch_one(self, query):
        session = self.get_session()
        with session.begin():
            result = session.execute(query).fetchone()
        session.close()
        return result

    def fetch_all(self, query):
        session = self.get_session()
        with session.begin():
            result = session.execute(query).fetchall()
        session.close()
        return result


def setup():
    db_url = CONF.default.database_url
    global DATABASE
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_pre_ping=True)
    DATABASE = DBWrapper(engine)
    DB.set(DATABASE)


def inject_db():
    global DATABASE
    DB.set(DATABASE)


def get_session():
    engine = DB.get()
    Session = sessionmaker(bind=engine)
    return Session()


class Transaction:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        self.session.begin()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


# Usage compatible with async with db.transaction():
def transaction():
    session = get_session()
    return Transaction(session)


# Usage compatible with await db.execute(query, ...)
def execute(query, params=None):
    session = get_session()
    with session.begin():
        if params:
            result = session.execute(query, params)
        else:
            result = session.execute(query)
    session.close()
    return result


# Usage compatible with await db.fetch_one(query)
def fetch_one(query):
    session = get_session()
    with session.begin():
        result = session.execute(query).fetchone()
    session.close()
    return result


# Usage compatible with await db.fetch_all(query)
def fetch_all(query):
    session = get_session()
    with session.begin():
        result = session.execute(query).fetchall()
    session.close()
    return result
