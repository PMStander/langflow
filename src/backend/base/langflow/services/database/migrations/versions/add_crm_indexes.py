"""Add indexes to frequently queried CRM fields

Revision ID: add_crm_indexes
Revises: 4d4f8a88110d
Create Date: 2025-05-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from uuid import uuid4
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_crm_indexes'
down_revision = '4d4f8a88110d'  # Updated to the current head
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes to frequently queried CRM fields."""
    # Add index to Task.status
    op.create_index(
        op.f('ix_task_status'),
        'task',
        ['status'],
        unique=False
    )

    # Add index to Task.priority
    op.create_index(
        op.f('ix_task_priority'),
        'task',
        ['priority'],
        unique=False
    )

    # Add index to Task.due_date
    op.create_index(
        op.f('ix_task_due_date'),
        'task',
        ['due_date'],
        unique=False
    )

    # Add index to Opportunity.status
    op.create_index(
        op.f('ix_opportunity_status'),
        'opportunity',
        ['status'],
        unique=False
    )

    # Add index to Opportunity.expected_close_date
    op.create_index(
        op.f('ix_opportunity_expected_close_date'),
        'opportunity',
        ['expected_close_date'],
        unique=False
    )


def downgrade():
    """Remove indexes from CRM fields."""
    # Remove index from Task.status
    op.drop_index(
        op.f('ix_task_status'),
        table_name='task'
    )

    # Remove index from Task.priority
    op.drop_index(
        op.f('ix_task_priority'),
        table_name='task'
    )

    # Remove index from Task.due_date
    op.drop_index(
        op.f('ix_task_due_date'),
        table_name='task'
    )

    # Remove index from Opportunity.status
    op.drop_index(
        op.f('ix_opportunity_status'),
        table_name='opportunity'
    )

    # Remove index from Opportunity.expected_close_date
    op.drop_index(
        op.f('ix_opportunity_expected_close_date'),
        table_name='opportunity'
    )
