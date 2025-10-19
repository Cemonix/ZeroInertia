<template>
    <Toast />
    <main class="main-grid">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2 class="sidebar-title">My Projects</h2>
                <Button
                class="sidebar-add-btn"
                @click="openProjectModal"
                text
                rounded
                aria-label="Add new project"
                >
                <font-awesome-icon icon="plus" />
            </Button>
            </div>
            <div class="sidebar-content">
                <ProjectTree />
            </div>
        </aside>
        <div class="content">
            <nav class="navbar">
                <Button v-if="!authStore.isAuthenticated" @click="login" class="login-btn">Log in</Button>
                <div v-else class="user-section">
                    <div class="streak-widget" v-if="streakStore.currentStreak > 0">
                        <span class="streak-flame">🔥</span>
                        <span class="streak-count">{{ streakStore.currentStreak }}</span>
                    </div>
                    <Avatar label="C" size="medium" shape="circle"/>
                </div>
            </nav>
            <Board :project-id="selectedProjectId" />
        </div>
    </main>
    <ProjectModal v-model:visible="isProjectModalVisible" />
</template>

<script lang="ts" setup>
import { useAuthStore } from '@/stores/auth';
import { useProjectStore } from '@/stores/project';
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import Toast from 'primevue/toast';
import Avatar from 'primevue/avatar';
import ProjectModal from '@/components/sidebar/ProjectCreateModal.vue';
import ProjectTree from '@/components/sidebar/ProjectTree.vue';
import Board from '@/components/board/Board.vue';
import { useStreakStore } from '@/stores/streak';

const authStore = useAuthStore();
const projectStore = useProjectStore();
const streakStore = useStreakStore();

const isProjectModalVisible = ref(false);
const { selectedProjectId } = storeToRefs(projectStore);

const login = () => {
    authStore.redirectToLogin();
};

const openProjectModal = () => {
    isProjectModalVisible.value = true;
};
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
}

.sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1rem 0.75rem 1rem;
    border-bottom: 1px solid var(--p-surface-200);
}

.sidebar-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0;
}

.sidebar-add-btn {
    color: var(--p-primary-color);
    transition: all 0.2s ease;
}

.sidebar-add-btn:hover {
    background-color: var(--p-primary-50);
    color: var(--p-primary-600);
}

.sidebar-content {
    flex: 1;
    overflow-y: auto;
}

.content {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.navbar {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    background: var(--p-blue-50);
    padding: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
</style>