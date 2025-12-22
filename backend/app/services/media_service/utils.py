from datetime import date
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Anime, Book, Game, Manga, Movie, Show


async def check_duplicate(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    media_type: str
) -> list[dict[str, str | None]]:
    """Check for similar titles within a specific media type"""
    media_type_map = {
        "book": Book,
        "game": Game,
        "movie": Movie,
        "show": Show,
        "manga": Manga,
        "anime": Anime
    }

    model = media_type_map.get(media_type)
    if not model:
        raise ValueError(f"Invalid media type: {media_type}")

    result = await db.execute(
        select(model)
        .where(model.user_id == user_id)
        .where(model.title.ilike(f"%{title}%"))
    )
    matches = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "title": m.title,
            "status": m.status,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None
        }
        for m in matches
    ]


async def get_yearly_stats(
    db: AsyncSession,
    user_id: UUID,
    year: int
) -> dict[str, int]:
    """Get completion counts for all media types for a given year"""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    stats: dict[str, int] = {}
    for name, model in [("books", Book), ("games", Game), ("manga", Manga), ("anime", Anime), ("movies", Movie), ("shows", Show)]:
        result = await db.execute(
            select(func.count(model.id))
            .where(model.user_id == user_id)
            .where(model.completed_at.between(start_date, end_date))
        )
        stats[name] = result.scalar() or 0

    return stats


async def search_media(
    db: AsyncSession,
    user_id: UUID,
    query: str,
    media_type: str | None = None
) -> dict[str, list[Book | Game | Manga | Anime | Movie | Show]]:
    """Search across all media types by title"""
    results: dict[str, list[Book | Game | Manga | Anime | Movie | Show]] = {"books": [], "games": [], "manga": [], "anime": [], "movies": [], "shows": []}
    search_term = f"%{query}%"

    models_to_search: list[tuple[str, type[Book] | type[Game] | type[Manga] | type[Anime] | type[Movie] | type[Show]]] = []
    if media_type is None:
        models_to_search = [
            ("books", Book), ("games", Game), ("manga", Manga), ("anime", Anime), ("movies", Movie), ("shows", Show)
        ]
    elif media_type == "book":
        models_to_search = [("books", Book)]
    elif media_type == "game":
        models_to_search = [("games", Game)]
    elif media_type == "manga":
        models_to_search = [("manga", Manga)]
    elif media_type == "anime":
        models_to_search = [("anime", Anime)]
    elif media_type == "movie":
        models_to_search = [("movies", Movie)]
    elif media_type == "show":
        models_to_search = [("shows", Show)]

    for name, model in models_to_search:
        search_conditions = [model.title.ilike(search_term)]
        if hasattr(model, "notes"):
            search_conditions.append(model.notes.ilike(search_term))

        result = await db.execute(
            select(model)
            .where(model.user_id == user_id)
            .where(or_(*search_conditions))
            .limit(20)
        )
        results[name] = list(result.scalars().all())

    return results
