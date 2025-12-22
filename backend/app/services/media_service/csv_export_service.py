import csv
from io import StringIO
from typing import TypeVar, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.genre import Genre
from app.models.media import Anime, Book, Game, Manga, Movie, Show
from app.services.media_service.base import get_all_by_user

MediaModel = TypeVar("MediaModel", Anime, Book, Game, Manga, Movie, Show)


def export_books_csv(books: list[Book]) -> str:
    """Export books to CSV format"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "title",
        "creator",
        "status",
        "is_audiobook",
        "genres",
        "started_at",
        "completed_at",
        "notes"
    ])

    for book in books:
        book_genres = cast(list[Genre], book.genres)
        genres_str = ", ".join(genre.name for genre in book_genres) if book_genres else ""
        writer.writerow([
            book.title,
            book.creator,
            book.status,
            "true" if book.is_audiobook else "false",
            genres_str,
            book.started_at.isoformat() if book.started_at else "",
            book.completed_at.isoformat() if book.completed_at else "",
            book.notes or ""
        ])

    return output.getvalue()


def export_movies_csv(movies: list[Movie]) -> str:
    """Export movies to CSV format"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "title",
        "status",
        "genres",
        "completed_at",
        "notes"
    ])

    for movie in movies:
        movie_genres = cast(list[Genre], movie.genres)
        genres_str = ", ".join(genre.name for genre in movie_genres) if movie_genres else ""
        writer.writerow([
            movie.title,
            movie.status,
            genres_str,
            movie.completed_at.isoformat() if movie.completed_at else "",
            movie.notes or ""
        ])

    return output.getvalue()


def export_games_csv(games: list[Game]) -> str:
    """Export games to CSV format"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "title",
        "status",
        "platform",
        "genres",
        "started_at",
        "completed_at",
        "notes"
    ])

    for game in games:
        game_genres = cast(list[Genre], game.genres)
        genres_str = ", ".join(genre.name for genre in game_genres) if game_genres else ""
        writer.writerow([
            game.title,
            game.status,
            game.platform or "",
            genres_str,
            game.started_at.isoformat() if game.started_at else "",
            game.completed_at.isoformat() if game.completed_at else "",
            game.notes or ""
        ])

    return output.getvalue()


def export_shows_csv(shows: list[Show]) -> str:
    """Export TV shows to CSV format"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "title",
        "status",
        "genres",
        "started_at",
        "completed_at",
        "notes"
    ])

    for show in shows:
        show_genres = cast(list[Genre], show.genres)
        genres_str = ", ".join(genre.name for genre in show_genres) if show_genres else ""
        writer.writerow([
            show.title,
            show.status,
            genres_str,
            show.started_at.isoformat() if show.started_at else "",
            show.completed_at.isoformat() if show.completed_at else "",
            show.notes or ""
        ])

    return output.getvalue()


def export_manga_csv(manga_list: list[Manga]) -> str:
    """Export manga to CSV format"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "title",
        "author",
        "status",
        "genres",
        "started_at",
        "completed_at",
        "notes"
    ])

    for manga in manga_list:
        manga_genres = cast(list[Genre], manga.genres)
        genres_str = ", ".join(genre.name for genre in manga_genres) if manga_genres else ""
        writer.writerow([
            manga.title,
            manga.author or "",
            manga.status,
            genres_str,
            manga.started_at.isoformat() if manga.started_at else "",
            manga.completed_at.isoformat() if manga.completed_at else "",
            manga.notes or ""
        ])

    return output.getvalue()


def export_anime_csv(anime_list: list[Anime]) -> str:
    """Export anime to CSV format"""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "title",
        "episodes",
        "status",
        "genres",
        "started_at",
        "completed_at",
        "notes"
    ])

    for anime in anime_list:
        anime_genres = cast(list[Genre], anime.genres)
        genres_str = ", ".join(genre.name for genre in anime_genres) if anime_genres else ""
        writer.writerow([
            anime.title,
            anime.episodes if anime.episodes is not None else "",
            anime.status,
            genres_str,
            anime.started_at.isoformat() if anime.started_at else "",
            anime.completed_at.isoformat() if anime.completed_at else "",
            anime.notes or ""
        ])

    return output.getvalue()


async def export_books_for_user(db: AsyncSession, user_id: UUID) -> str:
    """Get all books for a user and export to CSV"""
    books = await get_all_by_user(db, user_id, Book)
    return export_books_csv(list(books))


async def export_movies_for_user(db: AsyncSession, user_id: UUID) -> str:
    """Get all movies for a user and export to CSV"""
    movies = await get_all_by_user(db, user_id, Movie)
    return export_movies_csv(list(movies))


async def export_games_for_user(db: AsyncSession, user_id: UUID) -> str:
    """Get all games for a user and export to CSV"""
    games = await get_all_by_user(db, user_id, Game)
    return export_games_csv(list(games))


async def export_shows_for_user(db: AsyncSession, user_id: UUID) -> str:
    """Get all TV shows for a user and export to CSV"""
    shows = await get_all_by_user(db, user_id, Show)
    return export_shows_csv(list(shows))


async def export_manga_for_user(db: AsyncSession, user_id: UUID) -> str:
    """Get all manga for a user and export to CSV"""
    manga = await get_all_by_user(db, user_id, Manga)
    return export_manga_csv(list(manga))


async def export_anime_for_user(db: AsyncSession, user_id: UUID) -> str:
    """Get all anime for a user and export to CSV"""
    anime = await get_all_by_user(db, user_id, Anime)
    return export_anime_csv(list(anime))
