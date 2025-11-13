import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "@/views/HomeView.vue";
import NotesView from "@/views/NotesView.vue";
import MediaView from "@/views/MediaView.vue";
import StreakView from "@/views/StreakView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/home",
            name: "home",
            component: HomeView,
            alias: "/",
            meta: {
                title: "Zero Inertia",
                requiresAuth: true,
            },
        },
        {
            path: "/notes",
            name: "notes",
            component: NotesView,
            meta: {
                title: "Notes | Zero Inertia",
                requiresAuth: true,
            },
        },
        {
            path: "/media",
            name: "media",
            component: MediaView,
            meta: {
                title: "Media | Zero Inertia",
                requiresAuth: true,
            },
        },
        {
            path: "/streaks",
            name: "streaks",
            component: StreakView,
            meta: {
                title: "Streaks | Zero Inertia",
                requiresAuth: true,
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
        window.location.href = "/api/v1/auth/google/login";
        return;
    }

    if (requiresGuest && authStore.isAuthenticated) {
        next({ name: "home" });
        return;
    }

    next();
});

export default router;
