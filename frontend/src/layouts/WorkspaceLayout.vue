<template>
    <main class="main-grid">
        <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
            <!-- Mobile close button inside full-screen sidebar -->
            <Button
                v-if="isMobileView && !isSidebarCollapsed"
                class="sidebar-close-btn"
                text
                rounded
                aria-label="Close sidebar"
                @click="toggleSidebar"
            >
                <FontAwesomeIcon icon="times" />
            </Button>
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
                    <div
                        v-if="showStreak"
                        class="streak-widget"
                        role="button"
                        tabindex="0"
                        aria-label="Open streak calendar"
                        @click="goToStreaks"
                        @keyup.enter="goToStreaks"
                        @keyup.space.prevent="goToStreaks"
                    >
                        <span v-if="streakStore.currentStreak > 0" class="streak-flame">🔥</span>
                        <span class="streak-count">{{ streakStore.currentStreak }}</span>
                    </div>
                    <Button
                        class="theme-toggle-btn"
                        size="medium"
                        shape="circle"
                        rounded
                        @click="showShortcuts = true"
                        aria-label="Keyboard shortcuts"
                        :title="'Keyboard shortcuts'"
                    >
                        <FontAwesomeIcon icon="keyboard" />
                    </Button>
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
                    >
                        <template #item="{ item, props }">
                            <a class="p-menuitem-link" v-bind="props.action">
                                <span v-if="item.icon" class="p-menuitem-icon">
                                    <FontAwesomeIcon :icon="item.icon" />
                                </span>
                                <span class="p-menuitem-text">{{ item.label }}</span>
                            </a>
                        </template>
                    </Menu>
                </div>
            </nav>
            <section class="workspace">
                <slot />
            </section>
        </div>
        <NotificationToggle v-model:visible="showNotificationSettings" />
        <ShortcutsHelp v-model:visible="showShortcuts" />
    </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useUiStore } from "@/stores/ui";
import { useAuthStore } from "@/stores/auth";
import { useStreakStore } from "@/stores/streak";
import { useTheme } from "@/composables/useTheme";
import { useKeyboardShortcuts } from "@/composables/useKeyboardShortcuts";
import NotificationToggle from "@/components/common/NotificationToggle.vue";
import ShortcutsHelp from "@/components/common/ShortcutsHelp.vue";

const props = withDefaults(defineProps<{
    showStreak?: boolean;
}>(), {
    showStreak: true,
});

const authStore = useAuthStore();
const streakStore = useStreakStore();
const route = useRoute();
const router = useRouter();

const userMenu = ref();
const uiStore = useUiStore();
const { isSidebarCollapsed } = storeToRefs(uiStore);
const { isDarkMode, toggleTheme, initializeTheme } = useTheme();
const { register } = useKeyboardShortcuts();
const showNotificationSettings = ref(false);
const showShortcuts = ref(false);
const isMobileView = ref(false);
const TASK_COMPLETION_SOUND_KEY = "sound.taskCompletion.enabled";
const isTaskCompletionSoundEnabled = ref(true);

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
        icon: "bell",
        command: () => {
            showNotificationSettings.value = true;
        },
    },
    {
        label: isTaskCompletionSoundEnabled.value
            ? "Mute sound"
            : "Unmute sound",
        icon: isTaskCompletionSoundEnabled.value ? "volume-high" : "volume-xmark",
        command: () => {
            const next = !isTaskCompletionSoundEnabled.value;
            isTaskCompletionSoundEnabled.value = next;
            if (typeof localStorage !== "undefined") {
                localStorage.setItem(TASK_COMPLETION_SOUND_KEY, String(next));
            }
        },
    },
    {
        label: "Logout",
        icon: "sign-out-alt",
        command: async () => {
            await authStore.logout();
            // Force full page redirect to login after logout
            window.location.href = "/api/v1/auth/google/login";
        },
    },
]);

const toggleSidebar = () => {
    uiStore.toggleSidebar();
};

const goToStreaks = () => {
    if (router.currentRoute.value.path !== "/streaks") {
        router.push("/streaks");
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
    const wasMobile = isMobileView.value;
    isMobileView.value = window.innerWidth < mobileBreakpoint;

    // Collapse sidebar when entering mobile view
    if (isMobileView.value && !wasMobile) {
        uiStore.setSidebarCollapsed(true);
    }
    // Expand sidebar when entering desktop view
    else if (!isMobileView.value && wasMobile) {
        uiStore.setSidebarCollapsed(false);
    }
};

onMounted(() => {
    initializeTheme();

    if (typeof window !== "undefined") {
        const storedSound = localStorage.getItem(TASK_COMPLETION_SOUND_KEY);
        if (storedSound !== null) {
            isTaskCompletionSoundEnabled.value = storedSound !== "false";
        }
    }
    if (authStore.isAuthenticated && props.showStreak && !streakStore.hasLoadedStreak) {
        streakStore.loadStreak();
    }
    checkMobileView();
    if (typeof window !== "undefined") {
        window.addEventListener("resize", checkMobileView);
    }

    // Prevent background scroll when mobile sidebar is open
    if (typeof document !== "undefined") {
        const updateBodyOverflow = () => {
            document.body.style.overflow = (isMobileView.value && !isSidebarCollapsed.value) ? "hidden" : "";
        };
        // Initial set
        updateBodyOverflow();
        // Watch for changes
        watch([isMobileView, isSidebarCollapsed], updateBodyOverflow);
    }

    // Register keyboard shortcut to open shortcuts help
    register({
        key: '/',
        ctrl: true,
        handler: () => {
            showShortcuts.value = true;
        },
        description: 'Open shortcuts help',
    });
});

onUnmounted(() => {
    if (typeof window !== "undefined") {
        window.removeEventListener("resize", checkMobileView);
    }
    if (typeof document !== "undefined") {
        document.body.style.overflow = "";
    }
});

watch(
    () => authStore.isAuthenticated,
    async (isAuthenticated) => {
        if (isAuthenticated && props.showStreak && !streakStore.hasLoadedStreak) {
            await streakStore.loadStreak();
        }
    },
);

// Close the mobile sidebar on navigation (e.g., selecting a project)
watch(
    () => route.fullPath,
    () => {
        if (isMobileView.value && !isSidebarCollapsed.value) {
            uiStore.setSidebarCollapsed(true);
        }
    }
);
</script>

<style scoped>
.main-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    height: 100vh;
    position: relative;
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

/* Mobile sidebar - full screen overlay */
@media (max-width: 768px) {
    .main-grid {
        grid-template-columns: 1fr;
        width: 100%;
    }

    .sidebar-close-btn {
        position: absolute;
        right: calc(0.75rem + env(safe-area-inset-right, 0px));
        bottom: calc(0.75rem + env(safe-area-inset-bottom, 0px));
        width: 2.75rem;
        height: 2.75rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        z-index: 1110; /* above slot content */
        color: var(--p-content-background);
        background: var(--p-primary-color);
        border-radius: 999px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
    }
    .sidebar-close-btn.p-button {
        background: var(--p-primary-color);
        border: none;
        padding: 0;
    }
    .sidebar-close-btn :deep(.p-button-icon) {
        font-size: 1.15rem;
    }
    .sidebar-close-btn:hover {
        filter: brightness(0.95);
    }

    .sidebar {
        position: fixed;
        inset: 0; /* full-bleed overlay */
        width: auto;
        min-width: 0;
        max-width: none;
        z-index: 1100;
        border-right: none;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
        /* smoother slide performance */
        will-change: transform, opacity;
        transition: transform 260ms cubic-bezier(0.4, 0, 0.2, 1), opacity 200ms ease;
    }

    .sidebar.collapsed {
        transform: translateX(-100%);
        opacity: 0;
        pointer-events: none;
    }

    .sidebar:not(.collapsed) {
        transform: translateX(0);
        opacity: 1;
        pointer-events: auto;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
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
    cursor: pointer;
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

/* Mobile responsive navbar */
@media (max-width: 768px) {
    .navbar {
        padding: 0.4rem;
    }

    .user-section {
        gap: 0.5rem;
    }

    .streak-widget {
        padding: 0.3rem 0.6rem;
        font-size: 0.875rem;
    }

    .streak-flame {
        font-size: 1rem;
    }

    .streak-count {
        font-size: 0.8125rem;
    }

    .theme-toggle-btn {
        width: 1.875rem;
        height: 1.875rem;
    }

    .workspace {
        padding: 0.75rem;
    }
}

@media (max-width: 480px) {
    .navbar {
        padding: 0.3rem;
    }

    .navbar-left {
        gap: 0.3rem;
    }

    .user-section {
        gap: 0.4rem;
    }

    .streak-widget {
        padding: 0.25rem 0.5rem;
        font-size: 0.8125rem;
    }

    .workspace {
        padding: 0.5rem;
    }
}
</style>
