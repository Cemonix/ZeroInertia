"""Media service module for managing media items (books, movies, games, shows, manga, anime).

This module provides a unified interface for CRUD operations on different media types.
All services follow the same pattern:
- create_X: Create a new media item
- get_X_by_id: Get a specific media item by ID
- get_all_Xs: Get all media items of a type for a user
- update_X: Update a media item
- delete_X: Delete a media item
"""

from app.services.media_service.anime_service import (
    create_anime,
    delete_anime,
    get_all_anime,
    get_anime_by_id,
    import_anime_csv,
    update_anime,
)
from app.services.media_service.base import get_by_status
from app.services.media_service.book_service import (
    create_book,
    delete_book,
    get_all_books,
    get_book_by_id,
    import_books_csv,
    update_book,
)
from app.services.media_service.csv_export_service import (
    export_anime_for_user,
    export_books_for_user,
    export_games_for_user,
    export_manga_for_user,
    export_movies_for_user,
    export_shows_for_user,
)
from app.services.media_service.game_service import (
    create_game,
    delete_game,
    get_all_games,
    get_game_by_id,
    import_games_csv,
    update_game,
)
from app.services.media_service.manga_service import (
    create_manga,
    delete_manga,
    get_all_manga,
    get_manga_by_id,
    import_manga_csv,
    update_manga,
)
from app.services.media_service.movie_service import (
    create_movie,
    delete_movie,
    get_all_movies,
    get_movie_by_id,
    import_movies_csv,
    update_movie,
)
from app.services.media_service.show_service import (
    create_show,
    delete_show,
    get_all_shows,
    get_show_by_id,
    import_shows_csv,
    update_show,
)
from app.services.media_service.utils import (
    check_duplicate,
    get_yearly_stats,
    search_media,
)

__all__ = [
    # Base functions
    "get_by_status",
    # Book functions
    "create_book",
    "delete_book",
    "get_all_books",
    "get_book_by_id",
    "update_book",
    # Movie functions
    "create_movie",
    "delete_movie",
    "get_all_movies",
    "get_movie_by_id",
    "update_movie",
    # Game functions
    "create_game",
    "delete_game",
    "get_all_games",
    "get_game_by_id",
    "update_game",
    # Show functions
    "create_show",
    "delete_show",
    "get_all_shows",
    "get_show_by_id",
    "update_show",
    # Manga functions
    "create_manga",
    "delete_manga",
    "get_all_manga",
    "get_manga_by_id",
    "update_manga",
    # Anime functions
    "create_anime",
    "delete_anime",
    "get_all_anime",
    "get_anime_by_id",
    "update_anime",
    # CSV Import functions
    "import_anime_csv",
    "import_books_csv",
    "import_games_csv",
    "import_manga_csv",
    "import_movies_csv",
    "import_shows_csv",
    # CSV Export functions
    "export_anime_for_user",
    "export_books_for_user",
    "export_games_for_user",
    "export_manga_for_user",
    "export_movies_for_user",
    "export_shows_for_user",
    # Utility functions
    "check_duplicate",
    "get_yearly_stats",
    "search_media",
]
