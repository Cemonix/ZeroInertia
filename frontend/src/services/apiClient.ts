import axios from "axios";
import { env } from "@/config/env";
import { handleApiError } from "../core/errorHandler";

const apiClient = axios.create({
    baseURL: env.API_BASE_URL,
    timeout: 10000,
    headers: { "Content-Type": "application/json" },
    withCredentials: true,
});

apiClient.interceptors.request.use(async function (config) {
    // Attach CSRF token for unsafe methods
    const method = (config.method || 'get').toUpperCase();
    if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
        const token = await ensureCsrfToken();
        if (token) {
            config.headers = config.headers || {};
            (config.headers as any)['X-CSRF-Token'] = token;
        }
    }
    return config;
}, function (error) {
    return Promise.reject(error);
});

apiClient.interceptors.response.use(
    res => res,
    err => handleApiError(err, 'API request failed')
);


export default apiClient;

function getCookie(name: string): string | null {
    if (typeof document === 'undefined') return null;
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop()!.split(';').shift() || null;
    }
    return null;
}

let csrfTokenCache: string | null = null;

async function ensureCsrfToken(): Promise<string | null> {
    if (csrfTokenCache) return csrfTokenCache;

    // Try reading from same-origin cookie (when deployed as one domain)
    const cookieToken = getCookie('csrf_token');
    if (cookieToken) {
        csrfTokenCache = cookieToken;
        return csrfTokenCache;
    }

    // Otherwise, fetch from backend endpoint (CORS allowed origin) without axios interceptors
    try {
        const response = await fetch(`${env.API_BASE_URL}/csrf`, {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) return null;
        const data = await response.json().catch(() => null) as { csrf_token?: string } | null;
        const token = (data && data.csrf_token) || null;
        csrfTokenCache = token;
        return csrfTokenCache;
    } catch {
        return null;
    }
}

export function clearCsrfCache(): void {
    csrfTokenCache = null;
}

export async function prefetchCsrfToken(): Promise<void> {
    await ensureCsrfToken();
}
