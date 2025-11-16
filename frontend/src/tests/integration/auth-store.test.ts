import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '@/stores/auth';

describe('Auth Store Integration', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
    });

    it('should initialize as unauthenticated', () => {
        const authStore = useAuthStore();

        expect(authStore.isAuthenticated).toBe(false);
        expect(authStore.user).toBeNull();
        expect(authStore.userEmail).toBeNull();
    });

    it('should handle successful login', async () => {
        const authStore = useAuthStore();

        await authStore.initialize();

        expect(authStore.isInitialized).toBe(true);
        expect(authStore.isLoading).toBe(false);
    });

    it('should handle logout', async () => {
        const authStore = useAuthStore();

        authStore.setUser({
            id: 'user-1',
            email: 'test@example.com',
            full_name: 'Test User',
            avatar_url: null,
        });

        expect(authStore.isAuthenticated).toBe(true);

        await authStore.logout();

        expect(authStore.isAuthenticated).toBe(false);
        expect(authStore.user).toBeNull();
    });

    it('should compute isAuthenticated correctly', () => {
        const authStore = useAuthStore();

        expect(authStore.isAuthenticated).toBe(false);

        authStore.setUser({
            id: 'user-1',
            email: 'test@example.com',
            full_name: 'Test User',
            avatar_url: null,
        });

        expect(authStore.isAuthenticated).toBe(true);

        authStore.clearUser();

        expect(authStore.isAuthenticated).toBe(false);
    });

    it('should expose user email correctly', () => {
        const authStore = useAuthStore();

        expect(authStore.userEmail).toBeNull();

        authStore.setUser({
            id: 'user-1',
            email: 'test@example.com',
            full_name: 'Test User',
            avatar_url: null,
        });

        expect(authStore.userEmail).toBe('test@example.com');
    });

    it('should expose user name correctly', () => {
        const authStore = useAuthStore();

        expect(authStore.userName).toBeNull();

        authStore.setUser({
            id: 'user-1',
            email: 'test@example.com',
            full_name: 'Test User',
            avatar_url: null,
        });

        expect(authStore.userName).toBe('Test User');
    });

    it('should handle initialization errors gracefully', async () => {
        const authStore = useAuthStore();

        await authStore.initialize();

        expect(authStore.isInitialized).toBe(true);
        expect(authStore.user).toBeNull();
    });

    it('should not reinitialize if already initialized', async () => {
        const authStore = useAuthStore();

        await authStore.initialize();
        const firstInitState = authStore.isInitialized;

        await authStore.initialize();

        expect(authStore.isInitialized).toBe(firstInitState);
    });
});
