<template>
    <main class="main-grid">
        <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
            <NoteExplorerPanel />
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
                    <Button
                        class="home-nav-btn"
                        text
                        rounded
                        @click="goHome"
                        aria-label="Return to home"
                    >
                        <font-awesome-icon icon="house" />
                        <span class="home-nav-label">Home</span>
                    </Button>
                </div>
                <Button v-if="!authStore.isAuthenticated" @click="login" class="login-btn">Log in</Button>
                <div v-else class="user-section">
                    <div class="streak-widget">
                        <span v-if="streakStore.currentStreak > 0" class="streak-flame">🔥</span>
                        <span class="streak-count">{{ streakStore.currentStreak }}</span>
                    </div>
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
                <NoteEditor />
            </section>
        </div>
    </main>
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import Avatar from "primevue/avatar";
import Menu from "primevue/menu";
import { useAuthStore } from "@/stores/auth";
import { useStreakStore } from "@/stores/streak";
import { useNoteStore } from "@/stores/note";
import NoteExplorerPanel from "@/components/notes/NoteExplorerPanel.vue";
import NoteEditor from "@/components/notes/NoteEditor.vue";

const authStore = useAuthStore();
const streakStore = useStreakStore();
const noteStore = useNoteStore();
const router = useRouter();

const userMenu = ref();
const isSidebarCollapsed = ref(false);

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

const toggleUserMenu = (event: Event) => {
    userMenu.value.toggle(event);
};

const login = () => {
    authStore.redirectToLogin();
};

const goHome = () => {
    if (router.currentRoute.value.path !== "/home") {
        router.push("/home");
    }
};

const checkMobileView = () => {
    const mobileBreakpoint = 768;
    if (window.innerWidth < mobileBreakpoint) {
        isSidebarCollapsed.value = true;
    }
};

onMounted(async () => {
    if (authStore.isAuthenticated) {
        streakStore.loadStreak();
    }
    await noteStore.loadNotes();
    checkMobileView();
    window.addEventListener("resize", checkMobileView);
});

onUnmounted(() => {
    window.removeEventListener("resize", checkMobileView);
});
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
    background: var(--p-surface-50);
    border-right: 1px solid var(--p-surface-200);
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
    background: var(--p-blue-50);
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
    background-color: var(--p-surface-100);
    color: var(--p-primary-color);
}

.home-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
    transition: all 0.2s ease;
}

.home-nav-btn:hover {
    background-color: var(--p-surface-100);
    color: var(--p-primary-color);
}

.login-btn {
    background-color: var(--p-blue-500);
    color: white;
    border: none;
    border-radius: 5px;
    padding: 12px 20px;
    text-align: center;
    text-decoration: none;
    font-size: 1rem;
    margin: 4px 2px;
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
    background: var(--p-surface-100);
}

:deep(.user-info) {
    font-weight: 600;
    color: var(--p-text-color);
    padding: 0.5rem 1rem;
}
</style>
