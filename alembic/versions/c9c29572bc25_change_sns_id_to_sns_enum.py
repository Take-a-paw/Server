"""Change sns_id to sns enum

Revision ID: c9c29572bc25
Revises: 773a678e238b
Create Date: 2025-11-19 04:03:22.504911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9c29572bc25'
down_revision: Union[str, None] = '773a678e238b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
