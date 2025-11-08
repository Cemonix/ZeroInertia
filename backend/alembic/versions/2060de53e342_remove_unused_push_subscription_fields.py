"""remove_unused_push_subscription_fields

Revision ID: 2060de53e342
Revises: 590197257ef2
Create Date: 2025-11-07 19:59:12.366692

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2060de53e342'
down_revision: Union[str, Sequence[str], None] = '590197257ef2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Remove unused p256dh_key and auth_key fields."""
    # Drop columns that are not used with FCM
    op.drop_column('push_subscriptions', 'p256dh_key')
    op.drop_column('push_subscriptions', 'auth_key')


def downgrade() -> None:
    """Downgrade schema - Re-add p256dh_key and auth_key fields."""
    op.add_column('push_subscriptions', sa.Column('auth_key', sa.Text(), nullable=False, server_default=''))
    op.add_column('push_subscriptions', sa.Column('p256dh_key', sa.Text(), nullable=False, server_default=''))

    # Remove server defaults after column creation
    op.alter_column('push_subscriptions', 'auth_key', server_default=None)
    op.alter_column('push_subscriptions', 'p256dh_key', server_default=None)
