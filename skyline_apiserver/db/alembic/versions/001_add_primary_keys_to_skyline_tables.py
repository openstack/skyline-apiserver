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

from alembic import op

# revision identifiers, used by Alembic.
revision = "001"
down_revision = "000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("revoked_token") as batch_op:
        batch_op.drop_index(op.f("ix_revoked_token_uuid"))
        batch_op.create_primary_key("pk_revoked_token", ["uuid"])

    with op.batch_alter_table("settings") as batch_op:
        batch_op.drop_index(op.f("ix_settings_key"))
        batch_op.create_primary_key("pk_settings", ["key"])


def downgrade() -> None:
    with op.batch_alter_table("settings") as batch_op:
        batch_op.drop_constraint("pk_settings", type_="primary")
        batch_op.create_index(op.f("ix_settings_key"), ["key"], unique=False)

    with op.batch_alter_table("revoked_token") as batch_op:
        batch_op.drop_constraint("pk_revoked_token", type_="primary")
        batch_op.create_index(op.f("ix_revoked_token_uuid"), ["uuid"], unique=False)
