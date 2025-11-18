import apiClient from "./apiClient";
import type {
    BookMediaItem,
    DuplicateMatch,
    GameMediaItem,
    MediaFormValues,
    MediaItem,
    MediaStatus,
    MediaType,
    MovieMediaItem,
    ShowMediaItem,
    YearlyStats,
} from "@/models/media";

const API_URL = "/api/v1/media";

interface BookResponse extends Omit<BookMediaItem, "media_type"> {}
interface GameResponse extends Omit<GameMediaItem, "media_type"> {}
interface MovieResponse extends Omit<MovieMediaItem, "media_type"> {}
interface ShowResponse extends Omit<ShowMediaItem, "media_type"> {}

type DuplicateCheckRawResponse = {
    books: Array<Record<string, string | null>>;
    games: Array<Record<string, string | null>>;
    movies: Array<Record<string, string | null>>;
    shows: Array<Record<string, string | null>>;
};

interface ListMediaParams {
    status?: MediaStatus;
}

export const mediaService = {
    async listBooks(params?: ListMediaParams): Promise<BookMediaItem[]> {
        const res = await apiClient.get<BookResponse[]>(`${API_URL}/books`, {
            params,
        });
        return res.data.map((item) => ({
            ...item,
            media_type: "book",
        }));
    },

    async listGames(params?: ListMediaParams): Promise<GameMediaItem[]> {
        const res = await apiClient.get<GameResponse[]>(`${API_URL}/games`, {
            params,
        });
        return res.data.map((item) => ({
            ...item,
            media_type: "game",
        }));
    },

    async listMovies(params?: ListMediaParams): Promise<MovieMediaItem[]> {
        const res = await apiClient.get<MovieResponse[]>(`${API_URL}/movies`, {
            params,
        });
        return res.data.map((item) => ({
            ...item,
            media_type: "movie",
        }));
    },

    async listShows(params?: ListMediaParams): Promise<ShowMediaItem[]> {
        const res = await apiClient.get<ShowResponse[]>(`${API_URL}/shows`, {
            params,
        });
        return res.data.map((item) => ({
            ...item,
            media_type: "show",
        }));
    },

    async createMedia(values: MediaFormValues): Promise<MediaItem> {
        switch (values.media_type) {
            case "book": {
                const payload = {
                    title: values.title,
                    creator: values.creator,
                    status: values.status,
                    genre: values.genre,
                    started_at: values.started_at,
                    completed_at: values.completed_at,
                    notes: values.notes,
                };
                const res = await apiClient.post<BookResponse>(
                    `${API_URL}/books`,
                    payload,
                );
                return { ...res.data, media_type: "book" };
            }
            case "game": {
                const payload = {
                    title: values.title,
                    status: values.status,
                    genre: values.genre,
                    platform: values.platform,
                    started_at: values.started_at,
                    completed_at: values.completed_at,
                    notes: values.notes,
                };
                const res = await apiClient.post<GameResponse>(
                    `${API_URL}/games`,
                    payload,
                );
                return { ...res.data, media_type: "game" };
            }
            case "movie": {
                const payload = {
                    title: values.title,
                    status: values.status,
                    genre: values.genre,
                    started_at: values.started_at,
                    completed_at: values.completed_at,
                    notes: values.notes,
                };
                const res = await apiClient.post<MovieResponse>(
                    `${API_URL}/movies`,
                    payload,
                );
                return { ...res.data, media_type: "movie" };
            }
            case "show": {
                const payload = {
                    title: values.title,
                    season_number: values.season_number,
                    status: values.status,
                    genre: values.genre,
                    started_at: values.started_at,
                    completed_at: values.completed_at,
                    notes: values.notes,
                };
                const res = await apiClient.post<ShowResponse>(
                    `${API_URL}/shows`,
                    payload,
                );
                return { ...res.data, media_type: "show" };
            }
        }
    },

    async updateMedia(id: string, type: MediaType, values: Partial<MediaFormValues>): Promise<MediaItem> {
        switch (type) {
            case "book": {
                const payload: Partial<Omit<BookMediaItem, "id" | "media_type" | "created_at" | "updated_at">> = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre !== undefined) payload.genre = values.genre;
                if (values.started_at !== undefined) payload.started_at = values.started_at;
                if (values.completed_at !== undefined) payload.completed_at = values.completed_at;
                if (values.notes !== undefined) payload.notes = values.notes;
                if ("creator" in values && values.creator !== undefined) {
                    payload.creator = values.creator;
                }
                const res = await apiClient.patch<BookResponse>(
                    `${API_URL}/books/${id}`,
                    payload,
                );
                return { ...res.data, media_type: "book" };
            }
            case "game": {
                const payload: Partial<Omit<GameMediaItem, "id" | "media_type" | "created_at" | "updated_at">> = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre !== undefined) payload.genre = values.genre;
                if (values.started_at !== undefined) payload.started_at = values.started_at;
                if (values.completed_at !== undefined) payload.completed_at = values.completed_at;
                if (values.notes !== undefined) payload.notes = values.notes;
                if ("platform" in values && values.platform !== undefined) {
                    payload.platform = values.platform;
                }
                const res = await apiClient.patch<GameResponse>(
                    `${API_URL}/games/${id}`,
                    payload,
                );
                return { ...res.data, media_type: "game" };
            }
            case "movie": {
                const payload: Partial<Omit<MovieMediaItem, "id" | "media_type" | "created_at" | "updated_at">> = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre !== undefined) payload.genre = values.genre;
                if (values.started_at !== undefined) payload.started_at = values.started_at;
                if (values.completed_at !== undefined) payload.completed_at = values.completed_at;
                if (values.notes !== undefined) payload.notes = values.notes;
                const res = await apiClient.patch<MovieResponse>(
                    `${API_URL}/movies/${id}`,
                    payload,
                );
                return { ...res.data, media_type: "movie" };
            }
            case "show": {
                const payload: Partial<Omit<ShowMediaItem, "id" | "media_type" | "created_at" | "updated_at">> = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre !== undefined) payload.genre = values.genre;
                if (values.started_at !== undefined) payload.started_at = values.started_at;
                if (values.completed_at !== undefined) payload.completed_at = values.completed_at;
                if (values.notes !== undefined) payload.notes = values.notes;
                if ("season_number" in values && values.season_number !== undefined) {
                    payload.season_number = values.season_number;
                }
                const res = await apiClient.patch<ShowResponse>(
                    `${API_URL}/shows/${id}`,
                    payload,
                );
                return { ...res.data, media_type: "show" };
            }
        }
    },

    async deleteMedia(id: string, type: MediaType): Promise<void> {
        switch (type) {
            case "book":
                await apiClient.delete(`${API_URL}/books/${id}`);
                return;
            case "game":
                await apiClient.delete(`${API_URL}/games/${id}`);
                return;
            case "movie":
                await apiClient.delete(`${API_URL}/movies/${id}`);
                return;
            case "show":
                await apiClient.delete(`${API_URL}/shows/${id}`);
                return;
        }
    },

    async checkDuplicateTitle(title: string): Promise<DuplicateMatch[]> {
        const res = await apiClient.get<DuplicateCheckRawResponse>(
            `${API_URL}/duplicate-check`,
            {
                params: { title },
            },
        );

        const matches: DuplicateMatch[] = [];

        const pushMatches = (
            type: MediaType,
            entries: Array<Record<string, string | null>>,
        ) => {
            for (const entry of entries) {
                const rawTitle = (entry["title"] ?? "") as string;
                matches.push({
                    media_type: type,
                    title: rawTitle,
                    status: entry["status"] as MediaStatus | undefined,
                    completed_at: entry["completed_at"] ?? undefined,
                });
            }
        };

        pushMatches("book", res.data.books);
        pushMatches("game", res.data.games);
        pushMatches("movie", res.data.movies);
        pushMatches("show", res.data.shows);

        return matches;
    },

    async getYearlyStats(year?: number): Promise<YearlyStats> {
        const res = await apiClient.get<YearlyStats>(`${API_URL}/stats/yearly`, {
            params: year ? { year } : undefined,
        });
        return res.data;
    },
};
