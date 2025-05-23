"""add workspace_id to flow

Revision ID: add_workspace_id_to_flow
Revises: 24ff2ca5ec0e
Create Date: 2025-05-22 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration


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
            op.create_foreign_key(None, "flow", "workspace", ["workspace_id"], ["id"])
            op.create_index(op.f("ix_flow_workspace_id"), "flow", ["workspace_id"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore
    
    # Remove workspace_id from flow table
    if "flow" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("flow")]
        if "workspace_id" in columns:
            op.drop_index(op.f("ix_flow_workspace_id"), "flow")
            op.drop_constraint(None, "flow", type_="foreignkey")
            op.drop_column("flow", "workspace_id")
