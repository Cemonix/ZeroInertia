<template>
    <WorkspaceLayout>
        <template #sidebar>
            <ControlPanel v-model:activeView="activeWorkspaceView" />
            <ProjectPanel />
        </template>
        <template #navbar-left>
            <Button
                class="notes-nav-btn"
                text
                rounded
                @click="goToNotes"
                aria-label="Go to notes"
            >
                <font-awesome-icon icon="pen" />
                <span class="notes-nav-label">Notes</span>
            </Button>
            <Button
                class="media-nav-btn"
                text
                rounded
                @click="goToMedia"
                aria-label="Go to media"
            >
                <font-awesome-icon icon="table-columns" />
                <span class="media-nav-label">Media</span>
            </Button>
        </template>
        <template #default>
            <Transition name="fade-slide" mode="out-in">
                <div :key="viewKey">
                    <TodayBoard v-if="activeWorkspaceView === 'today'" />
                    <ProjectBoard v-else-if="activeWorkspaceView === 'project'" :project-id="selectedProjectId" />
                    <LabelManager v-else-if="activeWorkspaceView === 'labels'" />
                    <TaskFilters v-else-if="activeWorkspaceView === 'filters'" />
                    <div v-else class="workspace-placeholder">
                        <h2>Workspace</h2>
                        <p>Select a view from the control panel.</p>
                    </div>
                </div>
            </Transition>
        </template>
    </WorkspaceLayout>
</template>

<script lang="ts" setup>
import { ref, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useProjectStore } from '@/stores/project';
import { storeToRefs } from 'pinia';
import { useUiStore } from '@/stores/ui';
import ProjectPanel from '@/components/sidebar/ProjectPanel.vue';
import ControlPanel from '@/components/sidebar/ControlPanel.vue';
import ProjectBoard from '@/components/board/ProjectBoard.vue';
import LabelManager from '@/components/labels/LabelManager.vue';
import TaskFilters from '@/components/filters/TaskFilters.vue';
import TodayBoard from '@/components/today/TodayBoard.vue';
import WorkspaceLayout from '@/layouts/WorkspaceLayout.vue';

const projectStore = useProjectStore();
const uiStore = useUiStore();
const router = useRouter();

const { selectedProjectId } = storeToRefs(projectStore);
const activeWorkspaceView = ref<'today' | 'labels' | 'filters' | 'project'>('today');

// Unique key for transitions when switching views/projects
const viewKey = computed(() => {
    return activeWorkspaceView.value === 'project'
        ? `project:${selectedProjectId.value ?? 'none'}`
        : activeWorkspaceView.value;
});

const goToNotes = () => {
    if (router.currentRoute.value.path !== '/notes') {
        router.push('/notes');
    }
};

const goToMedia = () => {
    if (router.currentRoute.value.path !== '/media') {
        router.push('/media');
    }
};

// Add guards to prevent circular triggering between watchers
watch(selectedProjectId, (newProjectId) => {
    if (newProjectId && activeWorkspaceView.value !== 'project') {
        activeWorkspaceView.value = 'project';
    } else if (!newProjectId && activeWorkspaceView.value === 'project') {
        activeWorkspaceView.value = 'today';
    }
    // Close the mobile sidebar when a project is selected (board changes)
    if (newProjectId) {
        const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
        if (isMobile) uiStore.setSidebarCollapsed(true);
    }
}, { immediate: true });

// Deselect project when switching away from project view, only if a project is selected
watch(activeWorkspaceView, (newView) => {
    // Deselect project when leaving project view
    if (newView !== 'project' && selectedProjectId.value !== null) {
        projectStore.selectProject(null);
    }
    // Close the sidebar on mobile for any view change
    const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
    if (isMobile) uiStore.setSidebarCollapsed(true);
});
</script>

<style scoped>
/* Smooth fade/slide between workspace views */
.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: opacity 180ms ease, transform 240ms cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
    opacity: 0;
    transform: translateY(6px);
}

.notes-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
    transition: all 0.2s ease;
}

.notes-nav-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}

.media-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
    transition: all 0.2s ease;
}

.media-nav-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}

.workspace-placeholder {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
    justify-content: center;
    padding: 2rem;
    border: 1px dashed var(--p-content-border-color);
    border-radius: 12px;
    background-color: var(--p-content-background);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    color: var(--p-text-muted-color);
}

.workspace-placeholder h2 {
    margin: 0;
    color: var(--p-text-color);
}
</style>
