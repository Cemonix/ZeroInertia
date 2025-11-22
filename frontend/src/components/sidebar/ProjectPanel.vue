<template>
    <div class="projects-header">
        <h2 class="projects-title" v-show="!isPanelCollapsed">My Projects</h2>
        <Button class="projects-add-btn"
            @click="openProjectModal"
            text
            rounded
            aria-label="Add new project"
            v-show="!isPanelCollapsed"
        >
            <FontAwesomeIcon icon="plus" />
        </Button>
    </div>
    <div class="projects-content">
        <ProjectTree />
    </div>
    <ProjectModal v-model:visible="isProjectModalVisible" />
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import ProjectTree from '@/components/sidebar/ProjectTree.vue';
import ProjectModal from '@/components/sidebar/ProjectCreateModal.vue';

const isProjectModalVisible = ref(false);
const isPanelCollapsed = ref(false);

const openProjectModal = () => {
    isProjectModalVisible.value = true;
};
</script>

<style scoped>
.projects-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1rem 0.75rem 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
}

.projects-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0;
}

.projects-add-btn {
    color: var(--p-primary-color);
    transition: all 0.2s ease;
}

.projects-add-btn:hover {
    background-color: var(--p-primary-50);
    color: var(--p-primary-600);
}

.projects-content {
    flex: 1;
    overflow-y: auto;
}
</style>
