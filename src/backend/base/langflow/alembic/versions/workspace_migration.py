"""Add workspace tables

Revision ID: workspace_migration
Revises: 012fb73ac359
Create Date: 2024-06-01 00:00:00.000000

"""
from datetime import datetime, timezone

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "workspace_migration"
down_revision = "012fb73ac359"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore
    table_names = inspector.get_table_names()

    # Create workspace table
    if "workspace" not in table_names:
        op.create_table(
            "workspace",
            sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column("id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column("owner_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["owner_id"],
                ["user.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("owner_id", "name", name="unique_workspace_name"),
        )

        # Create index on workspace name
        op.create_index(op.f("ix_workspace_name"), "workspace", ["name"], unique=False)

    # Create workspace_member table
    if "workspace_member" not in table_names:
        op.create_table(
            "workspace_member",
            sa.Column("workspace_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column("user_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
            sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["workspace_id"],
                ["workspace.id"],
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["user.id"],
            ),
            sa.PrimaryKeyConstraint("workspace_id", "user_id"),
        )

    # Add workspace_id to folder table
    if "folder" in table_names:
        columns = [c["name"] for c in inspector.get_columns("folder")]
        if "workspace_id" not in columns:
            op.add_column("folder", sa.Column("workspace_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=True))
            op.create_foreign_key(None, "folder", "workspace", ["workspace_id"], ["id"])
            op.create_index(op.f("ix_folder_workspace_id"), "folder", ["workspace_id"], unique=False)

            # Update unique constraint on folder table
            op.drop_constraint("unique_folder_name", "folder")
            op.create_unique_constraint("unique_folder_name_per_workspace", "folder", ["user_id", "name", "workspace_id"])

    # Create personal workspace for each existing user
    conn = op.get_bind()
    users = conn.execute(sa.text("SELECT id, username FROM \"user\"")).fetchall()

    for user in users:
        user_id = user[0]
        username = user[1]

        # Create personal workspace
        workspace_id_result = conn.execute(sa.text("SELECT uuid_generate_v4()"))
        workspace_id = workspace_id_result.scalar()
        now = datetime.now(timezone.utc)

        conn.execute(
            sa.text(
                """
                INSERT INTO workspace (id, name, description, owner_id, created_at, updated_at)
                VALUES (:id, :name, :description, :owner_id, :created_at, :updated_at)
                """
            ),
            {
                "id": workspace_id,
                "name": "Personal",
                "description": f"Personal workspace for {username}",
                "owner_id": user_id,
                "created_at": now,
                "updated_at": now,
            },
        )

        # Add user as owner of their personal workspace
        conn.execute(
            sa.text(
                """
                INSERT INTO workspace_member (workspace_id, user_id, role, created_at)
                VALUES (:workspace_id, :user_id, :role, :created_at)
                """
            ),
            {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "role": "owner",
                "created_at": now,
            },
        )

        # Migrate existing folders to personal workspace
        conn.execute(
            sa.text(
                """
                UPDATE folder
                SET workspace_id = :workspace_id
                WHERE user_id = :user_id
                """
            ),
            {
                "workspace_id": workspace_id,
                "user_id": user_id,
            },
        )


def downgrade() -> None:
    # Remove workspace_id from folder table
    op.drop_constraint("unique_folder_name_per_workspace", "folder")
    op.create_unique_constraint("unique_folder_name", "folder", ["user_id", "name"])
    op.drop_index(op.f("ix_folder_workspace_id"), "folder")
    op.drop_constraint(None, "folder", type_="foreignkey")
    op.drop_column("folder", "workspace_id")

    # Drop workspace_member table
    op.drop_table("workspace_member")

    # Drop workspace table
    op.drop_index(op.f("ix_workspace_name"), "workspace")
    op.drop_table("workspace")
