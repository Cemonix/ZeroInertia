<template>
    <div class="task-filters-layout">
        <aside class="task-filters-panel">
            <header class="panel-header">
                <div>
                    <h2>Task Filters</h2>
                    <p>Scan every task across projects and focus on what matters right now.</p>
                </div>
                <Button
                    v-if="filtersActive"
                    text
                    class="clear-button"
                    @click="resetFilters"
                >
                    Reset
                </Button>
            </header>

            <div class="panel-body">
                <div class="filter-group">
                    <label for="task-filter-search">Search</label>
                    <InputText
                        id="task-filter-search"
                        v-model="searchTerm"
                        placeholder="Search by title or description"
                        autocomplete="off"
                    />
                </div>

                <div class="filter-group">
                    <label>Status</label>
                    <div class="status-options">
                        <Button
                            v-for="option in statusOptions"
                            :key="option.value"
                            :label="option.label"
                            :outlined="statusFilter !== option.value"
                            size="small"
                            @click="statusFilter = option.value"
                        />
                    </div>
                </div>

                <div class="filter-group">
                    <label for="task-filter-due">Due Date</label>
                    <Dropdown
                        id="task-filter-due"
                        v-model="dueFilter"
                        :options="dueOptions"
                        option-label="label"
                        option-value="value"
                        placeholder="Any due date"
                        class="w-full"
                    />
                </div>

                <div class="filter-group">
                    <label for="task-filter-projects">Projects</label>
                    <MultiSelect
                        id="task-filter-projects"
                        v-model="selectedProjects"
                        :options="projectOptions"
                        option-label="label"
                        option-value="value"
                        placeholder="All projects"
                        display="chip"
                        class="w-full"
                    />
                </div>

                <div class="filter-group">
                    <label for="task-filter-labels">Labels</label>
                    <MultiSelect
                        id="task-filter-labels"
                        v-model="selectedLabels"
                        :options="labelOptions"
                        option-label="label"
                        option-value="value"
                        placeholder="Any label"
                        display="chip"
                        class="w-full"
                    >
                        <template #option="slotProps">
                            <div class="label-option">
                                <span
                                    class="label-swatch"
                                    :style="{ backgroundColor: slotProps.option.meta?.color }"
                                />
                                <span>{{ slotProps.option.label }}</span>
                            </div>
                        </template>
                    </MultiSelect>
                </div>

                <div class="filter-group">
                    <label for="task-filter-priority">Priority</label>
                    <MultiSelect
                        id="task-filter-priority"
                        v-model="selectedPriorities"
                        :options="priorityOptions"
                        option-label="label"
                        option-value="value"
                        placeholder="Any priority"
                        display="chip"
                        class="w-full"
                    >
                        <template #option="slotProps">
                            <div class="priority-option">
                                <FontAwesomeIcon icon="flag" :style="{ color: slotProps.option.meta?.color }" />
                                <span>{{ slotProps.option.label }}</span>
                            </div>
                        </template>
                    </MultiSelect>
                </div>
            </div>
        </aside>

        <section class="task-results">
            <header class="results-header">
                <div>
                    <h2>Matching Tasks</h2>
                    <p v-if="filteredCount > 0">
                        Showing {{ filteredCount }} of {{ totalTasks }} tasks
                    </p>
                    <p v-else>
                        No tasks match the current filters
                    </p>
                </div>
                <Dropdown
                    v-model="sortOption"
                    :options="sortOptions"
                    option-label="label"
                    option-value="value"
                    size="small"
                    class="sort-dropdown"
                />
            </header>

            <div class="results-body">
                <div v-if="loading" class="results-loading">
                    <FontAwesomeIcon icon="spinner" class="spinner" />
                    <span>Loading tasks...</span>
                </div>

                <div
                    v-else-if="error"
                    class="results-empty"
                >
                    <FontAwesomeIcon icon="triangle-exclamation" class="empty-icon" />
                    <h3>Could not load tasks</h3>
                    <p>{{ error }}</p>
                    <Button @click="refreshTasks">
                        Retry
                    </Button>
                </div>

                <div
                    v-else-if="!filteredTasks.length"
                    class="results-empty"
                >
                    <FontAwesomeIcon icon="filter" class="empty-icon" />
                    <h3>No tasks found</h3>
                    <p>
                        Try adjusting your filters or clearing them to see more tasks.
                    </p>
                    <Button v-if="filtersActive" @click="resetFilters">
                        Clear filters
                    </Button>
                </div>

                <ul v-else class="results-list">
                    <li v-for="task in sortedTasks" :key="task.id" class="results-item">
                        <TaskCard :task="task" />
                        <div class="task-meta">
                            <span class="task-meta-pill">
                                <FontAwesomeIcon icon="fa fa-house" />
                                {{ getProjectName(task.project_id) }}
                            </span>
                            <span
                                v-if="task.completed"
                                class="task-meta-pill completed"
                            >
                                <FontAwesomeIcon icon="check" />
                                Completed
                            </span>
                        </div>
                    </li>
                </ul>
            </div>
        </section>
    </div>

    <TaskModal
        v-if="taskStore.isTaskModalVisible"
        :project-id="modalProjectId"
    />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { storeToRefs } from "pinia";
import Dropdown from "primevue/dropdown";
import MultiSelect from "primevue/multiselect";
import { useToast } from "primevue";
import { useTaskStore } from "@/stores/task";
import { useProjectStore } from "@/stores/project";
import { useLabelStore } from "@/stores/label";
import { usePriorityStore } from "@/stores/priority";
import TaskCard from "@/components/tasks/TaskCard.vue";
import TaskModal from "@/components/tasks/TaskModal.vue";
import type { Task } from "@/models/task";

const taskStore = useTaskStore();
const projectStore = useProjectStore();
const labelStore = useLabelStore();
const priorityStore = usePriorityStore();
const toast = useToast();

const { tasks, loading, error } = storeToRefs(taskStore);

const searchTerm = ref("");
const statusFilter = ref<"all" | "active" | "completed">("all");
const dueFilter = ref<"any" | "overdue" | "today" | "this_week" | "no_due">("any");
const selectedProjects = ref<string[]>([]);
const selectedLabels = ref<string[]>([]);
const selectedPriorities = ref<string[]>([]);
const sortOption = ref<"smart" | "dueAsc" | "dueDesc" | "recent">("smart");

const statusOptions = [
    { label: "All", value: "all" as const },
    { label: "Active", value: "active" as const },
    { label: "Completed", value: "completed" as const },
];

const dueOptions = [
    { label: "Any due date", value: "any" as const },
    { label: "Overdue", value: "overdue" as const },
    { label: "Due today", value: "today" as const },
    { label: "Due this week", value: "this_week" as const },
    { label: "No due date", value: "no_due" as const },
];

const sortOptions = [
    { label: "Recommended", value: "smart" as const },
    { label: "Due date ↑", value: "dueAsc" as const },
    { label: "Due date ↓", value: "dueDesc" as const },
    { label: "Recently updated", value: "recent" as const },
];

const projectOptions = computed(() =>
    projectStore.projects.map(project => ({
        label: project.title,
        value: project.id,
    }))
);

const labelOptions = computed(() =>
    labelStore.sortedLabels.map(label => ({
        label: label.name,
        value: label.id,
        meta: { color: label.color },
    }))
);

const priorityOptions = computed(() =>
    priorityStore.priorities.map(priority => ({
        label: priority.name,
        value: priority.id,
        meta: { color: priority.color },
    }))
);

const filtersActive = computed(() => (
    searchTerm.value.trim().length > 0 ||
    statusFilter.value !== "all" ||
    dueFilter.value !== "any" ||
    selectedProjects.value.length > 0 ||
    selectedLabels.value.length > 0 ||
    selectedPriorities.value.length > 0 ||
    sortOption.value !== "smart"
));

const totalTasks = computed(() => tasks.value.length);

function getDueCategory(task: Task): "overdue" | "today" | "this_week" | "no_due" | "future" {
    if (!task.due_datetime) {
        return "no_due";
    }

    const dueDate = new Date(task.due_datetime);
    const now = new Date();
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const endOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);

    if (!task.completed && dueDate < startOfToday) {
        return "overdue";
    }

    if (dueDate >= startOfToday && dueDate < endOfToday) {
        return "today";
    }

    const dayOfWeek = startOfToday.getDay();
    const startOfWeek = new Date(startOfToday);
    startOfWeek.setDate(startOfWeek.getDate() - dayOfWeek);
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 7);

    if (dueDate >= startOfWeek && dueDate < endOfWeek) {
        return "this_week";
    }

    return "future";
}

function matchesLabels(task: Task, requiredLabels: string[]): boolean {
    if (requiredLabels.length === 0) {
        return true;
    }
    const labelIds = new Set<string>(
        task.label_ids ??
        (task.labels ? task.labels.map(label => label.id) : [])
    );
    return requiredLabels.some(labelId => labelIds.has(labelId));
}

const filteredTasks = computed(() => {
    const normalizedSearch = searchTerm.value.trim().toLowerCase();

    return tasks.value.filter(task => {
        if (statusFilter.value === "active" && task.completed) {
            return false;
        }
        if (statusFilter.value === "completed" && !task.completed) {
            return false;
        }

        if (selectedProjects.value.length > 0 && !selectedProjects.value.includes(task.project_id)) {
            return false;
        }

        if (selectedPriorities.value.length > 0) {
            if (!task.priority_id || !selectedPriorities.value.includes(task.priority_id)) {
                return false;
            }
        }

        if (!matchesLabels(task, selectedLabels.value)) {
            return false;
        }

        if (dueFilter.value !== "any") {
            const category = getDueCategory(task);
            if (dueFilter.value === "no_due") {
                if (category !== "no_due") {
                    return false;
                }
            } else if (category !== dueFilter.value) {
                return false;
            }
        }

        if (normalizedSearch.length > 0) {
            const haystack = `${task.title} ${task.description ?? ""}`.toLowerCase();
            if (!haystack.includes(normalizedSearch)) {
                return false;
            }
        }

        return true;
    });
});

const filteredCount = computed(() => filteredTasks.value.length);

function compareDueAscending(a: Task, b: Task) {
    const dueA = a.due_datetime ? new Date(a.due_datetime).getTime() : Number.MAX_SAFE_INTEGER;
    const dueB = b.due_datetime ? new Date(b.due_datetime).getTime() : Number.MAX_SAFE_INTEGER;
    if (dueA === dueB) {
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    }
    return dueA - dueB;
}

function compareDueDescending(a: Task, b: Task) {
    const dueA = a.due_datetime ? new Date(a.due_datetime).getTime() : Number.MIN_SAFE_INTEGER;
    const dueB = b.due_datetime ? new Date(b.due_datetime).getTime() : Number.MIN_SAFE_INTEGER;
    if (dueA === dueB) {
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    }
    return dueB - dueA;
}

const sortedTasks = computed(() => {
    const tasksCopy = [...filteredTasks.value];

    switch (sortOption.value) {
        case "dueAsc":
            return tasksCopy.sort(compareDueAscending);
        case "dueDesc":
            return tasksCopy.sort(compareDueDescending);
        case "recent":
            return tasksCopy.sort((a, b) => {
                return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
            });
        case "smart":
        default:
            return tasksCopy.sort((a, b) => {
                if (a.completed !== b.completed) {
                    return a.completed ? 1 : -1;
                }
                const dueComparison = compareDueAscending(a, b);
                if (dueComparison !== 0) {
                    return dueComparison;
                }
                return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
            });
    }
});

const modalProjectId = computed(() => {
    return taskStore.getCurrentTask?.project_id ?? "";
});

const getProjectName = (projectId: string) => {
    const project = projectStore.getProjectById(projectId);
    return project ? project.title : "Unknown project";
};

const resetFilters = () => {
    searchTerm.value = "";
    statusFilter.value = "all";
    dueFilter.value = "any";
    selectedProjects.value = [];
    selectedLabels.value = [];
    selectedPriorities.value = [];
    sortOption.value = "smart";
};

const refreshTasks = async () => {
    try {
        await taskStore.loadAllTasks();
    } catch (err) {
        const detail = err instanceof Error ? err.message : "Failed to load tasks";
        toast.add({ severity: "error", summary: "Tasks", detail, life: 4000 });
    }
};

onMounted(async () => {
    try {
        await Promise.all([
            projectStore.projects.length ? Promise.resolve() : projectStore.loadProjects(),
            priorityStore.priorities.length ? Promise.resolve() : priorityStore.loadPriorities(),
            labelStore.labels.length ? Promise.resolve() : labelStore.loadLabels(),
        ]);
    } catch (error) {
        const detail = error instanceof Error ? error.message : "Failed to load filter data";
        toast.add({ severity: "error", summary: "Filters", detail, life: 4000 });
    }

    try {
        await taskStore.loadAllTasks();
    } catch (error) {
        const detail = error instanceof Error ? error.message : "Failed to load tasks";
        toast.add({ severity: "error", summary: "Tasks", detail, life: 4000 });
    }
});
</script>

<style scoped>
.task-filters-layout {
    display: grid;
    grid-template-columns: minmax(280px, 320px) 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
    background: var(--p-surface-ground);
}

.task-filters-panel {
    border: 1px solid var(--p-content-border-color);
    border-radius: 12px;
    background: var(--p-content-background);
    display: flex;
    flex-direction: column;
    min-height: 100%;
}

.panel-header {
    padding: 1.25rem 1.5rem 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
}

.panel-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--p-text-color);
}

.panel-header p {
    margin: 0.5rem 0 0;
    color: var(--p-text-muted-color);
    font-size: 0.9rem;
}

.clear-button {
    margin-top: 0.75rem;
    padding: 0;
}

.panel-body {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    padding: 1.5rem;
    overflow-y: auto;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.filter-group label {
    font-weight: 600;
    color: var(--p-text-color);
    font-size: 0.9rem;
}

.status-options {
    display: flex;
    gap: 0.5rem;
}

.label-option,
.priority-option,
.label-value,
.priority-value {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.label-swatch {
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 50%;
    flex-shrink: 0;
}

.task-results {
    border: 1px solid var(--p-content-border-color);
    border-radius: 12px;
    background: var(--p-content-background);
    display: flex;
    flex-direction: column;
    min-height: 100%;
}

.results-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--p-content-border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.results-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--p-text-color);
}

.results-header p {
    margin: 0.35rem 0 0;
    color: var(--p-text-muted-color);
    font-size: 0.9rem;
}

.sort-dropdown {
    min-width: 180px;
}

.results-body {
    flex: 1;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
}

.results-loading,
.results-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    color: var(--p-text-muted-color);
    text-align: center;
}

.spinner {
    animation: spin 1s linear infinite;
    font-size: 1.5rem;
}

.results-empty h3 {
    margin: 0.5rem 0 0;
    color: var(--p-text-color);
}

.results-empty p {
    margin: 0;
    max-width: 320px;
}

.empty-icon {
    font-size: 1.75rem;
    color: var(--p-text-muted-color);
}

.results-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    list-style: none;
    padding: 0;
    margin: 0;
}

.results-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.task-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding-left: 0.5rem;
}

.task-meta-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 999px;
    background: var(--p-content-hover-background);
    color: var(--p-text-muted-color);
}

.task-meta-pill.completed {
    background: rgba(34, 197, 94, 0.15);
    color: var(--p-green-600);
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
    .task-filters-layout {
        grid-template-columns: 1fr;
    }
}
</style>
