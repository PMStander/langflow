"""Create CRM tables

Revision ID: crm_tables_migration
Revises: workspace_migration
Create Date: 2025-05-24 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = 'crm_tables_migration'
down_revision = 'workspace_migration'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore
    table_names = inspector.get_table_names()
    
    # Create client table
    if "client" not in table_names:
        op.create_table(
            'client',
            sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('company', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('workspace_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('created_by', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_client_name'), 'client', ['name'], unique=False)
        op.create_index(op.f('ix_client_workspace_id'), 'client', ['workspace_id'], unique=False)
        op.create_index(op.f('ix_client_created_by'), 'client', ['created_by'], unique=False)
    
    # Create invoice table
    if "invoice" not in table_names:
        op.create_table(
            'invoice',
            sa.Column('invoice_number', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('issue_date', sa.DateTime(), nullable=False),
            sa.Column('due_date', sa.DateTime(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('workspace_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('client_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('created_by', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
            sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_invoice_invoice_number'), 'invoice', ['invoice_number'], unique=False)
        op.create_index(op.f('ix_invoice_workspace_id'), 'invoice', ['workspace_id'], unique=False)
        op.create_index(op.f('ix_invoice_client_id'), 'invoice', ['client_id'], unique=False)
        op.create_index(op.f('ix_invoice_created_by'), 'invoice', ['created_by'], unique=False)
    
    # Create opportunity table
    if "opportunity" not in table_names:
        op.create_table(
            'opportunity',
            sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('value', sa.Float(), nullable=True),
            sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('expected_close_date', sa.DateTime(), nullable=True),
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('workspace_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('client_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('created_by', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
            sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_opportunity_name'), 'opportunity', ['name'], unique=False)
        op.create_index(op.f('ix_opportunity_workspace_id'), 'opportunity', ['workspace_id'], unique=False)
        op.create_index(op.f('ix_opportunity_client_id'), 'opportunity', ['client_id'], unique=False)
        op.create_index(op.f('ix_opportunity_created_by'), 'opportunity', ['created_by'], unique=False)
    
    # Create task table
    if "task" not in table_names:
        op.create_table(
            'task',
            sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('priority', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('due_date', sa.DateTime(), nullable=True),
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('workspace_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('created_by', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('assigned_to', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.Column('client_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.Column('invoice_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.Column('opportunity_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
            sa.ForeignKeyConstraint(['assigned_to'], ['user.id'], ),
            sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
            sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ),
            sa.ForeignKeyConstraint(['opportunity_id'], ['opportunity.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_task_title'), 'task', ['title'], unique=False)
        op.create_index(op.f('ix_task_workspace_id'), 'task', ['workspace_id'], unique=False)
        op.create_index(op.f('ix_task_created_by'), 'task', ['created_by'], unique=False)
        op.create_index(op.f('ix_task_client_id'), 'task', ['client_id'], unique=False)
        op.create_index(op.f('ix_task_invoice_id'), 'task', ['invoice_id'], unique=False)
        op.create_index(op.f('ix_task_opportunity_id'), 'task', ['opportunity_id'], unique=False)


def downgrade():
    # Drop tables in reverse order to avoid foreign key constraints
    op.drop_table('task')
    op.drop_table('opportunity')
    op.drop_table('invoice')
    op.drop_table('client')
