"""fix workspace table

Revision ID: fix_workspace_table
Revises: merge_heads_migration
Create Date: 2025-05-23 07:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

# revision identifiers, used by Alembic.
revision: str = 'fix_workspace_table'
down_revision: Union[str, None] = 'merge_heads_migration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('workspace', schema=None) as batch_op:
        # Change description column type from VARCHAR to Text
        batch_op.alter_column('description',
                              existing_type=sa.VARCHAR(),
                              type_=sa.Text(),
                              existing_nullable=True)
        
        # Add index on owner_id column
        batch_op.create_index('ix_workspace_owner_id', ['owner_id'], unique=False)
        
        # Add unique constraint on id column
        batch_op.create_unique_constraint('uq_workspace_id', ['id'])


def downgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('workspace', schema=None) as batch_op:
        # Remove unique constraint on id column
        batch_op.drop_constraint('uq_workspace_id', type_='unique')
        
        # Remove index on owner_id column
        batch_op.drop_index('ix_workspace_owner_id')
        
        # Change description column type back to VARCHAR
        batch_op.alter_column('description',
                              existing_type=sa.Text(),
                              type_=sa.VARCHAR(),
                              existing_nullable=True)
