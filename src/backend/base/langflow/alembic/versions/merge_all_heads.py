"""merge all heads

Revision ID: merge_all_heads
Revises: 325df5b9eb02, merge_crm_product_models
Create Date: 2025-05-23 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration


# revision identifiers, used by Alembic.
revision: str = 'merge_all_heads'
down_revision: Union[str, None] = ('325df5b9eb02', 'merge_crm_product_models')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    pass


def downgrade() -> None:
    conn = op.get_bind()
    pass
