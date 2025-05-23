"""merge workspace migration

Revision ID: 24ff2ca5ec0e
Revises: 66f72f04a1de, workspace_migration
Create Date: 2025-05-22 21:05:30.338878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration


# revision identifiers, used by Alembic.
revision: str = '24ff2ca5ec0e'
down_revision: Union[str, None] = ('66f72f04a1de', 'workspace_migration')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    pass


def downgrade() -> None:
    conn = op.get_bind()
    pass
