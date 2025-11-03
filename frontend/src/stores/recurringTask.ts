import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type {
    RecurringTask,
    RecurringTaskCreateInput,
    RecurringTaskUpdateInput
} from "@/models/recurringTask";
import { recurringTaskService } from "@/services/recurringTaskService";

export const useRecurringTaskStore = defineStore("recurringTask", () => {
    const recurringTasks = ref<RecurringTask[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const getRecurringTasksByProject = computed(() => {
        return (projectId: string) =>
            recurringTasks.value.filter(task => task.project_id === projectId);
    });

    const getRecurringTaskById = computed(() => {
        return (recurringTaskId: string) =>
            recurringTasks.value.find(task => task.id === recurringTaskId) ?? null;
    });

    function upsertRecurringTask(task: RecurringTask) {
        const index = recurringTasks.value.findIndex(item => item.id === task.id);
        if (index === -1) {
            recurringTasks.value.push(task);
        } else {
            recurringTasks.value[index] = task;
        }
    }

    function removeRecurringTask(taskId: string) {
        recurringTasks.value = recurringTasks.value.filter(task => task.id !== taskId);
    }

    async function loadRecurringTasks(params?: { projectId?: string; includeInactive?: boolean }) {
        loading.value = true;
        error.value = null;

        try {
            const tasks = await recurringTaskService.getRecurringTasks({
                project_id: params?.projectId,
                include_inactive: params?.includeInactive
            });

            if (params?.projectId) {
                recurringTasks.value = recurringTasks.value
                    .filter(task => task.project_id !== params.projectId)
                    .concat(tasks);
            } else {
                recurringTasks.value = tasks;
            }

            return tasks;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load recurring tasks";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function createRecurringTask(payload: RecurringTaskCreateInput) {
        loading.value = true;
        error.value = null;

        try {
            const task = await recurringTaskService.createRecurringTask(payload);
            upsertRecurringTask(task);
            return task;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to create recurring task";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateRecurringTask(recurringTaskId: string, updates: RecurringTaskUpdateInput) {
        loading.value = true;
        error.value = null;

        try {
            const updated = await recurringTaskService.updateRecurringTask(recurringTaskId, updates);
            upsertRecurringTask(updated);
            return updated;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to update recurring task";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteRecurringTask(recurringTaskId: string) {
        loading.value = true;
        error.value = null;

        try {
            await recurringTaskService.deleteRecurringTask(recurringTaskId);
            removeRecurringTask(recurringTaskId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to delete recurring task";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function pauseRecurringTask(recurringTaskId: string) {
        loading.value = true;
        error.value = null;

        try {
            const paused = await recurringTaskService.pauseRecurringTask(recurringTaskId);
            upsertRecurringTask(paused);
            return paused;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to pause recurring task";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function resumeRecurringTask(recurringTaskId: string) {
        loading.value = true;
        error.value = null;

        try {
            const resumed = await recurringTaskService.resumeRecurringTask(recurringTaskId);
            upsertRecurringTask(resumed);
            return resumed;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to resume recurring task";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    return {
        recurringTasks,
        loading,
        error,
        getRecurringTasksByProject,
        getRecurringTaskById,
        upsertRecurringTask,
        removeRecurringTask,
        loadRecurringTasks,
        createRecurringTask,
        updateRecurringTask,
        deleteRecurringTask,
        pauseRecurringTask,
        resumeRecurringTask
    };
});
