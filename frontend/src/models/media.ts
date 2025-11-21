export type MediaType = "book" | "game" | "manga" | "movie" | "show";

export type MediaStatus = "planned" | "in_progress" | "completed" | "dropped";

export interface Genre {
    id: string;
    name: string;
    created_at: string;
}

export interface BaseMediaItem {
    id: string;
    title: string;
    status: MediaStatus;
    genres: Genre[];
    started_at: string | null;
    completed_at: string | null;
    notes: string | null;
    created_at: string;
    updated_at: string;
}

export interface BookMediaItem extends BaseMediaItem {
    media_type: "book";
    creator: string;
    is_audiobook: boolean;
}

export interface GameMediaItem extends BaseMediaItem {
    media_type: "game";
    platform: string | null;
}

export interface MovieMediaItem extends BaseMediaItem {
    media_type: "movie";
}

export interface ShowMediaItem extends BaseMediaItem {
    media_type: "show";
    season_number: number | null;
}

export interface MangaMediaItem extends BaseMediaItem {
    media_type: "manga";
    author: string | null;
}

export type MediaItem =
    | BookMediaItem
    | GameMediaItem
    | MangaMediaItem
    | MovieMediaItem
    | ShowMediaItem;

interface BaseMediaFormValues {
    title: string;
    status: MediaStatus;
    genre_ids: string[];
    started_at: string | null;
    completed_at: string | null;
    notes: string | null;
}

interface BookFormValues extends BaseMediaFormValues {
    media_type: "book";
    creator: string;
    is_audiobook: boolean;
}

interface GameFormValues extends BaseMediaFormValues {
    media_type: "game";
    platform: string | null;
}

interface MovieFormValues extends BaseMediaFormValues {
    media_type: "movie";
}

interface ShowFormValues extends BaseMediaFormValues {
    media_type: "show";
    season_number: number | null;
}

interface MangaFormValues extends BaseMediaFormValues {
    media_type: "manga";
    author: string | null;
}

export type MediaFormValues =
    | BookFormValues
    | GameFormValues
    | MangaFormValues
    | MovieFormValues
    | ShowFormValues;

export interface DuplicateMatch {
    media_type: MediaType;
    title: string;
    status?: MediaStatus;
    completed_at?: string | null;
}

export interface YearlyStats {
    year: number;
    books: number;
    games: number;
    manga: number;
    movies: number;
    shows: number;
}

export const MEDIA_TYPES: { label: string; value: MediaType }[] = [
    { label: "Books", value: "book" },
    { label: "Games", value: "game" },
    { label: "Manga", value: "manga" },
    { label: "Movies", value: "movie" },
    { label: "Shows", value: "show" },
];

export const MEDIA_STATUSES: { label: string; value: MediaStatus }[] = [
    { label: "Planned", value: "planned" },
    { label: "In Progress", value: "in_progress" },
    { label: "Completed", value: "completed" },
    { label: "Dropped", value: "dropped" },
];
