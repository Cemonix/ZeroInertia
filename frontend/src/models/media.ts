export type MediaType = 'book' | 'movie' | 'game' | 'show';

export type MediaStatus = 'planned' | 'in_progress' | 'completed' | 'dropped';

export interface MediaBase {
    id: string;
    media_type: MediaType;
    title: string;
    status: MediaStatus;
    rating: number | null; // 0-100
    started_at: string | null; // ISO date string (YYYY-MM-DD)
    completed_at: string | null; // ISO date string (YYYY-MM-DD)
    notes: string | null;
    created_at: string;
    updated_at: string;
}

export interface BookDetails {
    author: string;
    pages: number | null;
    isbn: string | null;
    publisher: string | null;
}

export interface MovieDetails {
    director: string | null;
    duration_minutes: number | null;
    release_year: number | null;
    genre: string | null;
}

export interface GameDetails {
    platform: string | null; // e.g., 'PS5', 'PC', 'Switch'
    developer: string | null;
    playtime_hours: number | null;
    genre: string | null;
    is_100_percent: boolean | null;
}

export interface ShowDetails {
    season_number: number | null;
    episodes: number | null;
    creator: string | null;
    release_year: number | null;
    genre: string | null;
}

export type BookItem = MediaBase & { media_type: 'book' } & Required<Pick<BookDetails, 'author'>> & Omit<BookDetails, 'author'>;
export type MovieItem = MediaBase & { media_type: 'movie' } & MovieDetails;
export type GameItem = MediaBase & { media_type: 'game' } & Required<Pick<GameDetails, 'is_100_percent'>> & Omit<GameDetails, never>;
export type ShowItem = MediaBase & { media_type: 'show' } & ShowDetails;

export type MediaItem = BookItem | MovieItem | GameItem | ShowItem;

export interface MediaCreateInput {
    media_type: MediaType;
    title: string;
    status: MediaStatus;
    rating?: number | null;
    started_at?: string | null; // YYYY-MM-DD
    completed_at?: string | null; // YYYY-MM-DD
    notes?: string | null;
    // One of the following based on media_type
    book?: BookDetails;
    movie?: MovieDetails;
    game?: GameDetails;
    show?: ShowDetails;
}

export interface MediaUpdateInput {
    title?: string;
    status?: MediaStatus;
    rating?: number | null;
    started_at?: string | null;
    completed_at?: string | null;
    notes?: string | null;
    book?: Partial<BookDetails> | null;
    movie?: Partial<MovieDetails> | null;
    game?: Partial<GameDetails> | null;
    show?: Partial<ShowDetails> | null;
}

export interface MediaQueryParams {
    types?: MediaType[];
    status?: MediaStatus[];
    rating_min?: number;
    rating_max?: number;
    started_from?: string; // YYYY-MM-DD
    started_to?: string; // YYYY-MM-DD
    completed_from?: string; // YYYY-MM-DD
    completed_to?: string; // YYYY-MM-DD
    search?: string;
    sort?: 'created_at' | 'updated_at' | 'rating' | 'completed_at' | 'started_at' | 'title';
    order?: 'asc' | 'desc';
    skip?: number;
    limit?: number;
}

export const MEDIA_TYPES: { label: string; value: MediaType }[] = [
    { label: 'Book', value: 'book' },
    { label: 'Movie', value: 'movie' },
    { label: 'Game', value: 'game' },
    { label: 'Show', value: 'show' },
];

export const MEDIA_STATUSES: { label: string; value: MediaStatus }[] = [
    { label: 'Planned', value: 'planned' },
    { label: 'In Progress', value: 'in_progress' },
    { label: 'Completed', value: 'completed' },
    { label: 'Dropped', value: 'dropped' },
];
