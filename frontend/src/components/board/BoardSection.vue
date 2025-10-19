<template>
    <div class="board-section">
        <!-- Section Header -->
        <div class="section-header">
            <div class="section-info" @click="toggleCollapse">
                <FontAwesomeIcon
                    :icon="isCollapsed ? 'chevron-right' : 'chevron-down'"
                    class="collapse-icon"
                />
                <h3 class="section-title">{{ title }}</h3>
            </div>

            <div class="section-actions">
                <Button
                    text
                    rounded
                    size="small"
                    @click.stop="handleSectionMenu"
                >
                    <template #icon>
                        <FontAwesomeIcon icon="ellipsis-vertical" />
                    </template>
                </Button>
            </div>
        </div>
        <div class="section-divider"></div>

        <!-- Task List -->
        <div v-if="!isCollapsed" class="task-list">
            <TaskCard
                v-for="task in tasks"
                :key="task.id"
                :task="task"
            />

            <!-- Add Task -->
            <Button
                label="Add task"
                text
                class="add-task-button"
                @click="openTaskModal"
            >
                <template #icon>
                    <FontAwesomeIcon icon="plus" />
                </template>
            </Button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useTaskStore } from "@/stores/task";
import TaskCard from "./TaskCard.vue";
import type { Section } from "@/models/section";

interface Props {
    projectId: string;
    section: Section;
}

const taskStore = useTaskStore();

const props = defineProps<Props>();

// State
const isCollapsed = ref(false);
const title = ref(props.section.title);

const tasks = computed(() => taskStore.getTasksBySection(props.section.id));

const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value;
};

function handleSectionMenu() {
    // Placeholder for section menu actions (edit, delete, etc.)
    console.log("Section menu clicked");
}

function openTaskModal() {
    taskStore.openTaskModal(props.section.id);
}
</script>

<style scoped>
.board-section {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid var(--p-surface-200);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 0.75rem;
    gap: 0.5rem;
}

.section-divider {
    height: 1px;
    background: var(--p-surface-200);
    margin-bottom: 0.75rem;
}

.section-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    flex: 1;
    user-select: none;
}

.section-info:hover .section-title {
    color: var(--p-primary-color);
}

.collapse-icon {
    font-size: 0.875rem;
    color: var(--p-text-color);
    opacity: 0.6;
    transition: transform 0.2s;
}

.section-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0;
    transition: color 0.2s;
}

.section-actions {
    display: flex;
    gap: 0.25rem;
}

.task-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.new-task-container {
    background: var(--p-surface-50);
    border: 2px solid var(--p-primary-color);
    border-radius: 6px;
    padding: 0.75rem;
}

.new-task-input {
    width: 100%;
    margin-bottom: 0.5rem;
}

.new-task-actions {
    display: flex;
    gap: 0.5rem;
}

.add-task-button {
    width: 100%;
    justify-content: flex-start;
    color: var(--p-text-color);
    opacity: 0.7;
}

.add-task-button:hover {
    background: var(--p-surface-50);
    opacity: 1;
}
</style>
