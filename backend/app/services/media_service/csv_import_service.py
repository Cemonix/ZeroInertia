import csv
from io import StringIO
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException
from app.core.settings.app_settings import get_app_settings
from app.models.genre import Genre
from app.models.media import Anime, Book, Game, Manga, Movie, Show
from app.schemas.media import CSVImportResult, MediaStatus

MediaModel = TypeVar("MediaModel", Anime, Book, Game, Manga, Movie, Show)

# pyright: reportAny=false


def validate_csv_file_size(file_size_bytes: int) -> None:
    """Validate that the CSV file size is within acceptable limits"""
    settings = get_app_settings()
    max_size_bytes = settings.max_csv_file_size_mb * 1024 * 1024

    if file_size_bytes > max_size_bytes:
        raise BadRequestException(
            f"CSV file size ({file_size_bytes / 1024 / 1024:.2f} MB) exceeds maximum allowed size " +
            f"of {settings.max_csv_file_size_mb} MB"
        )


async def get_or_create_genre(db: AsyncSession, user_id: UUID, genre_name: str) -> Genre:
    """Get an existing genre by name or create a new one"""
    genre_name = genre_name.strip()

    result = await db.execute(
        select(Genre).where(Genre.user_id == user_id, Genre.name == genre_name)
    )
    genre = result.scalars().first()

    if genre:
        return genre

    new_genre = Genre(user_id=user_id, name=genre_name)
    db.add(new_genre)
    await db.flush()
    return new_genre


async def parse_genres(db: AsyncSession, user_id: UUID, genres_str: str | None) -> list[Genre]:
    """Parse comma-separated genre names and return Genre objects"""
    if not genres_str or not genres_str.strip():
        return []

    genre_names = [name.strip() for name in genres_str.split(",") if name.strip()]
    genres: list[Genre] = []

    for genre_name in genre_names:
        genre = await get_or_create_genre(db, user_id, genre_name)
        genres.append(genre)

    return genres


def parse_csv_content(csv_content: str) -> list[dict[str, str]]:
    """Parse CSV content and return list of dictionaries"""
    # Strip leading/trailing whitespace and blank lines
    csv_content = csv_content.strip()

    csv_file = StringIO(csv_content)
    reader = csv.DictReader(csv_file)

    rows: list[dict[str, str]] = []
    for row in reader:
        row_dict = {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}
        rows.append(row_dict)

    return rows


def validate_csv_row(row: dict[str, str], create_schema: type[BaseModel], row_number: int) -> dict[str, object]:
    """Validate a CSV row against a Pydantic schema and return validated data"""
    clean_row: dict[str, object] = {}

    for key, value in row.items():
        if value == "":
            clean_row[key] = None
        else:
            clean_row[key] = value

    if "status" in clean_row and clean_row["status"]:
        status_value = clean_row["status"]
        if isinstance(status_value, str):
            status_value = status_value.lower()
            if status_value not in [s.value for s in MediaStatus]:
                raise BadRequestException(
                    f"Row {row_number}: Invalid status '{clean_row['status']}'. " +
                    f"Must be one of: {', '.join([s.value for s in MediaStatus])}"
                )
            clean_row["status"] = status_value

    if "is_audiobook" in clean_row and clean_row["is_audiobook"]:
        audiobook_value = clean_row["is_audiobook"]
        if isinstance(audiobook_value, str):
            audiobook_value = audiobook_value.lower()
            if audiobook_value in ["true", "1", "yes"]:
                clean_row["is_audiobook"] = True
            elif audiobook_value in ["false", "0", "no"]:
                clean_row["is_audiobook"] = False
            else:
                raise BadRequestException(
                    f"Row {row_number}: Invalid is_audiobook value '{clean_row['is_audiobook']}'. " +
                    "Must be true/false, yes/no, or 1/0"
                )

    if "episodes" in clean_row and clean_row["episodes"]:
        try:
            clean_row["episodes"] = int(str(clean_row["episodes"]))
        except ValueError:
            raise BadRequestException(f"Row {row_number}: episodes must be a number") from None

    clean_row["genre_ids"] = []

    try:
        validated = create_schema(**clean_row)
        return validated.model_dump(exclude={"genre_ids"})
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")
        raise BadRequestException(f"Row {row_number}: {', '.join(errors)}") from None


async def check_for_duplicate(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    model: type[MediaModel],
) -> bool:
    """Check if a media item with the same title already exists for the user"""
    result = await db.execute(
        select(model).where(model.user_id == user_id, model.title == title)
    )
    return result.scalars().first() is not None


async def import_csv_generic(
    db: AsyncSession,
    user_id: UUID,
    csv_content: str,
    model: type[MediaModel],
    create_schema: type[BaseModel],
) -> CSVImportResult:
    """Generic CSV import function for any media type"""
    rows = parse_csv_content(csv_content)

    if not rows:
        raise BadRequestException("CSV file is empty or has no valid rows")

    validated_items: list[tuple[dict[str, object], str | None]] = []

    for idx, row in enumerate(rows, start=2):
        validated_data = validate_csv_row(row, create_schema, idx)
        title = validated_data.get("title")
        if not isinstance(title, str):
            raise BadRequestException(f"Row {idx}: title is required")

        genres_str = row.get("genres")
        validated_items.append((validated_data, genres_str))

    result = CSVImportResult(
        total_rows=len(rows),
        imported=0,
        skipped_duplicates=0,
        imported_items=[],
        duplicate_titles=[],
    )

    for validated_data, genres_str in validated_items:
        title = validated_data.get("title")
        if not isinstance(title, str):
            continue

        is_duplicate = await check_for_duplicate(db, user_id, title, model)

        if is_duplicate:
            result.skipped_duplicates += 1
            result.duplicate_titles.append(title)
            continue

        validated_data["user_id"] = user_id
        if "status" in validated_data and hasattr(validated_data["status"], "value"):
            validated_data["status"] = validated_data["status"].value  # pyright: ignore[reportAttributeAccessIssue]

        media_item = model(**validated_data)

        if genres_str:
            genres = await parse_genres(db, user_id, genres_str)
            media_item.genres = genres

        db.add(media_item)
        await db.flush()

        result.imported += 1
        result.imported_items.append(media_item.id)

    await db.commit()

    return result
