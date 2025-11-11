export interface PaginationParams {
    page?: number;
    page_size?: number;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
}

export function isPaginatedResponse<T = unknown>(
    value: unknown
): value is PaginatedResponse<T> {
    if (!value || typeof value !== "object") return false;
    const v = value as Record<string, unknown>;
    return (
        Array.isArray(v.items) &&
        typeof v.total === "number" &&
        typeof v.page === "number"
    );
}

export function wrapAsSinglePage<T>(
    items: T[],
    pageSize?: number
): PaginatedResponse<T> {
    const size = (pageSize ?? items.length) || 1;
    return {
        items,
        total: items.length,
        page: 1,
        page_size: size,
        total_pages: items.length > 0 ? Math.ceil(items.length / size) : 0,
        has_next: false,
        has_prev: false,
    };
}

export function buildPaginationQuery(
    params?: PaginationParams
): Record<string, number> | undefined {
    if (!params) return undefined;
    const query: Record<string, number> = {};
    if (typeof params.page === "number") query.page = params.page;
    if (typeof params.page_size === "number")
        query.page_size = params.page_size;
    return Object.keys(query).length ? query : undefined;
}
