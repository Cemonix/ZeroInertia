"""redesign_media_tables_to_separate_clean_schema

Revision ID: 735313b8c25e
Revises: 00638d32aa95
Create Date: 2025-11-18 16:47:27.653093

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '735313b8c25e'
down_revision: Union[str, Sequence[str], None] = '00638d32aa95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create new books_v2 table (no inheritance, clean schema)
    _ = op.create_table(
        'books_v2',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('creator', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='planned'),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name='chk_books_status')
    )
    op.create_index('idx_books_user', 'books_v2', ['user_id'])
    op.create_index('idx_books_status', 'books_v2', ['user_id', 'status'])
    op.create_index('idx_books_completed', 'books_v2', ['user_id', 'completed_at'])
    op.create_index('idx_books_title', 'books_v2', ['title'])

    # Create new games_v2 table
    _ = op.create_table(
        'games_v2',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='planned'),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.Column('platform', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name='chk_games_status')
    )
    op.create_index('idx_games_user', 'games_v2', ['user_id'])
    op.create_index('idx_games_status', 'games_v2', ['user_id', 'status'])
    op.create_index('idx_games_completed', 'games_v2', ['user_id', 'completed_at'])
    op.create_index('idx_games_title', 'games_v2', ['title'])

    # Create new movies_v2 table
    _ = op.create_table(
        'movies_v2',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='planned'),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name='chk_movies_status')
    )
    op.create_index('idx_movies_user', 'movies_v2', ['user_id'])
    op.create_index('idx_movies_status', 'movies_v2', ['user_id', 'status'])
    op.create_index('idx_movies_completed', 'movies_v2', ['user_id', 'completed_at'])
    op.create_index('idx_movies_title', 'movies_v2', ['title'])

    # Create new shows_v2 table
    _ = op.create_table(
        'shows_v2',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('season_number', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='planned'),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name='chk_shows_status')
    )
    op.create_index('idx_shows_user', 'shows_v2', ['user_id'])
    op.create_index('idx_shows_status', 'shows_v2', ['user_id', 'status'])
    op.create_index('idx_shows_completed', 'shows_v2', ['user_id', 'completed_at'])
    op.create_index('idx_shows_title', 'shows_v2', ['title'])

    # Migrate data from old schema to new schema
    # Books: old books table joined with media
    op.execute("""
        INSERT INTO books_v2 (id, user_id, title, creator, status, genre, started_at, completed_at, notes, created_at, updated_at)
        SELECT
            b.id,
            m.user_id,
            m.title,
            COALESCE(b.author, 'Unknown'),
            m.status,
            NULL as genre,
            m.started_at,
            m.completed_at,
            m.notes,
            m.created_at,
            m.updated_at
        FROM books b
        INNER JOIN media m ON b.id = m.id
        WHERE m.media_type = 'book'
    """)

    # Games: old games table joined with media
    op.execute("""
        INSERT INTO games_v2 (id, user_id, title, status, genre, platform, started_at, completed_at, notes, created_at, updated_at)
        SELECT
            g.id,
            m.user_id,
            m.title,
            m.status,
            g.genre,
            g.platform,
            m.started_at,
            m.completed_at,
            m.notes,
            m.created_at,
            m.updated_at
        FROM games g
        INNER JOIN media m ON g.id = m.id
        WHERE m.media_type = 'game'
    """)

    # Movies: old movies table joined with media
    op.execute("""
        INSERT INTO movies_v2 (id, user_id, title, status, genre, started_at, completed_at, notes, created_at, updated_at)
        SELECT
            mv.id,
            m.user_id,
            m.title,
            m.status,
            mv.genre,
            m.started_at,
            m.completed_at,
            m.notes,
            m.created_at,
            m.updated_at
        FROM movies mv
        INNER JOIN media m ON mv.id = m.id
        WHERE m.media_type = 'movie'
    """)

    # Shows: old shows table joined with media
    op.execute("""
        INSERT INTO shows_v2 (id, user_id, title, season_number, status, genre, started_at, completed_at, notes, created_at, updated_at)
        SELECT
            s.id,
            m.user_id,
            m.title,
            s.season_number,
            m.status,
            s.genre,
            m.started_at,
            m.completed_at,
            m.notes,
            m.created_at,
            m.updated_at
        FROM shows s
        INNER JOIN media m ON s.id = m.id
        WHERE m.media_type = 'show'
    """)

    # Drop old tables (inheritance pattern)
    op.drop_table('books')
    op.drop_table('games')
    op.drop_table('movies')
    op.drop_table('shows')
    op.drop_index('ix_media_user_id', table_name='media')
    op.drop_index('ix_media_status', table_name='media')
    op.drop_index('ix_media_media_type', table_name='media')
    op.drop_table('media')

    # Rename new tables to final names
    op.rename_table('books_v2', 'books')
    op.rename_table('games_v2', 'games')
    op.rename_table('movies_v2', 'movies')
    op.rename_table('shows_v2', 'shows')


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate old media base table
    _ = op.create_table(
        'media',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('media_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_media_media_type', 'media', ['media_type'])
    op.create_index('ix_media_status', 'media', ['status'])
    op.create_index('ix_media_user_id', 'media', ['user_id'])

    # Rename current tables to temp names
    op.rename_table('books', 'books_v2')
    op.rename_table('games', 'games_v2')
    op.rename_table('movies', 'movies_v2')
    op.rename_table('shows', 'shows_v2')

    # Recreate old child tables
    _ = op.create_table(
        'books',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('pages', sa.Integer(), nullable=True),
        sa.Column('isbn', sa.String(length=20), nullable=True),
        sa.Column('publisher', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['media.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    _ = op.create_table(
        'games',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('platform', sa.String(length=100), nullable=True),
        sa.Column('developer', sa.String(length=255), nullable=True),
        sa.Column('playtime_hours', sa.Integer(), nullable=True),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.Column('is_100_percent', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['media.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    _ = op.create_table(
        'movies',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('director', sa.String(length=255), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['media.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    _ = op.create_table(
        'shows',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('season_number', sa.Integer(), nullable=True),
        sa.Column('episodes', sa.Integer(), nullable=True),
        sa.Column('creator', sa.String(length=255), nullable=True),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('genre', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['media.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Migrate data back to old schema
    # Note: This will lose data that doesn't fit old schema (genre for books, etc.)
    op.execute("""
        INSERT INTO media (id, user_id, media_type, title, status, rating, started_at, completed_at, notes, created_at, updated_at)
        SELECT id, user_id, 'book'::varchar, title, status, NULL, started_at, completed_at, notes, created_at, updated_at
        FROM books_v2
    """)

    op.execute("""
        INSERT INTO books (id, author, pages, isbn, publisher)
        SELECT id, creator, NULL, NULL, NULL
        FROM books_v2
    """)

    op.execute("""
        INSERT INTO media (id, user_id, media_type, title, status, rating, started_at, completed_at, notes, created_at, updated_at)
        SELECT id, user_id, 'game'::varchar, title, status, NULL, started_at, completed_at, notes, created_at, updated_at
        FROM games_v2
    """)

    op.execute("""
        INSERT INTO games (id, platform, developer, playtime_hours, genre, is_100_percent)
        SELECT id, platform, NULL, NULL, genre, FALSE
        FROM games_v2
    """)

    op.execute("""
        INSERT INTO media (id, user_id, media_type, title, status, rating, started_at, completed_at, notes, created_at, updated_at)
        SELECT id, user_id, 'movie'::varchar, title, status, NULL, started_at, completed_at, notes, created_at, updated_at
        FROM movies_v2
    """)

    op.execute("""
        INSERT INTO movies (id, director, duration_minutes, release_year, genre)
        SELECT id, NULL, NULL, NULL, genre
        FROM movies_v2
    """)

    op.execute("""
        INSERT INTO media (id, user_id, media_type, title, status, rating, started_at, completed_at, notes, created_at, updated_at)
        SELECT id, user_id, 'show'::varchar, title, status, NULL, started_at, completed_at, notes, created_at, updated_at
        FROM shows_v2
    """)

    op.execute("""
        INSERT INTO shows (id, season_number, episodes, creator, release_year, genre)
        SELECT id, season_number, NULL, NULL, NULL, genre
        FROM shows_v2
    """)

    # Drop v2 tables
    op.drop_table('books_v2')
    op.drop_table('games_v2')
    op.drop_table('movies_v2')
    op.drop_table('shows_v2')
