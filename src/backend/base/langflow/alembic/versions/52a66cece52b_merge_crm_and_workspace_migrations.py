"""merge crm and workspace migrations

Revision ID: 52a66cece52b
Revises: crm_tables_migration, fix_workspace_table
Create Date: 2025-05-23 11:08:11.319190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration


# revision identifiers, used by Alembic.
revision: str = '52a66cece52b'
down_revision: Union[str, None] = ('crm_tables_migration', 'fix_workspace_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    pass


def downgrade() -> None:
    conn = op.get_bind()
    pass
