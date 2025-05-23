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

            # Use batch operations for SQLite compatibility
            with op.batch_alter_table("folder", schema=None) as batch_op:
                batch_op.create_foreign_key(None, "workspace", ["workspace_id"], ["id"])
                batch_op.create_index("ix_folder_workspace_id", ["workspace_id"], unique=False)

                # Check if the constraint exists before trying to drop it
                constraints = inspector.get_unique_constraints("folder")
                constraint_names = [constraint['name'] for constraint in constraints]

                if "unique_folder_name" in constraint_names:
                    batch_op.drop_constraint("unique_folder_name", type_="unique")

                batch_op.create_unique_constraint("unique_folder_name_per_workspace", ["user_id", "name", "workspace_id"])

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
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore

    # Remove workspace_id from folder table
    with op.batch_alter_table("folder", schema=None) as batch_op:
        # Check if the constraint exists before trying to drop it
        constraints = inspector.get_unique_constraints("folder")
        constraint_names = [constraint['name'] for constraint in constraints]

        if "unique_folder_name_per_workspace" in constraint_names:
            batch_op.drop_constraint("unique_folder_name_per_workspace", type_="unique")
            batch_op.create_unique_constraint("unique_folder_name", ["user_id", "name"])

        # Check if the index exists before trying to drop it
        indexes = inspector.get_indexes("folder")
        index_names = [index['name'] for index in indexes]

        if "ix_folder_workspace_id" in index_names:
            batch_op.drop_index("ix_folder_workspace_id")

        # Check for foreign keys
        foreign_keys = inspector.get_foreign_keys("folder")
        for fk in foreign_keys:
            if fk.get('referred_table') == 'workspace' and 'workspace_id' in fk.get('constrained_columns', []):
                batch_op.drop_constraint(fk.get('name'), type_="foreignkey")

    # Check if the column exists before trying to drop it
    columns = [c["name"] for c in inspector.get_columns("folder")]
    if "workspace_id" in columns:
        op.drop_column("folder", "workspace_id")

    # Drop workspace_member table if it exists
    if "workspace_member" in inspector.get_table_names():
        op.drop_table("workspace_member")

    # Drop workspace table if it exists
    if "workspace" in inspector.get_table_names():
        # Check if the index exists before trying to drop it
        indexes = inspector.get_indexes("workspace")
        index_names = [index['name'] for index in indexes]

        if "ix_workspace_name" in index_names:
            op.drop_index(op.f("ix_workspace_name"), "workspace")

        op.drop_table("workspace")
