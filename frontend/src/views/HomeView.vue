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
        </template>
        <template #default>
            <div
                v-if="activeWorkspaceView === 'today'"
                class="workspace-placeholder"
            >
                <h2>Today</h2>
                <p>Today's focus view is under construction.</p>
            </div>
            <Board
                v-else-if="activeWorkspaceView === 'project'"
                :project-id="selectedProjectId"
            />
            <LabelManager
                v-else-if="activeWorkspaceView === 'labels'"
            />
            <div
                v-else
                class="workspace-placeholder"
            >
                <h2>Filters</h2>
                <p>Filters are coming soon. Stay tuned!</p>
            </div>
        </template>
    </WorkspaceLayout>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useProjectStore } from '@/stores/project';
import { storeToRefs } from 'pinia';
import ProjectPanel from '@/components/sidebar/ProjectPanel.vue';
import ControlPanel from '@/components/sidebar/ControlPanel.vue';
import Board from '@/components/board/Board.vue';
import LabelManager from '@/components/labels/LabelManager.vue';
import WorkspaceLayout from '@/layouts/WorkspaceLayout.vue';

const projectStore = useProjectStore();
const router = useRouter();

const { selectedProjectId } = storeToRefs(projectStore);
const activeWorkspaceView = ref<'today' | 'labels' | 'filters' | 'project'>('today');

const goToNotes = () => {
    if (router.currentRoute.value.path !== '/notes') {
        router.push('/notes');
    }
};

// Add guards to prevent circular triggering between watchers
watch(selectedProjectId, (newProjectId) => {
    if (newProjectId && activeWorkspaceView.value !== 'project') {
        activeWorkspaceView.value = 'project';
    } else if (!newProjectId && activeWorkspaceView.value === 'project') {
        activeWorkspaceView.value = 'today';
    }
}, { immediate: true });

// Deselect project when switching away from project view, only if a project is selected
watch(activeWorkspaceView, (newView) => {
    if (newView !== 'project' && selectedProjectId.value !== null) {
        projectStore.selectProject(null);
    }
});
</script>

<style scoped>
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
