"""Add book creator tables

Revision ID: add_book_creator_tables
Revises: 4d4f8a88110d
Create Date: 2025-05-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = 'add_book_creator_tables'
down_revision = '4d4f8a88110d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore
    table_names = inspector.get_table_names()
    
    # Create book table
    if "book" not in table_names:
        op.create_table(
            'book',
            sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('book_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('dimensions', sa.JSON(), nullable=False),
            sa.Column('page_count', sa.Integer(), nullable=False),
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('user_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('workspace_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspace.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_book_name'), 'book', ['name'], unique=False)
        op.create_index(op.f('ix_book_book_type'), 'book', ['book_type'], unique=False)
        op.create_index(op.f('ix_book_user_id'), 'book', ['user_id'], unique=False)
        op.create_index(op.f('ix_book_workspace_id'), 'book', ['workspace_id'], unique=False)
    
    # Create book_cover table
    if "book_cover" not in table_names:
        op.create_table(
            'book_cover',
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('book_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('front_design', sa.JSON(), nullable=False),
            sa.Column('back_design', sa.JSON(), nullable=False),
            sa.Column('spine_design', sa.JSON(), nullable=False),
            sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('book_id'),
            sa.UniqueConstraint('id')
        )
    
    # Create book_interior table
    if "book_interior" not in table_names:
        op.create_table(
            'book_interior',
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('book_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('template_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.Column('layout_settings', sa.JSON(), nullable=False),
            sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('book_id'),
            sa.UniqueConstraint('id')
        )
    
    # Create book_template table
    if "book_template" not in table_names:
        op.create_table(
            'book_template',
            sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('template_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('is_system', sa.Boolean(), nullable=False),
            sa.Column('content', sa.JSON(), nullable=False),
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('user_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_book_template_name'), 'book_template', ['name'], unique=False)
        op.create_index(op.f('ix_book_template_category'), 'book_template', ['category'], unique=False)
        op.create_index(op.f('ix_book_template_template_type'), 'book_template', ['template_type'], unique=False)
    
    # Create book_page table
    if "book_page" not in table_names:
        op.create_table(
            'book_page',
            sa.Column('id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('book_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column('page_number', sa.Integer(), nullable=False),
            sa.Column('content', sa.JSON(), nullable=False),
            sa.Column('template_id', sqlmodel.sql.sqltypes.types.Uuid(), nullable=True),
            sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
            sa.ForeignKeyConstraint(['template_id'], ['book_template.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('id')
        )
        
        # Create indexes
        op.create_index(op.f('ix_book_page_book_id'), 'book_page', ['book_id'], unique=False)
        op.create_index(op.f('ix_book_page_page_number'), 'book_page', ['page_number'], unique=False)
    
    # Add foreign key constraints for book_interior.template_id
    if "book_interior" in table_names and "book_template" in table_names:
        with op.batch_alter_table('book_interior', schema=None) as batch_op:
            batch_op.create_foreign_key('fk_book_interior_template_id', 'book_template', ['template_id'], ['id'])


def downgrade() -> None:
    # Drop tables in reverse order to avoid foreign key constraints
    op.drop_table('book_page')
    op.drop_table('book_interior')
    op.drop_table('book_cover')
    op.drop_table('book_template')
    op.drop_table('book')
