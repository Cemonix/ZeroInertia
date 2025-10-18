<template>
    <div class="board-section">
        <!-- Section Header -->
        <div class="section-header">
            <div class="section-info" @click="toggleCollapse">
                <FontAwesomeIcon
                    :icon="isCollapsed ? 'chevron-right' : 'chevron-down'"
                    class="collapse-icon"
                />
                <h3 class="section-title">{{ section.title }}</h3>
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
            <!-- Existing Tasks -->
            <TaskCard
                v-for="task in tasks"
                :key="task.id"
                :task="task"
                @click="handleTaskClick(task.id)"
                @toggle-complete="
                    handleToggleTaskComplete(task.id, task.is_done)
                "
                @delete="handleDeleteTask(task.id)"
            />

            <!-- Inline Task Creation -->
            <div v-if="isAddingTask" class="new-task-container">
                <InputText
                    v-model="newTaskTitle"
                    class="new-task-input"
                    placeholder="Task title..."
                    @keydown="handleKeydown"
                    @blur="cancelAddingTask"
                />
                <div class="new-task-actions">
                    <Button
                        label="Add"
                        size="small"
                        @mousedown.prevent="handleCreateTask"
                    />
                    <Button
                        label="Cancel"
                        size="small"
                        text
                        @mousedown.prevent="cancelAddingTask"
                    />
                </div>
            </div>

            <!-- Add Task Button (when not adding) -->
            <Button
                v-else
                label="Add task"
                text
                class="add-task-button"
                @click="startAddingTask"
            >
                <template #icon>
                    <FontAwesomeIcon icon="plus" />
                </template>
            </Button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { Section } from "@/models/section";
import type { Task } from "@/models/task";
import TaskCard from "./TaskCard.vue";

interface Props {
    section: Section;
    tasks: Task[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
    createTask: [title: string, projectId: string, sectionId: string];
    updateTask: [taskId: string, updates: Partial<Task>];
    deleteTask: [taskId: string];
}>();

// State
const isCollapsed = ref(false);
const isAddingTask = ref(false);
const newTaskTitle = ref("");

// Methods
const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value;
};

const startAddingTask = () => {
    isAddingTask.value = true;
    // Focus input on next tick
    setTimeout(() => {
        const input = document.querySelector(
            ".new-task-input"
        ) as HTMLInputElement;
        input?.focus();
    }, 0);
};

const handleCreateTask = () => {
    const title = newTaskTitle.value.trim();
    if (title) {
        emit("createTask", title, props.section.project_id, props.section.id);
        newTaskTitle.value = "";
        isAddingTask.value = false;
    }
};

const cancelAddingTask = () => {
    newTaskTitle.value = "";
    isAddingTask.value = false;
};

const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === "Enter") {
        handleCreateTask();
    } else if (event.key === "Escape") {
        cancelAddingTask();
    }
};

const handleTaskClick = (taskId: string) => {
    // TODO: Open TaskModal for full task details/editing
    console.log("Task clicked:", taskId);
};

const handleToggleTaskComplete = (taskId: string, isDone: boolean) => {
    emit("updateTask", taskId, { is_done: !isDone });
};

const handleDeleteTask = (taskId: string) => {
    emit("deleteTask", taskId);
};

const handleSectionMenu = () => {
    // TODO: Open section menu (rename, delete, etc.)
    console.log("Section menu clicked");
};
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
