"""Change sns_id to sns enum

Revision ID: e809d5361851
Revises: 6cc1fc8cdac6
Create Date: 2025-11-19 04:01:35.629864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e809d5361851'
down_revision: Union[str, None] = '6cc1fc8cdac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
