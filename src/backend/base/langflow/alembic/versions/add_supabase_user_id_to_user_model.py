"""Add supabase_user_id to User model

Revision ID: add_supabase_user_id
Revises: 
Create Date: 2023-10-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_supabase_user_id'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add supabase_user_id column to user table
    op.add_column('user', sa.Column('supabase_user_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_user_supabase_user_id'), 'user', ['supabase_user_id'], unique=False)


def downgrade() -> None:
    # Drop supabase_user_id column from user table
    op.drop_index(op.f('ix_user_supabase_user_id'), table_name='user')
    op.drop_column('user', 'supabase_user_id')
