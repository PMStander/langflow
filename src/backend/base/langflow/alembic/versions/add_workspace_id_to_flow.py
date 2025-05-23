"""add workspace_id to flow

Revision ID: add_workspace_id_to_flow
Revises: 24ff2ca5ec0e
Create Date: 2025-05-22 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'add_workspace_id_to_flow'
down_revision: Union[str, None] = '24ff2ca5ec0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore

    # Add workspace_id to flow table
    if "flow" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("flow")]
        if "workspace_id" not in columns:
            op.add_column("flow", sa.Column("workspace_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=True))

            # Use batch operations for SQLite compatibility
            with op.batch_alter_table("flow", schema=None) as batch_op:
                batch_op.create_foreign_key(None, "workspace", ["workspace_id"], ["id"])
                batch_op.create_index("ix_flow_workspace_id", ["workspace_id"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore

    # Remove workspace_id from flow table
    if "flow" in inspector.get_table_names():
        # Use batch operations for SQLite compatibility
        with op.batch_alter_table("flow", schema=None) as batch_op:
            # Check if the index exists before trying to drop it
            indexes = inspector.get_indexes("flow")
            index_names = [index['name'] for index in indexes]

            if "ix_flow_workspace_id" in index_names:
                batch_op.drop_index("ix_flow_workspace_id")

            # Check for foreign keys
            foreign_keys = inspector.get_foreign_keys("flow")
            for fk in foreign_keys:
                if fk.get('referred_table') == 'workspace' and 'workspace_id' in fk.get('constrained_columns', []):
                    batch_op.drop_constraint(fk.get('name'), type_="foreignkey")

        # Check if the column exists before trying to drop it
        columns = [c["name"] for c in inspector.get_columns("flow")]
        if "workspace_id" in columns:
            op.drop_column("flow", "workspace_id")
