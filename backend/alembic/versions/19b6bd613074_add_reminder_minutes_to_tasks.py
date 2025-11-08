"""add_reminder_minutes_to_tasks

Revision ID: 19b6bd613074
Revises: 2060de53e342
Create Date: 2025-11-07 20:19:30.849596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19b6bd613074'
down_revision: Union[str, Sequence[str], None] = '2060de53e342'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add reminder_minutes field to tasks table."""
    op.add_column('tasks', sa.Column('reminder_minutes', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - Remove reminder_minutes field from tasks table."""
    op.drop_column('tasks', 'reminder_minutes')
