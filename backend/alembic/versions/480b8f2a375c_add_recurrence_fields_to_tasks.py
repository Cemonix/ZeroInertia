"""add_recurrence_fields_to_tasks

Revision ID: 480b8f2a375c
Revises: 83c6bc227569
Create Date: 2025-11-06 19:33:57.262197

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '480b8f2a375c'
down_revision: Union[str, Sequence[str], None] = '83c6bc227569'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add recurrence fields to tasks table
    op.add_column('tasks', sa.Column('recurrence_type', sa.String(length=50), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_days', sa.ARRAY(sa.Integer()), nullable=True))

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Drop the foreign key constraint on recurring_task_id if it exists under any known name
    constraint_names = {'tasks_recurring_task_id_fkey', 'fk_tasks_recurring_task_id'}
    existing_constraints = {
        fk['name']
        for fk in inspector.get_foreign_keys('tasks')
        if fk.get('name')
    }
    for constraint_name in constraint_names & existing_constraints:
        op.drop_constraint(constraint_name, 'tasks', type_='foreignkey')

    # Drop the recurring_task_id column if present
    task_columns = {column['name'] for column in inspector.get_columns('tasks')}
    if 'recurring_task_id' in task_columns:
        op.drop_column('tasks', 'recurring_task_id')

    # Drop the recurring_tasks table entirely (no longer needed)
    if inspector.has_table('recurring_tasks'):
        op.drop_table('recurring_tasks')


def downgrade() -> None:
    """Downgrade schema."""
    # Note: This downgrade recreates the recurring_tasks table structure
    _ = op.create_table(
        'recurring_tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('recurrence_type', sa.String(length=50), nullable=False),
        sa.Column('recurrence_days', sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column('recurrence_time', sa.Time(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('last_generated_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('section_id', sa.UUID(), nullable=False),
        sa.Column('priority_id', sa.UUID(), nullable=True),
        sa.Column('label_ids', sa.ARRAY(sa.UUID()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Restore recurring_task_id column
    op.add_column('tasks', sa.Column('recurring_task_id', sa.UUID(), nullable=True))

    # Restore foreign key constraint
    op.create_foreign_key(
        'tasks_recurring_task_id_fkey',
        'tasks',
        'recurring_tasks',
        ['recurring_task_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Remove new recurrence fields
    op.drop_column('tasks', 'recurrence_days')
    op.drop_column('tasks', 'recurrence_type')
