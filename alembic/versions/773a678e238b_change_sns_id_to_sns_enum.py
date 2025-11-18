"""Change sns_id to sns enum

Revision ID: 773a678e238b
Revises: e809d5361851
Create Date: 2025-11-19 04:01:39.497982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '773a678e238b'
down_revision: Union[str, None] = 'e809d5361851'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
