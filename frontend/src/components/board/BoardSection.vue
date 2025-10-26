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
                item-key="id"
                @end="handleDragEnd"
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
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
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

const toast = useToast();

interface Props {
    projectId: string;
    section: Section;
}

const taskStore = useTaskStore();
const sectionStore = useSectionStore();
const confirm = useConfirm();

const props = defineProps<Props>();

// State
const menu = ref<InstanceType<typeof Menu>>();
const items = ref([
    {
        label: 'Options',
        items: [
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

const tasks = computed(() => taskStore.getTasksBySection(props.section.id));

// Filter tasks based on showCompleted toggle
const visibleTasks = computed(() => {
    if (showCompleted.value) {
        return tasks.value;
    }
    return tasks.value.filter(task => !task.completed);
});

watch(visibleTasks, (newTasks) => {
    draggableTasks.value = [...newTasks];
}, { immediate: true });

const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value;
};

async function handleDragEnd() {
    const taskIds = draggableTasks.value.map((task: Task) => task.id);
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

/* Show Completed Toggle */
.section-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    padding: 0.5rem;
    background: var(--p-surface-50);
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
