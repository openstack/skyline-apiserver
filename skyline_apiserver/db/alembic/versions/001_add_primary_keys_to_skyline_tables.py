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

"""add primary keys to skyline tables

Revision ID: 001
Revises: 000
Create Date: 2026-07-20 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001"
down_revision = "000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Bug 2108940 left these tables without a primary key, which Galera and
    # Percona XtraDB Cluster with pxc_strict_mode=ENFORCING refuse to write
    # to, so some deployments added one by hand. Creating a second one fails
    # there, so leave such a table as it is.
    inspector = sa.inspect(op.get_bind())
    for table, column in (("revoked_token", "uuid"), ("settings", "key")):
        if inspector.get_pk_constraint(table)["constrained_columns"]:
            continue
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_index(op.f(f"ix_{table}_{column}"))
            batch_op.create_primary_key(f"pk_{table}", [column])


def downgrade() -> None:
    with op.batch_alter_table("settings") as batch_op:
        batch_op.drop_constraint("pk_settings", type_="primary")
        batch_op.create_index(op.f("ix_settings_key"), ["key"], unique=False)

    with op.batch_alter_table("revoked_token") as batch_op:
        batch_op.drop_constraint("pk_revoked_token", type_="primary")
        batch_op.create_index(op.f("ix_revoked_token_uuid"), ["uuid"], unique=False)
