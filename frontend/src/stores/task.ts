import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Task } from '@/models/task';
import { taskService, type TaskCreateInput } from '@/services/taskService';

export const useTaskStore = defineStore('task', () => {
    const tasks = ref<Task[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    // Computed: Get tasks by section
    const getTasksBySection = computed(() => {
        return (sectionId: string) =>
            tasks.value.filter(task => task.section_id === sectionId);
    });

    // Computed: Get tasks by project
    const getTasksByProject = computed(() => {
        return (projectId: string) =>
            tasks.value.filter(task => task.project_id === projectId);
    });

    async function fetchTasksByProject(projectId: string) {
        loading.value = true;
        error.value = null;
        try {
            const allTasks = await taskService.getTasks(projectId);
            tasks.value = allTasks.filter(task => task.project_id === projectId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to fetch tasks';
            console.error('Error fetching tasks:', err);
            tasks.value = [];
        } finally {
            loading.value = false;
        }
    }

    async function createTask(taskData: TaskCreateInput) {
        loading.value = true;
        error.value = null;
        try {
            const newTask = await taskService.createTask(taskData);
            tasks.value.push(newTask);
            return newTask;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to create task';
            console.error('Error creating task:', err);
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateTask(taskId: string, updates: Partial<Task>) {
        loading.value = true;
        error.value = null;
        try {
            const updatedTask = await taskService.updateTask(taskId, updates);
            const index = tasks.value.findIndex(t => t.id === taskId);
            if (index !== -1) {
                tasks.value[index] = updatedTask;
            }
            return updatedTask;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to update task';
            console.error('Error updating task:', err);
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteTask(taskId: string) {
        loading.value = true;
        error.value = null;
        try {
            await taskService.deleteTask(taskId);
            tasks.value = tasks.value.filter(t => t.id !== taskId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to delete task';
            console.error('Error deleting task:', err);
            throw err;
        } finally {
            loading.value = false;
        }
    }

    return {
        tasks,
        loading,
        error,
        getTasksBySection,
        getTasksByProject,
        fetchTasksByProject,
        createTask,
        updateTask,
        deleteTask,
    };
});
