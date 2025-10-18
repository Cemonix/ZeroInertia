"""Add tasks table

Revision ID: 1fb94fa770c0
Revises: 13b2fc61bdca
Create Date: 2025-10-10 17:31:31.263797

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1fb94fa770c0'
down_revision: str | Sequence[str] | None = '13b2fc61bdca'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    _ = op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_done', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_tasks_user_id', 'tasks')
    op.drop_table('tasks')
