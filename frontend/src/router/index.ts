import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "@/views/HomeView.vue";
import NotesView from "@/views/NotesView.vue";
import MediaView from "@/views/MediaView.vue";

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
            },
        },
        {
            path: "/notes",
            name: "notes",
            component: NotesView,
            meta: {
                title: "Notes | Zero Inertia",
            },
        },
        {
            path: "/media",
            name: "media",
            component: MediaView,
            meta: {
                title: "Media | Zero Inertia",
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

    next();
});

export default router;
