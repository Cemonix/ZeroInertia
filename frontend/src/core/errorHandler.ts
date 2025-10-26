import { AxiosError, isAxiosError } from 'axios';

export class ApiError extends Error {
    public readonly statusCode: number;
    public readonly errorCode: string;
    public readonly originalError?: unknown;

    constructor(
        message: string,
        statusCode: number = 500,
        errorCode: string = 'UNKNOWN_ERROR',
        originalError?: unknown
    ) {
        super(message);
        this.name = this.constructor.name;
        this.statusCode = statusCode;
        this.errorCode = errorCode;
        this.originalError = originalError;
    }
}

export class AuthError extends ApiError {
    constructor(
        message: string,
        statusCode: number = 401,
        errorCode: string = 'AUTH_ERROR',
        originalError?: unknown
    ) {
        super(message, statusCode, errorCode, originalError);
    }
}

export class NetworkError extends ApiError {
    constructor(
        message: string,
        statusCode: number = 503,
        errorCode: string = 'NETWORK_ERROR',
        originalError?: unknown
    ) {
        super(message, statusCode, errorCode, originalError);
    }
}

export function handleApiError(
    error: unknown,
    fallbackMessage: string = 'An unexpected error occurred',
    ErrorClass: typeof ApiError = ApiError
): never {
    if (isAxiosError(error)) {
        const axiosError = error as AxiosError;

        if (axiosError.code === 'ECONNABORTED' || axiosError.message === 'Network Error') {
            throw new NetworkError(fallbackMessage, 503, 'NETWORK_ERROR', axiosError);
        }
        if (axiosError.response) {
            const status = axiosError.response.status;
            const data = axiosError.response.data as { message?: string; code?: string };
            const message = data?.message || fallbackMessage;
            const errorCode = data?.code || 'API_ERROR';
            
            if (status === 401 || status === 403) {
                throw new AuthError(message, status, errorCode, axiosError);
            }

            throw new ErrorClass(message, status, errorCode, axiosError);
        }

        if (axiosError.request) {
            throw new NetworkError(fallbackMessage, 503, 'NO_RESPONSE', axiosError);
        }
    }

    throw new ErrorClass(fallbackMessage, 500, 'UNKNOWN_ERROR', error);
}

export function createAuthError(
    message: string,
    statusCode: number = 401,
    errorCode: string = 'AUTH_ERROR'
): AuthError {
    return new AuthError(message, statusCode, errorCode);
}