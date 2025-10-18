<template>
    <div class="board-container">
        <div v-if="!projectId" class="empty-state">
            <p>Select a project to view its tasks</p>
        </div>
        <div v-else>
            <div class="board-sections">
                <BoardSection
                    v-for="section in sectionStore.sections"
                    :key="section.id"
                    :section="section"
                    :tasks="getTasksForSection(section.id)"
                    @create-task="handleCreateTask"
                    @update-task="handleUpdateTask"
                    @delete-task="handleDeleteTask"
                />
            </div>
            <Button
                @click="isSectionDialogVisible = true"
                class="add-section-btn"
                icon="pi pi-plus"
                label="Add Section"
                outlined
            />
        </div>
    </div>

    <SectionCreateModal
        v-model:visible="isSectionDialogVisible"
        @create="handleCreateSection"
    />
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import type { Task } from "@/models/task";
import BoardSection from "./BoardSection.vue";
import SectionCreateModal from "./SectionCreateModal.vue";
import Button from "primevue/button";
import { useSectionStore } from "@/stores/section";
import { useTaskStore } from "@/stores/task";

const props = defineProps<{
    projectId: string | null;
}>();

const sectionStore = useSectionStore();
const taskStore = useTaskStore();

const isSectionDialogVisible = ref(false);

const getTasksForSection = (sectionId: string) => {
    return taskStore.getTasksBySection(sectionId);
};

const handleCreateSection = async (title: string) => {
    if (!props.projectId) return;

    try {
        const nextOrderIndex = sectionStore.sections.length;
        await sectionStore.createSection({
            title,
            project_id: props.projectId,
            order_index: nextOrderIndex,
        });
    } catch (error) {
        console.error("Failed to create section:", error);
    }
};

const loadProjectData = async () => {
    if (!props.projectId) {
        sectionStore.sections = [];
        taskStore.tasks = [];
        return;
    }

    try {
        // Load sections and tasks for the project in parallel
        await Promise.all([
            sectionStore.fetchSectionsByProject(props.projectId),
            taskStore.fetchTasksByProject(props.projectId)
        ]);
    } catch (error) {
        console.error("Failed to load project data:", error);
    }
};

// Create a new task
const handleCreateTask = async (title: string, projectId: string, sectionId: string) => {
    try {
        await taskStore.createTask({
            title,
            section_id: sectionId,
            project_id: projectId,
            description: null,
        });
    } catch (error) {
        console.error("Failed to create task:", error);
    }
};

// Update a task
const handleUpdateTask = async (taskId: string, updates: Partial<Task>) => {
    try {
        await taskStore.updateTask(taskId, updates);
    } catch (error) {
        console.error("Failed to update task:", error);
    }
};

// Delete a task
const handleDeleteTask = async (taskId: string) => {
    try {
        await taskStore.deleteTask(taskId);
    } catch (error) {
        console.error("Failed to delete task:", error);
    }
};

// Watch for project selection changes
watch(() => props.projectId, () => {
    loadProjectData();
}, { immediate: true });
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
