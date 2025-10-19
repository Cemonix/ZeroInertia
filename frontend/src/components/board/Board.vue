<template>
    <div class="board-container">
        <div v-if="!projectId" class="empty-state">
            <p>Select a project to view its tasks</p>
        </div>
        <div v-else>
            <div class="board-sections">
                <BoardSection
                    v-for="section in sectionStore.sortedSections"
                    :key="section.id"
                    :project-id="projectId"
                    :section="section"
                />
            </div>
            <Button
                @click="isSectionCreateVisible = true"
                class="add-section-btn"
                icon="pi pi-plus"
                label="Add Section"
                outlined
            />
        </div>
    </div>

    <SectionCreateModal
        v-if="projectId"
        v-model:visible="isSectionCreateVisible"
        :projectId="projectId"
    />

    <TaskModal v-if="projectId" :projectId="projectId" />
</template>

<script setup lang="ts">
import { ref, watch, withDefaults } from "vue";
import BoardSection from "./BoardSection.vue";
import SectionCreateModal from "./SectionCreateModal.vue";
import TaskModal from "./TaskModal.vue";
import { useSectionStore } from "@/stores/section";
import { useTaskStore } from "@/stores/task";

interface Props {
    projectId?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
    projectId: null,
});

const sectionStore = useSectionStore();
const taskStore = useTaskStore();

const isSectionCreateVisible = ref(false);

const loadSections = async () => {
    if (!props.projectId) {
        sectionStore.clearSections();
        return;
    }

    try {
        await Promise.all([
            sectionStore.loadsSectionsForProject(props.projectId),
            taskStore.loadTasksForProject(props.projectId),
        ]);
    } catch (error) {
        console.error("Failed to load sections and tasks:", error);
    }
};

watch(
    () => props.projectId,
    () => { loadSections(); },
    { immediate: true }
);
</script>

<style scoped>
.board-container {
    width: 100%;
    padding: 1rem;
    margin: 0 auto;
}

.board-header {
    margin-bottom: 1.5rem;
}

.board-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--p-text-color);
    margin: 0;
}

.board-sections {
    display: flex;
    flex-direction: column;
    gap: 0;
}

/* Future: Kanban view support */
.board-sections.kanban-view {
    flex-direction: row;
    gap: 1rem;
    overflow-x: auto;
}

.board-sections.kanban-view > * {
    min-width: 300px;
    max-width: 350px;
}

.empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    color: var(--p-text-muted-color);
    font-size: 1.125rem;
}

.add-section-btn {
    margin-top: 1rem;
    width: 100%;
}
</style>
