import { defineStore } from "pinia";
import { ref, computed, readonly } from "vue";
import type { User } from "@/models/auth";
import { AuthService } from "@/services/authService";
import { clearCsrfCache, prefetchCsrfToken } from "@/services/apiClient";

export const useAuthStore = defineStore("auth", () => {
    const user = ref<User | null>(null);
    const isLoading = ref(false);
    const isInitialized = ref(false);
    const error = ref<string | null>(null);

    const isAuthenticated = computed(() => user.value !== null);
    const userEmail = computed(() => user.value?.email ?? null);
    const userName = computed(() => user.value?.full_name ?? null);

    /**
     * Initialize auth state by checking current user
     */
    async function initialize() {
        if (isInitialized.value) return;

        isLoading.value = true;

        try {
            if (await AuthService.isAuthenticated()) {
                const userData = await AuthService.getCurrentUser();
                // Rotate happened server-side during login; refresh CSRF cache client-side
                clearCsrfCache();
                await prefetchCsrfToken();
                setUser(userData);
            } else {
                clearUser();
            }
        } catch (error) {
            clearUser();
        } finally {
            isInitialized.value = true;
            isLoading.value = false;
        }
    }

    /**
     * Redirect to Google OAuth login
     */
    function redirectToLogin() {
        window.location.href = AuthService.getGoogleLoginUrl();
    }

    /**
     * Logout user and clear state
     */
    async function logout() {
        isLoading.value = true;

        try {
            await AuthService.logout();
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to logout';
        } finally {
            // Clear CSRF cache as cookie is deleted server-side
            clearCsrfCache();
            clearUser();
            isLoading.value = false;
        }
    }

    /**
     * Update user data in store
     */
    function setUser(userData: User) {
        user.value = userData;
    }

    /**
     * Clear user data from store
     */
    function clearUser() {
        user.value = null;
    }

    return {
        // State
        user: readonly(user),
        isLoading: readonly(isLoading),
        isInitialized: readonly(isInitialized),

        // Getters
        isAuthenticated,
        userEmail,
        userName,

        // Actions
        initialize,
        redirectToLogin,
        logout,
        setUser,
        clearUser,
    };
});
