<template>
    <div class="today-container">
        <div class="today-header">
            <div class="today-header-content">
                <div v-if="viewMode === 'list'">
                    <h2>Today</h2>
                    <p class="today-date">{{ formattedDate }}</p>
                </div>
                <div class="view-toggle">
                    <Button
                        :class="{ 'active': viewMode === 'list' }"
                        text
                        @click="viewMode = 'list'"
                        title="List View"
                    >
                        <FontAwesomeIcon icon="list" class="view-toggle-icon" />
                        <span class="view-toggle-label">List</span>
                    </Button>
                    <Button
                        :class="{ 'active': viewMode === 'calendar' }"
                        text
                        @click="viewMode = 'calendar'"
                        title="Calendar View"
                    >
                        <FontAwesomeIcon icon="calendar" class="view-toggle-icon" />
                        <span class="view-toggle-label">Calendar</span>
                    </Button>
                </div>
            </div>
        </div>

        <div v-if="loading" class="loading-state">
            <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
            <p>Loading tasks...</p>
        </div>

        <div v-else-if="error" class="error-state">
            <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: var(--p-red-500)"></i>
            <p>{{ error }}</p>
        </div>

        <div v-else class="today-content">
            <!-- Calendar View -->
            <TodayCalendar
                v-if="viewMode === 'calendar'"
                :tasks="allTodayTasks"
                :current-date="new Date()"
            />

            <!-- List View -->
            <div v-else class="list-view">
                <!-- Overdue Tasks Section -->
                <div v-if="overdueTasks.length > 0" class="task-group overdue-group">
                <div class="task-group-header">
                    <FontAwesomeIcon icon="exclamation-circle" class="group-icon overdue-icon" />
                    <h3>Overdue</h3>
                    <span class="task-count">{{ overdueTasks.length }}</span>
                </div>
                <TransitionGroup name="task-list" tag="div" class="task-list">
                    <TaskCard
                        v-for="task in overdueTasks"
                        :key="task.id"
                        :task="task"
                    />
                </TransitionGroup>
            </div>

            <!-- Today's Tasks Section -->
            <div v-if="todayTasks.length > 0" class="task-group today-group">
                <div class="task-group-header">
                    <FontAwesomeIcon icon="calendar-day" class="group-icon today-icon" />
                    <h3>Today</h3>
                    <span class="task-count">{{ todayTasks.length }}</span>
                </div>
                <TransitionGroup name="task-list" tag="div" class="task-list">
                    <TaskCard
                        v-for="task in todayTasks"
                        :key="task.id"
                        :task="task"
                    />
                </TransitionGroup>
            </div>

            <!-- Empty State -->
            <div v-if="overdueTasks.length === 0 && todayTasks.length === 0" class="empty-state">
                <FontAwesomeIcon icon="check-circle" class="empty-icon" />
                <h3>No tasks for today</h3>
                <p>You're all caught up! Enjoy your day.</p>
            </div>
            </div>
        </div>
    </div>

    <TaskModal project-id="" />
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useTaskStore } from "@/stores/task";
import { useLabelStore } from "@/stores/label";
import { usePriorityStore } from "@/stores/priority";
import TaskCard from "@/components/board/TaskCard.vue";
import TaskModal from "@/components/board/TaskModal.vue";
import TodayCalendar from "@/components/today/TodayCalendar.vue";
import type { Task } from "@/models/task";

type ViewMode = 'list' | 'calendar';

const STORAGE_KEY = 'today-view-mode';

// Load saved view mode from localStorage, default to 'list'
const loadViewMode = (): ViewMode => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return (saved === 'list' || saved === 'calendar') ? saved : 'list';
};

const viewMode = ref<ViewMode>(loadViewMode());

const taskStore = useTaskStore();
const labelStore = useLabelStore();
const priorityStore = usePriorityStore();

const loading = computed(() => taskStore.loading);
const error = computed(() => taskStore.error);

const formattedDate = computed(() => {
    const today = new Date();
    return today.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
});

// Filter tasks to only show those with due dates that aren't completed or archived
// Use a stable reference by mapping to task IDs to prevent unnecessary re-computations
const getTasksWithDueDate = computed((): Task[] => {
    return taskStore.tasks.filter(task =>
        !task.completed &&
        !task.archived &&
        task.due_datetime !== null
    );
});

// Filter overdue tasks (due before today, not completed)
const overdueTasks = computed((): Task[] => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    return getTasksWithDueDate.value.filter(task => {
        const dueDate = new Date(task.due_datetime!);
        const taskDate = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());
        return taskDate < today;
    }).sort((a, b) => {
        // Sort by due date, earliest first
        return new Date(a.due_datetime!).getTime() - new Date(b.due_datetime!).getTime();
    });
});

// Filter today's tasks (due today, not completed)
const todayTasks = computed((): Task[] => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    return getTasksWithDueDate.value.filter(task => {
        const dueDate = new Date(task.due_datetime!);
        const taskDate = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());
        return taskDate.getTime() === today.getTime();
    }).sort((a, b) => {
        // Sort by due time, earliest first
        return new Date(a.due_datetime!).getTime() - new Date(b.due_datetime!).getTime();
    });
});

// Get tasks without a due date (treat as all-day tasks for calendar)
const tasksWithoutDate = computed((): Task[] => {
    return taskStore.tasks.filter(task =>
        !task.completed &&
        !task.archived &&
        task.due_datetime === null
    );
});

// Combined tasks for calendar view (includes overdue + today + no-date tasks)
const allTodayTasks = computed((): Task[] => {
    return [...overdueTasks.value, ...todayTasks.value, ...tasksWithoutDate.value];
});

// Save viewMode to localStorage whenever it changes
watch(viewMode, (newMode) => {
    localStorage.setItem(STORAGE_KEY, newMode);
});

onMounted(async () => {
    await Promise.all([
        taskStore.loadAllTasks(),
        labelStore.labels.length === 0 ? labelStore.loadLabels() : Promise.resolve(),
        priorityStore.priorities.length === 0 ? priorityStore.loadPriorities() : Promise.resolve(),
    ]);
});
</script>

<style scoped>
.today-container {
    padding: 1.5rem;
    max-width: 900px;
    margin: 0 auto;
    transition: max-width 0.3s ease;
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    box-sizing: border-box;
}

.today-container:has(.today-calendar-container) {
    max-width: 1400px;
}

.today-header {
    margin-bottom: 2rem;
}

.today-header-content {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 1rem;
}

.view-toggle {
    display: flex;
    gap: 0.25rem;
    background: color-mix(in srgb, var(--p-content-background) 95%, var(--p-text-color) 5%);
    padding: 0.25rem;
    border-radius: 8px;
    margin-left: auto;
}

.view-toggle :deep(.p-button) {
    min-width: 0;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.75rem;
}

.view-toggle :deep(.p-button.active) {
    background: var(--p-primary-color);
    color: white;
}

.view-toggle :deep(.p-button:not(.active):hover) {
    background: color-mix(in srgb, var(--p-content-background) 90%, var(--p-text-color) 10%);
}

.today-header h2 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--p-text-color);
    margin: 0 0 0.5rem 0;
}

.today-date {
    font-size: 1rem;
    color: var(--p-text-muted-color);
    margin: 0;
}

.view-toggle-label {
    font-size: 0.85rem;
}

.view-toggle-icon {
    font-size: 0.85rem;
}

.loading-state,
.error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 3rem;
    text-align: center;
    color: var(--p-text-muted-color);
}

.today-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    flex: 1;
    min-height: 0;
    overflow: hidden;
}

.task-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding-bottom: 1rem;
}

.task-group-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--p-content-border-color);
}

.task-group-header h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0;
    flex: 1;
}

.group-icon {
    font-size: 1.25rem;
}

.overdue-icon {
    color: var(--p-red-500);
}

.today-icon {
    color: var(--p-primary-color);
}

.task-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 1.5rem;
    height: 1.5rem;
    padding: 0 0.5rem;
    background: var(--p-primary-color);
    color: white;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.overdue-group .task-count {
    background: var(--p-red-500);
}

.task-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* Smooth transitions for task completion */
.task-list-move,
.task-list-enter-active,
.task-list-leave-active {
    transition: all 0.3s ease;
}

.task-list-enter-from {
    opacity: 0;
    transform: translateX(-20px);
}

.task-list-leave-to {
    opacity: 0;
    transform: translateX(20px);
}

.task-list-leave-active {
    position: absolute;
    width: 100%;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 4rem 2rem;
    text-align: center;
}

.empty-icon {
    font-size: 4rem;
    color: var(--p-green-500);
    opacity: 0.5;
}

.empty-state h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0;
}

.empty-state p {
    font-size: 1rem;
    color: var(--p-text-muted-color);
    margin: 0;
}
</style>
