"""add missing is_active columns

Revision ID: 0123456789ab
Revises: 137d8c1521c9
Create Date: 2026-06-19 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0123456789ab'
down_revision: Union[str, Sequence[str], None] = '137d8c1521c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.add_column('products', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'is_active')
    op.drop_column('products', 'is_active')
    op.drop_column('categories', 'is_active')
