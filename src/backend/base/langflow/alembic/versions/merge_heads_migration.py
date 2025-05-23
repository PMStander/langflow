"""merge heads migration

Revision ID: merge_heads_migration
Revises: add_supabase_user_id, add_workspace_id_to_flow
Create Date: 2025-05-23 07:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'merge_heads_migration'
down_revision: Union[str, None] = ('add_supabase_user_id', 'add_workspace_id_to_flow')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a merge migration, no schema changes needed
    pass


def downgrade() -> None:
    # This is a merge migration, no schema changes needed
    pass
