"""remove_season_number_from_shows

Revision ID: be6476d7e8f3
Revises: 09ce8d147243
Create Date: 2025-12-13 22:57:36.801600

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'be6476d7e8f3'
down_revision: Union[str, Sequence[str], None] = '09ce8d147243'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('shows', 'season_number')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('shows', sa.Column('season_number', sa.Integer(), nullable=True))
