import apiClient from './apiClient';
import type { MediaCreateInput, MediaItem, MediaQueryParams, MediaUpdateInput, MediaType } from '@/models/media';
import type { PaginatedResponse, PaginationParams } from '@/models/pagination';
import { isPaginatedResponse, wrapAsSinglePage } from '@/models/pagination';

const API_URL = '/api/v1/media';

const buildQueryParams = (params: MediaQueryParams & PaginationParams = {}) => {
    const query: Record<string, unknown> = {};
    if (params.types && params.types.length === 1) query.type = params.types[0];
    if (params.status && params.status.length === 1) query.status = params.status[0];
    // Rating filters - send to backend
    if (typeof params.rating_min === 'number' && params.rating_min > 0) {
        query.rating_min = params.rating_min;
    }
    if (typeof params.rating_max === 'number' && params.rating_max < 100) {
        query.rating_max = params.rating_max;
    }
    // Search filter - send to backend
    if (params.search && params.search.trim()) {
        query.search = params.search.trim();
    }
    // TODO: Date filters (not yet implemented in backend)
    if (params.started_from) query.started_from = params.started_from;
    if (params.started_to) query.started_to = params.started_to;
    if (params.completed_from) query.completed_from = params.completed_from;
    if (params.completed_to) query.completed_to = params.completed_to;
    // TODO: Sorting and pagination (not yet implemented in backend)
    if (params.sort) query.sort = params.sort;
    if (params.order) query.order = params.order;
    // Prefer page-based pagination per backend schema
    if (typeof params.page === 'number') query.page = params.page;
    if (typeof params.page_size === 'number') query.page_size = params.page_size;
    // Back-compat for any older endpoints (unused once fully paginated)
    if (typeof (params as any).skip === 'number') query.skip = (params as any).skip;
    if (typeof (params as any).limit === 'number') query.limit = (params as any).limit;
    return query;
};

// Flatten payloads per backend type-specific schemas
const toBookCreate = (p: MediaCreateInput) => ({
    title: p.title,
    author: p.book?.author ?? '',
    pages: p.book?.pages ?? null,
    isbn: p.book?.isbn ?? null,
    publisher: p.book?.publisher ?? null,
    status: p.status,
    rating: p.rating ?? null,
    started_at: p.started_at ?? null,
    completed_at: p.completed_at ?? null,
    notes: p.notes ?? null,
});
const toMovieCreate = (p: MediaCreateInput) => ({
    title: p.title,
    director: p.movie?.director ?? null,
    duration_minutes: p.movie?.duration_minutes ?? null,
    release_year: p.movie?.release_year ?? null,
    genre: p.movie?.genre ?? null,
    status: p.status,
    rating: p.rating ?? null,
    started_at: p.started_at ?? null,
    completed_at: p.completed_at ?? null,
    notes: p.notes ?? null,
});
const toGameCreate = (p: MediaCreateInput) => ({
    title: p.title,
    platform: p.game?.platform ?? null,
    developer: p.game?.developer ?? null,
    playtime_hours: p.game?.playtime_hours ?? null,
    genre: p.game?.genre ?? null,
    is_100_percent: p.game?.is_100_percent ?? false,
    status: p.status,
    rating: p.rating ?? null,
    started_at: p.started_at ?? null,
    completed_at: p.completed_at ?? null,
    notes: p.notes ?? null,
});
const toShowCreate = (p: MediaCreateInput) => ({
    title: p.title,
    season_number: p.show?.season_number ?? null,
    episodes: p.show?.episodes ?? null,
    creator: p.show?.creator ?? null,
    release_year: p.show?.release_year ?? null,
    genre: p.show?.genre ?? null,
    status: p.status,
    rating: p.rating ?? null,
    started_at: p.started_at ?? null,
    completed_at: p.completed_at ?? null,
    notes: p.notes ?? null,
});

const toBookUpdate = (p: MediaUpdateInput) => ({
    title: p.title,
    author: p.book?.author,
    pages: p.book?.pages,
    isbn: p.book?.isbn,
    publisher: p.book?.publisher,
    status: p.status,
    rating: p.rating,
    started_at: p.started_at,
    completed_at: p.completed_at,
    notes: p.notes,
});
const toMovieUpdate = (p: MediaUpdateInput) => ({
    title: p.title,
    director: p.movie?.director,
    duration_minutes: p.movie?.duration_minutes,
    release_year: p.movie?.release_year,
    genre: p.movie?.genre,
    status: p.status,
    rating: p.rating,
    started_at: p.started_at,
    completed_at: p.completed_at,
    notes: p.notes,
});
const toGameUpdate = (p: MediaUpdateInput) => ({
    title: p.title,
    platform: p.game?.platform,
    developer: p.game?.developer,
    playtime_hours: p.game?.playtime_hours,
    genre: p.game?.genre,
    is_100_percent: p.game?.is_100_percent,
    status: p.status,
    rating: p.rating,
    started_at: p.started_at,
    completed_at: p.completed_at,
    notes: p.notes,
});
const toShowUpdate = (p: MediaUpdateInput) => ({
    title: p.title,
    season_number: p.show?.season_number,
    episodes: p.show?.episodes,
    creator: p.show?.creator,
    release_year: p.show?.release_year,
    genre: p.show?.genre,
    status: p.status,
    rating: p.rating,
    started_at: p.started_at,
    completed_at: p.completed_at,
    notes: p.notes,
});

export const mediaService = {
    async list(params: MediaQueryParams & PaginationParams = {}): Promise<PaginatedResponse<MediaItem>> {
        const response = await apiClient.get(`${API_URL}/`, { params: buildQueryParams(params) });
        const data = response.data as unknown;
        if (isPaginatedResponse<MediaItem>(data)) return data;
        return wrapAsSinglePage((data as MediaItem[]) ?? []);
    },

    async getById(id: string, type: MediaType): Promise<MediaItem> {
        const path =
            type === 'book' ? 'books' :
            type === 'movie' ? 'movies' :
            type === 'game' ? 'games' : 'shows';
        const response = await apiClient.get(`${API_URL}/${path}/${id}`);
        return response.data;
    },

    async create(payload: MediaCreateInput): Promise<MediaItem> {
        const path =
            payload.media_type === 'book' ? 'books' :
            payload.media_type === 'movie' ? 'movies' :
            payload.media_type === 'game' ? 'games' : 'shows';
        const body =
            payload.media_type === 'book' ? toBookCreate(payload) :
            payload.media_type === 'movie' ? toMovieCreate(payload) :
            payload.media_type === 'game' ? toGameCreate(payload) : toShowCreate(payload);
        const response = await apiClient.post(`${API_URL}/${path}`, body);
        return response.data;
    },

    async update(id: string, type: MediaType, payload: MediaUpdateInput): Promise<MediaItem> {
        const path =
            type === 'book' ? 'books' :
            type === 'movie' ? 'movies' :
            type === 'game' ? 'games' : 'shows';
        const body =
            type === 'book' ? toBookUpdate(payload) :
            type === 'movie' ? toMovieUpdate(payload) :
            type === 'game' ? toGameUpdate(payload) : toShowUpdate(payload);
        const response = await apiClient.patch(`${API_URL}/${path}/${id}`, body);
        return response.data;
    },

    async remove(id: string, type: MediaType): Promise<void> {
        const path =
            type === 'book' ? 'books' :
            type === 'movie' ? 'movies' :
            type === 'game' ? 'games' : 'shows';
        await apiClient.delete(`${API_URL}/${path}/${id}`);
    },
};
