export interface Environment {
    readonly API_BASE_URL: string;
    readonly NODE_ENV: string;
    readonly IS_DEVELOPMENT: boolean;
    readonly IS_PRODUCTION: boolean;
    readonly APP_NAME: string;
    readonly APP_VERSION: string;
}

function createEnv(): Environment {
    const nodeEnv = import.meta.env.NODE_ENV || "development";

    const environment = {
        API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
        NODE_ENV: nodeEnv,
        IS_DEVELOPMENT: nodeEnv === "development",
        IS_PRODUCTION: nodeEnv === "production",
        APP_NAME: import.meta.env.VITE_APP_NAME || "ZeroInertia",
        APP_VERSION: import.meta.env.VITE_APP_VERSION || "0.0.1",
    } as const;

    return environment;
}

export const env = createEnv();