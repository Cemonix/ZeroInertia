<template>
    <div class="board-section" v-bind="attrs">
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
                    aria-haspopup="true"
                    aria-controls="section_menu"
                    @click.stop="toggleSectionMenu"
                >
                    <template #icon>
                        <FontAwesomeIcon icon="ellipsis-vertical" />
                    </template>
                </Button>
                <Menu ref="menu" id="section_menu" :model="items" :popup="true" />
            </div>
        </div>
        <div class="section-divider"></div>

        <!-- Show Completed Toggle -->
        <div v-if="!isCollapsed && tasks.some(t => t.completed)" class="section-controls">
            <label for="show-completed" class="control-label">Show completed</label>
            <ToggleSwitch v-model="showCompleted" inputId="show-completed" />
        </div>

        <!-- Task List -->
        <div v-if="!isCollapsed" class="task-list">
            <draggable
                v-model="draggableTasks"
                group="tasks"
                item-key="id"
                @change="handleDragChange"
                handle=".task-card"
                animation="200"
                ghost-class="task-ghost"
                :delay="200"
                :delay-on-touch-only="true"
            >
                <template #item="{element}">
                    <TaskCard :task="element" />
                </template>
            </draggable>

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

    <Dialog
        v-model:visible="isRenameDialogVisible"
        header="Rename Section"
        modal
        :style="{ width: '420px' }"
        :pt="{ content: { style: { padding: '1.5rem' } } }"
    >
        <div class="rename-section-form">
            <label for="section-rename-input">Section name</label>
            <InputText
                id="section-rename-input"
                v-model="newSectionTitle"
                autofocus
                @keyup.enter="handleRenameSection"
            />
            <div class="rename-section-actions">
                <Button
                    label="Cancel"
                    text
                    type="button"
                    @click="isRenameDialogVisible = false"
                />
                <Button
                    label="Save"
                    type="button"
                    :disabled="!newSectionTitle.trim() || newSectionTitle.trim() === title"
                    @click="handleRenameSection"
                />
            </div>
        </div>
    </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, useAttrs } from "vue";
import { useTaskStore } from "@/stores/task";
import { useSectionStore } from "@/stores/section";
import { useConfirm } from "primevue/useconfirm";
import draggable from "vuedraggable";
import TaskCard from "./TaskCard.vue";
import type { Section } from "@/models/section";
import type { Task } from "@/models/task";
import Menu from "primevue/menu";
import ToggleSwitch from "primevue/toggleswitch";
import { useToast } from "primevue";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";

const toast = useToast();

interface Props {
    projectId: string;
    section: Section;
}

const taskStore = useTaskStore();
const sectionStore = useSectionStore();
const confirm = useConfirm();

const props = defineProps<Props>();
const attrs = useAttrs();

// State
const menu = ref<InstanceType<typeof Menu>>();
const items = ref([
    {
        label: 'Options',
        items: [
            {
                label: 'Rename Section',
                command: () => openRenameDialog(),
            },
            {
                label: 'Delete Section',
                command: () => handleDeleteSection(),
            }
        ]
    }
]);
const isCollapsed = ref(false);
const title = ref(props.section.title);
const showCompleted = ref(false);
const draggableTasks = ref<Task[]>([]);
const isRenameDialogVisible = ref(false);
const newSectionTitle = ref(props.section.title);

const tasks = computed(() => taskStore.getTasksBySection(props.section.id));

// Filter and sort tasks: uncompleted first, then completed (when toggle is on)
const visibleTasks = computed(() => {
    if (showCompleted.value) {
        // Sort: uncompleted tasks first (by order_index), then completed tasks (by order_index)
        const uncompleted = tasks.value.filter(task => !task.completed);
        const completed = tasks.value.filter(task => task.completed);
        return [...uncompleted, ...completed];
    }
    return tasks.value.filter(task => !task.completed);
});

watch(visibleTasks, (newTasks) => {
    draggableTasks.value = [...newTasks];
}, { immediate: true });

watch(() => props.section.title, (newTitle) => {
    title.value = newTitle;
});

watch(isRenameDialogVisible, (visible) => {
    if (visible) {
        newSectionTitle.value = title.value;
    }
});

const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value;
};

async function handleDragChange(event: any) {
    // Handle task being added to this section from another section
    if (event.added) {
        const movedTask = event.added.element;
        // Update the task's section_id immediately
        movedTask.section_id = props.section.id;
    }

    // Recalculate order indices for all tasks in this section
    const taskIds = draggableTasks.value.map((task: Task) => task.id);

    // Don't send reorder request if there are no tasks
    if (taskIds.length === 0) {
        return;
    }

    try {
        await taskStore.reorderTasks(props.section.id, taskIds);
    } catch (error) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to reorder tasks" });
    }
}

function toggleSectionMenu(event: MouseEvent) {
    menu.value?.toggle(event);
}

function openTaskModal() {
    taskStore.openTaskModal(props.section.id);
}

function openRenameDialog() {
    isRenameDialogVisible.value = true;
}

async function handleRenameSection() {
    const trimmedTitle = newSectionTitle.value.trim();
    if (!trimmedTitle || trimmedTitle === title.value) {
        isRenameDialogVisible.value = false;
        return;
    }

    try {
        await sectionStore.updateSection(props.section.id, { title: trimmedTitle });
        toast.add({ severity: "success", summary: "Section renamed", detail: `Section is now "${trimmedTitle}".` });
    } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to rename section";
        toast.add({ severity: "error", summary: "Error", detail: message });
    } finally {
        isRenameDialogVisible.value = false;
    }
}

function handleDeleteSection() {
    confirm.require({
        message: "This will permanently delete this section and all its tasks. This action cannot be undone.",
        header: "Confirm Deletion",
        acceptClass: "p-button-danger",
        accept: async () => {
            try {
                await sectionStore.deleteSection(props.section.id);
            } catch (error) {
                toast.add({ severity: "error", summary: "Error", detail: "Failed to delete section" });
            }
        },
    });
}
</script>

<style scoped>
.board-section {
    background: var(--p-content-background);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid var(--p-content-border-color);
    /* Make sections behave like full-height columns in Kanban */
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
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
    background: var(--p-content-border-color);
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
    flex: 1;
    overflow-y: auto;
    min-height: 0;
}

.new-task-container {
    background: var(--p-content-hover-background);
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
    background: var(--p-content-hover-background);
    opacity: 1;
}

.rename-section-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.rename-section-form label {
    font-weight: 600;
    color: var(--p-text-color);
}

.rename-section-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}

/* Show Completed Toggle */
.section-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    padding: 0.5rem;
    background: var(--p-content-hover-background);
    border-radius: 6px;
}

.control-label {
    font-size: 0.875rem;
    color: var(--p-text-color);
    cursor: pointer;
    user-select: none;
}

/* Draggable ghost styles */
.task-ghost {
    opacity: 0.5;
    background: var(--p-primary-50);
    border: 2px dashed var(--p-primary-color);
}
</style>
