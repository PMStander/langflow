"""merge crm product models

Revision ID: merge_crm_product_models
Revises: 4d4f8a88110d, crm_product_models_migration
Create Date: 2025-05-23 19:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration


# revision identifiers, used by Alembic.
revision: str = 'merge_crm_product_models'
down_revision: Union[str, None] = ('4d4f8a88110d', 'crm_product_models_migration')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    pass


def downgrade() -> None:
    conn = op.get_bind()
    pass
