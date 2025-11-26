import apiClient from "./apiClient";
import type {
    BookMediaItem,
    DuplicateMatch,
    GameMediaItem,
    Genre,
    MangaMediaItem,
    MediaFormValues,
    MediaItem,
    MediaStatus,
    MediaType,
    MovieMediaItem,
    ShowMediaItem,
    AnimeMediaItem,
    YearlyStats,
} from "@/models/media";

const API_URL = "/api/v1/media";

interface BookResponse extends Omit<BookMediaItem, "media_type"> {}
interface GameResponse extends Omit<GameMediaItem, "media_type"> {}
interface MangaResponse extends Omit<MangaMediaItem, "media_type"> {}
interface MovieResponse extends Omit<MovieMediaItem, "media_type"> {}
interface ShowResponse extends Omit<ShowMediaItem, "media_type"> {}
interface AnimeResponse extends Omit<AnimeMediaItem, "media_type"> {}

type DuplicateCheckRawResponse = Array<Record<string, string | null>>;

interface ListMediaParams {
    status?: MediaStatus;
}

interface CreateGenrePayload {
    name: string;
}

export const mediaService = {
    async listGenres(): Promise<Genre[]> {
        const res = await apiClient.get<Genre[]>(`${API_URL}/genres`);
        return res.data;
    },

    async createGenre(payload: CreateGenrePayload): Promise<Genre> {
        const res = await apiClient.post<Genre>(`${API_URL}/genres`, payload);
        return res.data;
    },

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

    async listAnime(params?: ListMediaParams): Promise<AnimeMediaItem[]> {
        const res = await apiClient.get<AnimeResponse[]>(`${API_URL}/anime`, {
            params,
        });
        return res.data.map((item) => ({
            ...item,
            media_type: "anime",
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

    async listManga(params?: ListMediaParams): Promise<MangaMediaItem[]> {
        const res = await apiClient.get<MangaResponse[]>(`${API_URL}/manga`, {
            params,
        });
        return res.data.map((item) => ({
            ...item,
            media_type: "manga",
        }));
    },

    async createMedia(values: MediaFormValues): Promise<MediaItem> {
        switch (values.media_type) {
            case "book": {
                const payload = {
                    title: values.title,
                    creator: values.creator,
                    status: values.status,
                    is_audiobook: values.is_audiobook,
                    genre_ids: values.genre_ids ?? [],
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
                    genre_ids: values.genre_ids ?? [],
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
                    genre_ids: values.genre_ids ?? [],
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
                    genre_ids: values.genre_ids ?? [],
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
            case "anime": {
                const payload = {
                    title: values.title,
                    status: values.status,
                    genre_ids: values.genre_ids ?? [],
                    episodes: values.episodes,
                    started_at: values.started_at,
                    completed_at: values.completed_at,
                    notes: values.notes,
                };
                const res = await apiClient.post<AnimeResponse>(
                    `${API_URL}/anime`,
                    payload,
                );
                return { ...res.data, media_type: "anime" };
            }
            case "manga": {
                const payload = {
                    title: values.title,
                    author: values.author,
                    status: values.status,
                    genre_ids: values.genre_ids ?? [],
                    started_at: values.started_at,
                    completed_at: values.completed_at,
                    notes: values.notes,
                };
                const res = await apiClient.post<MangaResponse>(
                    `${API_URL}/manga`,
                    payload,
                );
                return { ...res.data, media_type: "manga" };
            }
        }
    },

    async updateMedia(id: string, type: MediaType, values: Partial<MediaFormValues>): Promise<MediaItem> {
        switch (type) {
            case "book": {
                const payload: Partial<Omit<BookMediaItem, "id" | "media_type" | "created_at" | "updated_at">> & {
                    genre_ids?: string[];
                } = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre_ids !== undefined) payload.genre_ids = values.genre_ids;
                if ("is_audiobook" in values && values.is_audiobook !== undefined) {
                    payload.is_audiobook = values.is_audiobook;
                }
                if ("started_at" in values && values.started_at !== undefined) payload.started_at = values.started_at;
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
                const payload: Partial<Omit<GameMediaItem, "id" | "media_type" | "created_at" | "updated_at">> & {
                    genre_ids?: string[];
                } = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre_ids !== undefined) payload.genre_ids = values.genre_ids;
                if ("started_at" in values && values.started_at !== undefined) payload.started_at = values.started_at;
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
                const payload: Partial<Omit<MovieMediaItem, "id" | "media_type" | "created_at" | "updated_at">> & {
                    genre_ids?: string[];
                } = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre_ids !== undefined) payload.genre_ids = values.genre_ids;
                if (values.completed_at !== undefined) payload.completed_at = values.completed_at;
                if (values.notes !== undefined) payload.notes = values.notes;
                const res = await apiClient.patch<MovieResponse>(
                    `${API_URL}/movies/${id}`,
                    payload,
                );
                return { ...res.data, media_type: "movie" };
            }
            case "show": {
                const payload: Partial<Omit<ShowMediaItem, "id" | "media_type" | "created_at" | "updated_at">> & {
                    genre_ids?: string[];
                } = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre_ids !== undefined) payload.genre_ids = values.genre_ids;
                if ("started_at" in values && values.started_at !== undefined) payload.started_at = values.started_at;
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
            case "anime": {
                const payload: Partial<Omit<AnimeMediaItem, "id" | "media_type" | "created_at" | "updated_at">> & {
                    genre_ids?: string[];
                } = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre_ids !== undefined) payload.genre_ids = values.genre_ids;
                if ("started_at" in values && values.started_at !== undefined) payload.started_at = values.started_at;
                if (values.completed_at !== undefined) payload.completed_at = values.completed_at;
                if (values.notes !== undefined) payload.notes = values.notes;
                if ("episodes" in values && values.episodes !== undefined) {
                    payload.episodes = values.episodes;
                }
                const res = await apiClient.patch<AnimeResponse>(
                    `${API_URL}/anime/${id}`,
                    payload,
                );
                return { ...res.data, media_type: "anime" };
            }
            case "manga": {
                const payload: Partial<Omit<MangaMediaItem, "id" | "media_type" | "created_at" | "updated_at">> & {
                    genre_ids?: string[];
                } = {};
                if (values.title !== undefined) payload.title = values.title;
                if (values.status !== undefined) payload.status = values.status;
                if (values.genre_ids !== undefined) payload.genre_ids = values.genre_ids;
                if ("started_at" in values && values.started_at !== undefined) payload.started_at = values.started_at;
                if (values.completed_at !== undefined) payload.completed_at = values.completed_at;
                if (values.notes !== undefined) payload.notes = values.notes;
                if ("author" in values && values.author !== undefined) {
                    payload.author = values.author;
                }
                const res = await apiClient.patch<MangaResponse>(
                    `${API_URL}/manga/${id}`,
                    payload,
                );
                return { ...res.data, media_type: "manga" };
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
            case "anime":
                await apiClient.delete(`${API_URL}/anime/${id}`);
                return;
            case "manga":
                await apiClient.delete(`${API_URL}/manga/${id}`);
                return;
            case "movie":
                await apiClient.delete(`${API_URL}/movies/${id}`);
                return;
            case "show":
                await apiClient.delete(`${API_URL}/shows/${id}`);
                return;
        }
    },

    async checkDuplicateTitle(
        title: string,
        mediaType: MediaType,
    ): Promise<DuplicateMatch[]> {
        const res = await apiClient.get<DuplicateCheckRawResponse>(
            `${API_URL}/duplicate-check`,
            {
                params: { title, media_type: mediaType },
            },
        );

        return res.data.map((entry) => ({
            media_type: mediaType,
            title: (entry["title"] ?? "") as string,
            status: entry["status"] as MediaStatus | undefined,
            completed_at: entry["completed_at"] ?? undefined,
        }));
    },

    async getYearlyStats(year?: number): Promise<YearlyStats> {
        const res = await apiClient.get<YearlyStats>(`${API_URL}/stats/yearly`, {
            params: year ? { year } : undefined,
        });
        return { ...res.data, anime: res.data.anime ?? 0 };
    },
};
