<template>
    <main class="main-grid">
        <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
            <slot name="sidebar" />
        </aside>
        <div class="content">
            <nav class="navbar">
                <div class="navbar-left">
                    <Button
                        class="sidebar-toggle-btn"
                        @click="toggleSidebar"
                        text
                        rounded
                        aria-label="Toggle sidebar"
                    >
                        <font-awesome-icon :icon="isSidebarCollapsed ? 'chevron-right' : 'chevron-left'" />
                    </Button>
                    <slot name="navbar-left" />
                </div>
                <Button v-if="!authStore.isAuthenticated" @click="login" class="login-btn">Log in</Button>
                <div v-else class="user-section">
                    <div v-if="showStreak" class="streak-widget">
                        <span v-if="streakStore.currentStreak > 0" class="streak-flame">🔥</span>
                        <span class="streak-count">{{ streakStore.currentStreak }}</span>
                    </div>
                    <Button
                        class="theme-toggle-btn"
                        :class="{ 'dark-mode-btn': isDarkMode }"
                        size="medium"
                        shape="circle"
                        rounded
                        @click="toggleTheme"
                        aria-label="Toggle theme"
                    >
                        <FontAwesomeIcon :icon="isDarkMode ? 'sun' : 'moon'" />
                    </Button>
                    <Avatar
                        :label="userInitials"
                        size="medium"
                        shape="circle"
                        class="user-avatar"
                        @click="toggleUserMenu"
                    />
                    <Menu
                        ref="userMenu"
                        :model="userMenuItems"
                        :popup="true"
                    />
                </div>
            </nav>
            <section class="workspace">
                <slot />
            </section>
        </div>
        <NotificationToggle v-model:visible="showNotificationSettings" />
    </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useStreakStore } from "@/stores/streak";
import NotificationToggle from "@/components/common/NotificationToggle.vue";

const props = withDefaults(defineProps<{
    showStreak?: boolean;
}>(), {
    showStreak: true,
});

const authStore = useAuthStore();
const streakStore = useStreakStore();
const router = useRouter();

const userMenu = ref();
const isSidebarCollapsed = ref(false);
const isDarkMode = ref(false);
const showNotificationSettings = ref(false);

const getUserInitials = (fullName: string | null, email: string): string => {
    if (fullName && fullName.trim()) {
        const nameParts = fullName.trim().split(/\s+/);
        if (nameParts.length >= 2) {
            return (nameParts[0][0] + nameParts[nameParts.length - 1][0]).toUpperCase();
        }
        return nameParts[0][0].toUpperCase();
    }
    return email[0]?.toUpperCase() ?? "U";
};

const userInitials = computed(() => {
    if (!authStore.user) return "U";
    return getUserInitials(authStore.userName, authStore.userEmail || "");
});

const userMenuItems = computed(() => [
    {
        label: authStore.userName || authStore.userEmail || "User",
        disabled: true,
        class: "user-info",
    },
    { separator: true },
    {
        label: "Notifications",
        icon: "fa fa-bell",
        command: () => {
            showNotificationSettings.value = true;
        },
    },
    {
        label: "Logout",
        icon: "fa fa-sign-out-alt",
        command: async () => {
            await authStore.logout();
            router.push("/home");
        },
    },
]);

const toggleSidebar = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const toggleTheme = () => {
    const nextDarkMode = !isDarkMode.value;
    isDarkMode.value = nextDarkMode;
    
    if (typeof document !== "undefined") {
        const html = document.documentElement;
        
        if (nextDarkMode) {
            html.classList.add("dark-mode");
        } else {
            html.classList.remove("dark-mode");
        }
    }
    
    if (typeof localStorage !== "undefined") {
        localStorage.setItem("theme.mode", nextDarkMode ? "dark" : "light");
    }
};

const toggleUserMenu = (event: Event) => {
    userMenu.value?.toggle(event);
};

const login = () => {
    authStore.redirectToLogin();
};

const checkMobileView = () => {
    if (typeof window === "undefined") return;
    const mobileBreakpoint = 768;
    if (window.innerWidth < mobileBreakpoint) {
        isSidebarCollapsed.value = true;
    }
};

onMounted(() => {
    if (typeof window !== "undefined") {
        const storedTheme = localStorage.getItem("theme.mode");
        if (storedTheme === "dark") {
            isDarkMode.value = true;
            document.documentElement.classList.add("dark-mode");
        } else if (storedTheme === "light") {
            isDarkMode.value = false;
            document.documentElement.classList.remove("dark-mode");
        } else {
            isDarkMode.value = document.documentElement.classList.contains("dark-mode");
        }
    }
    if (authStore.isAuthenticated && props.showStreak) {
        streakStore.loadStreak();
    }
    checkMobileView();
    if (typeof window !== "undefined") {
        window.addEventListener("resize", checkMobileView);
    }
});

onUnmounted(() => {
    if (typeof window !== "undefined") {
        window.removeEventListener("resize", checkMobileView);
    }
});

watch(
    () => authStore.isAuthenticated,
    async (isAuthenticated) => {
        if (isAuthenticated && props.showStreak) {
            await streakStore.loadStreak();
        }
    },
);
</script>

<style scoped>
.main-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    height: 100vh;
}

.sidebar {
    display: flex;
    flex-direction: column;
    background: var(--p-content-background);
    border-right: 1px solid var(--p-content-border-color);
    min-width: 280px;
    max-width: 320px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.sidebar.collapsed {
    min-width: 0;
    max-width: 0;
    border-right: none;
}

.content {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--p-content-background);
    padding: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sidebar-toggle-btn {
    color: var(--p-text-color);
    transition: all 0.2s ease;
}

.sidebar-toggle-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}

.login-btn {
    background-color: var(--p-blue-500);
    color: var(--p-surface-0);
    border: none;
    border-radius: 5px;
    padding: 12px 20px;
    font-size: 1rem;
    cursor: pointer;
}

.login-btn:hover {
    background-color: var(--p-blue-600);
}

.user-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.theme-toggle-btn {
    width: 2.125rem;
    height: 2.125rem;
    background: transparent;
    border: 2px solid var(--p-gray-400);
    color: var(--p-gray-400);
    border-radius: 50%;
    transition: color 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
}

.theme-toggle-btn.dark-mode-btn {
    border-color: var(--p-orange-400);
    color: var(--p-orange-400);
}

.theme-toggle-btn:hover {
    background: transparent;
    color: var(--p-orange-400);
    border-color: var(--p-orange-400);
}

.theme-toggle-btn.dark-mode-btn:hover {
    background: transparent;
    color: var(--p-gray-400);
    border-color: var(--p-gray-400);
}

.streak-widget {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background: var(--p-orange-50);
    border: 1px solid var(--p-orange-200);
    border-radius: 20px;
    padding: 0.375rem 0.75rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.streak-widget:hover {
    background: var(--p-orange-100);
    border-color: var(--p-orange-300);
    transform: scale(1.05);
}

.streak-flame {
    font-size: 1.25rem;
    line-height: 1;
}

.streak-count {
    font-size: 0.9375rem;
    color: var(--p-orange-700);
}

.user-avatar {
    cursor: pointer;
    transition: transform 0.2s ease;
    background-color: var(--p-primary-500);
}

.user-avatar:hover {
    transform: scale(1.1);
}

.workspace {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    background: var(--p-content-hover-background);
}

:deep(.user-info) {
    font-weight: 600;
    color: var(--p-text-color);
    padding: 0.5rem 1rem;
}
</style>
