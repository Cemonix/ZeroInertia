import apiClient from "./apiClient";
import type {
    User,
    LogoutResponse
} from "@/models/auth";
import { AuthError, handleApiError } from "../core/errorHandler";

const API_URL = "/api/v1/auth";

export class AuthService {
    /**
     * Gets the login URL for redirect-based OAuth
     */
    static getGoogleLoginUrl(): string {
        return `${API_URL}/google/login`;
    }

    /**
     * Gets the currently authenticated user from the backend
     */
    static async getCurrentUser(): Promise<User> {
        try {
            const response = await apiClient.get<User>(`${API_URL}/me`);

            return response.data;
        } 
        catch (error) {
            throw handleApiError(error, 'Failed to get current user', AuthError);
        }
    }

    /**
     * Logs out the current user by clearing the authentication cookie
     */
    static async logout(): Promise<void> {
        try {
            await apiClient.post<LogoutResponse>(`${API_URL}/logout`);
        } catch (error) {
            throw handleApiError(error, 'Failed to logout', AuthError);
        }
    }

    /**
     * Checks if user is currently authenticated by verifying the token
     */
    static async isAuthenticated(): Promise<boolean> {
        try {
            const response = await apiClient.get(`${API_URL}/is_authenticated`);
            return response.data.is_authenticated;
        } catch {
            return false;
        }
    }
}
