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

import importlib.util
from pathlib import Path
from typing import Any, Iterator

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

VERSIONS = Path(__file__).parents[2] / "db" / "alembic" / "versions"
TABLES = (("revoked_token", "uuid"), ("settings", "key"))


def _migration(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, VERSIONS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(connection: sa.engine.Connection, step: Any) -> None:
    with Operations.context(MigrationContext.configure(connection)):
        step()


def _schema(connection: sa.engine.Connection) -> dict:
    inspector = sa.inspect(connection)
    return {
        table: (
            inspector.get_pk_constraint(table)["constrained_columns"],
            sorted(i["name"] for i in inspector.get_indexes(table)),
        )
        for table, _ in TABLES
    }


@pytest.fixture
def connection() -> Iterator[sa.engine.Connection]:
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        _run(connection, _migration("000_init").upgrade)
        yield connection


class TestAddPrimaryKeys:
    expected = {"revoked_token": (["uuid"], []), "settings": (["key"], [])}

    def test_adds_the_primary_keys(self, connection: sa.engine.Connection) -> None:
        _run(connection, _migration("001_add_primary_keys_to_skyline_tables").upgrade)
        assert _schema(connection) == self.expected

    def test_keeps_primary_keys_added_by_hand(self, connection: sa.engine.Connection) -> None:
        # The way out of bug 2108940 on Galera/PXC was to add the keys by
        # hand, leaving both the key and the old index; the migration leaves
        # such a table as it is.
        def add_by_hand() -> None:
            from alembic import op

            for table, column in TABLES:
                with op.batch_alter_table(table) as batch_op:
                    batch_op.create_primary_key(f"manual_{table}", [column])

        _run(connection, add_by_hand)
        _run(connection, _migration("001_add_primary_keys_to_skyline_tables").upgrade)
        assert _schema(connection) == {
            "revoked_token": (["uuid"], ["ix_revoked_token_uuid"]),
            "settings": (["key"], ["ix_settings_key"]),
        }
