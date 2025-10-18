export interface User {
    id: string;
    email: string;
    full_name: string | null;
    avatar_url: string | null;
}

export interface AuthResponse {
    message: string;
    user: User;
}

export interface GoogleAuthInitResponse {
    auth_url: string;
}

export interface MeResponse {
    user: User;
}

export interface LogoutResponse {
    message: string;
}
