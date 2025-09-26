import { createRouter, createWebHistory } from "vue-router";
import LandingView from "@/views/LandingView.vue";
import WorkspaceView from "@/views/WorkspaceView.vue";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "landing",
            component: LandingView,
            meta: {
                layout: "public",
                title: "Zero Inertia - AI-Powered Productivity",
            },
        },
        {
            path: "/workspace",
            name: "workspace",
            component: WorkspaceView,
            meta: {
                requiresAuth: true,
                layout: "authenticated",
                title: "Workspace - Zero Inertia",
            },
        },
        {
            path: "/auth/error",
            name: "auth-error",
            component: LandingView,
            meta: {
                layout: "public",
                title: "Authentication Error - Zero Inertia",
            },
        },
    ],
});

router.beforeEach(async (to, _, next) => {
    document.title = (to.meta.title as string) || "Zero Inertia";
    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
    const requiresGuest = to.matched.some(
        (record) => record.meta.requiresGuest
    );

    const authStore = useAuthStore();

    // Only initialize auth state if we need to check authentication
    if ((requiresAuth || requiresGuest) && !authStore.isInitialized) {
        await authStore.initialize();
    }

    if (requiresAuth && !authStore.isAuthenticated) {
        next({ name: "landing" });
    } else if (requiresGuest && authStore.isAuthenticated) {
        next({ name: "workspace" });
    } else {
        next();
    }
});

export default router;
