import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import HomeView from "@/views/HomeView.vue";
import NotesView from "@/views/NotesView.vue";
import MediaView from "@/views/MediaView.vue";
import StreakView from "@/views/StreakView.vue";
import LoginView from "@/views/LoginView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "landing",
            component: () => import("@/views/public/LandingView.vue"),
            meta: {
                title: "Zero Inertia - Your Personal Productivity Ecosystem",
            },
        },
        {
            path: "/features",
            name: "features",
            component: () => import("@/views/public/FeaturesView.vue"),
            meta: {
                title: "Features | Zero Inertia",
            },
        },
        {
            path: "/about",
            name: "about",
            component: () => import("@/views/public/AboutView.vue"),
            meta: {
                title: "About | Zero Inertia",
            },
        },
        {
            path: "/pricing",
            name: "pricing",
            component: () => import("@/views/public/PricingView.vue"),
            meta: {
                title: "Pricing | Zero Inertia",
            },
        },
        {
            path: "/contact",
            name: "contact",
            component: () => import("@/views/public/ContactView.vue"),
            meta: {
                title: "Contact | Zero Inertia",
            },
        },
        {
            path: "/login",
            name: "login",
            component: LoginView,
            meta: {
                title: "Login | Zero Inertia",
                requiresGuest: true,
            },
        },
        {
            path: "/auth/error",
            name: "auth-error",
            component: () => import("@/views/AuthErrorView.vue"),
            meta: {
                title: "Authentication Error | Zero Inertia",
            },
        },
        {
            path: "/home",
            name: "home",
            component: HomeView,
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
        {
            path: "/:pathMatch(.*)*",
            name: "not-found",
            redirect: { name: "landing" },
        },
    ],
});

router.beforeEach(async (to, _, next) => {
    document.title = (to.meta.title as string) || "Zero Inertia";

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
    const requiresGuest = to.matched.some(
        (record) => record.meta.requiresGuest
    );

    // Public routes (no auth requirements) bypass all auth checks
    if (!requiresAuth && !requiresGuest) {
        next();
        return;
    }

    const authStore = useAuthStore();

    // Only initialize auth state if we need to check authentication
    if (!authStore.isInitialized) {
        await authStore.initialize();
    }

    if (requiresAuth && !authStore.isAuthenticated) {
        next({ name: "login" });
        return;
    }

    if (requiresGuest && authStore.isAuthenticated) {
        next({ name: "home" });
        return;
    }

    next();
});

export default router;
