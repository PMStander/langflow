"""Add CRM product models

Revision ID: crm_product_models_migration
Revises: 4d4f8a88110d
Create Date: 2025-05-23 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'crm_product_models_migration'
down_revision: Union[str, None] = '4d4f8a88110d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Create product table
    if not migration.table_exists("product", conn):
        op.create_table(
            "product",
            sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("short_description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("sku", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("price", sa.Float(), nullable=False, server_default=sa.text("0.0")),
            sa.Column("regular_price", sa.Float(), nullable=False, server_default=sa.text("0.0")),
            sa.Column("sale_price", sa.Float(), nullable=True),
            sa.Column("on_sale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'publish'")),
            sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("catalog_visibility", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'visible'")),
            sa.Column("tax_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'taxable'")),
            sa.Column("tax_class", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("manage_stock", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("stock_quantity", sa.Integer(), nullable=True),
            sa.Column("stock_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'instock'")),
            sa.Column("backorders", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'no'")),
            sa.Column("backorders_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("backordered", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("weight", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("dimensions", sa.JSON(), nullable=True),
            sa.Column("shipping_class", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("shipping_class_id", sa.Integer(), nullable=True),
            sa.Column("virtual", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("downloadable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("downloads", sa.JSON(), nullable=True),
            sa.Column("download_limit", sa.Integer(), nullable=True, server_default=sa.text("-1")),
            sa.Column("download_expiry", sa.Integer(), nullable=True, server_default=sa.text("-1")),
            sa.Column("sold_individually", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("external_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("button_text", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("menu_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("purchasable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("images", sa.JSON(), nullable=True),
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["created_by"], ["user.id"], ),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"], ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_product_created_by", "product", ["created_by"], unique=False)
        op.create_index("ix_product_name", "product", ["name"], unique=False)
        op.create_index("ix_product_sku", "product", ["sku"], unique=False)
        op.create_index("ix_product_slug", "product", ["slug"], unique=False)
        op.create_index("ix_product_status", "product", ["status"], unique=False)
        op.create_index("ix_product_workspace_id", "product", ["workspace_id"], unique=False)
    
    # Create product_attribute table
    if not migration.table_exists("product_attribute", conn):
        op.create_table(
            "product_attribute",
            sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'select'")),
            sa.Column("order_by", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'menu_order'")),
            sa.Column("has_archives", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["created_by"], ["user.id"], ),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"], ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_product_attribute_created_by", "product_attribute", ["created_by"], unique=False)
        op.create_index("ix_product_attribute_name", "product_attribute", ["name"], unique=False)
        op.create_index("ix_product_attribute_slug", "product_attribute", ["slug"], unique=False)
        op.create_index("ix_product_attribute_workspace_id", "product_attribute", ["workspace_id"], unique=False)
    
    # Create product_category table
    if not migration.table_exists("product_category", conn):
        op.create_table(
            "product_category",
            sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("display", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'default'")),
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["created_by"], ["user.id"], ),
            sa.ForeignKeyConstraint(["parent_id"], ["product_category.id"], ),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"], ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_product_category_created_by", "product_category", ["created_by"], unique=False)
        op.create_index("ix_product_category_name", "product_category", ["name"], unique=False)
        op.create_index("ix_product_category_slug", "product_category", ["slug"], unique=False)
        op.create_index("ix_product_category_workspace_id", "product_category", ["workspace_id"], unique=False)
    
    # Create product_attribute_link table
    if not migration.table_exists("product_attribute_link", conn):
        op.create_table(
            "product_attribute_link",
            sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("attribute_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.ForeignKeyConstraint(["attribute_id"], ["product_attribute.id"], ),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"], ),
            sa.PrimaryKeyConstraint("product_id", "attribute_id"),
        )
    
    # Create product_attribute_term table
    if not migration.table_exists("product_attribute_term", conn):
        op.create_table(
            "product_attribute_term",
            sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("menu_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("attribute_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["attribute_id"], ["product_attribute.id"], ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_product_attribute_term_attribute_id", "product_attribute_term", ["attribute_id"], unique=False)
        op.create_index("ix_product_attribute_term_name", "product_attribute_term", ["name"], unique=False)
        op.create_index("ix_product_attribute_term_slug", "product_attribute_term", ["slug"], unique=False)
    
    # Create product_category_link table
    if not migration.table_exists("product_category_link", conn):
        op.create_table(
            "product_category_link",
            sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.ForeignKeyConstraint(["category_id"], ["product_category.id"], ),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"], ),
            sa.PrimaryKeyConstraint("product_id", "category_id"),
        )
    
    # Create product_meta table
    if not migration.table_exists("product_meta", conn):
        op.create_table(
            "product_meta",
            sa.Column("key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("value", sa.JSON(), nullable=True),
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"], ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_product_meta_key", "product_meta", ["key"], unique=False)
        op.create_index("ix_product_meta_product_id", "product_meta", ["product_id"], unique=False)
    
    # Create product_review table
    if not migration.table_exists("product_review", conn):
        op.create_table(
            "product_review",
            sa.Column("rating", sa.Integer(), nullable=False),
            sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("reviewer_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("reviewer_email", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("verified_purchase", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["created_by"], ["user.id"], ),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"], ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_product_review_created_by", "product_review", ["created_by"], unique=False)
        op.create_index("ix_product_review_product_id", "product_review", ["product_id"], unique=False)
    
    # Create product_variation table
    if not migration.table_exists("product_variation", conn):
        op.create_table(
            "product_variation",
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("sku", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("price", sa.Float(), nullable=False, server_default=sa.text("0.0")),
            sa.Column("regular_price", sa.Float(), nullable=False, server_default=sa.text("0.0")),
            sa.Column("sale_price", sa.Float(), nullable=True),
            sa.Column("on_sale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'publish'")),
            sa.Column("virtual", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("downloadable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("downloads", sa.JSON(), nullable=True),
            sa.Column("download_limit", sa.Integer(), nullable=True, server_default=sa.text("-1")),
            sa.Column("download_expiry", sa.Integer(), nullable=True, server_default=sa.text("-1")),
            sa.Column("tax_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'taxable'")),
            sa.Column("tax_class", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("manage_stock", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("stock_quantity", sa.Integer(), nullable=True),
            sa.Column("stock_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'instock'")),
            sa.Column("backorders", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=sa.text("'no'")),
            sa.Column("backorders_allowed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("backordered", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("weight", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("dimensions", sa.JSON(), nullable=True),
            sa.Column("shipping_class", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("shipping_class_id", sa.Integer(), nullable=True),
            sa.Column("menu_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("attributes", sa.JSON(), nullable=True),
            sa.Column("image", sa.JSON(), nullable=True),
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["product_id"], ["product.id"], ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_product_variation_product_id", "product_variation", ["product_id"], unique=False)
        op.create_index("ix_product_variation_sku", "product_variation", ["sku"], unique=False)
        op.create_index("ix_product_variation_status", "product_variation", ["status"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    
    # Drop tables in reverse order to avoid foreign key constraints
    if migration.table_exists("product_variation", conn):
        op.drop_table("product_variation")
    
    if migration.table_exists("product_review", conn):
        op.drop_table("product_review")
    
    if migration.table_exists("product_meta", conn):
        op.drop_table("product_meta")
    
    if migration.table_exists("product_category_link", conn):
        op.drop_table("product_category_link")
    
    if migration.table_exists("product_attribute_term", conn):
        op.drop_table("product_attribute_term")
    
    if migration.table_exists("product_attribute_link", conn):
        op.drop_table("product_attribute_link")
    
    if migration.table_exists("product_category", conn):
        op.drop_table("product_category")
    
    if migration.table_exists("product_attribute", conn):
        op.drop_table("product_attribute")
    
    if migration.table_exists("product", conn):
        op.drop_table("product")
