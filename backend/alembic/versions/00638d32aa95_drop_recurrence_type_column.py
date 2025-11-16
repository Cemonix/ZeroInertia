"""drop_recurrence_type_column

Revision ID: 00638d32aa95
Revises: 5298cd44f707
Create Date: 2025-11-16 13:29:39.544913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00638d32aa95'
down_revision: Union[str, Sequence[str], None] = '5298cd44f707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the deprecated recurrence_type column
    op.drop_column('tasks', 'recurrence_type')


def downgrade() -> None:
    """Downgrade schema."""
    # Restore the recurrence_type column for downgrade compatibility
    op.add_column('tasks', sa.Column('recurrence_type', sa.String(length=50), nullable=True))

    # Best-effort restoration of legacy recurrence_type from interval/unit
    op.execute(
        """
        UPDATE tasks
        SET recurrence_type = 'daily'
        WHERE recurrence_interval = 1 AND recurrence_unit = 'days'
        """
    )

    op.execute(
        """
        UPDATE tasks
        SET recurrence_type = 'alternate_days'
        WHERE recurrence_interval = 2 AND recurrence_unit = 'days'
        """
    )

    op.execute(
        """
        UPDATE tasks
        SET recurrence_type = 'weekly'
        WHERE recurrence_interval = 1 AND recurrence_unit = 'weeks'
        """
    )
