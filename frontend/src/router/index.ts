import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import DashboardView from "@/views/DashboardView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/home",
            name: "dashboard",
            component: DashboardView,
            alias: "/",
            meta: {
                title: "Zero Inertia",
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
