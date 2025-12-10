"""add fcm_token to users

Revision ID: add_fcm_token_001
Revises: 031a8506720a
Create Date: 2025-12-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_fcm_token_001'
down_revision: Union[str, None] = '031a8506720a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users 테이블에 fcm_token 컬럼 추가
    op.add_column('users', sa.Column('fcm_token', sa.String(255), nullable=True))


def downgrade() -> None:
    # fcm_token 컬럼 삭제
    op.drop_column('users', 'fcm_token')

