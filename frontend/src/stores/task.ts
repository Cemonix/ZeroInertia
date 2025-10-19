import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Task } from '@/models/task';
import { taskService, type TaskCreateInput } from '@/services/taskService';

export const useTaskStore = defineStore('task', () => {
    const tasks = ref<Task[]>([]);
    const currentTask = ref<Task | null>(null);
    const currentSectionId = ref<string | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const taskModalVisible = ref(false);

    const getTasksBySection = computed(() => {
        return (sectionId: string) =>
            tasks.value.filter(task => task.section_id === sectionId);
    });

    const getTasksByProject = computed(() => {
        return (projectId: string) =>
            tasks.value.filter(task => task.project_id === projectId);
    });

    const getTaskById = computed(() => {
        return (taskId: string) => tasks.value.find(task => task.id === taskId) || null;
    });

    const getCurrentTask = computed(() => currentTask.value);

    const setCurrentTask = (task: Task | null) => {
        currentTask.value = task;
        // If setting a task, also set its section
        if (task) {
            currentSectionId.value = task.section_id;
        }
    };

    const setCurrentSectionId = (sectionId: string | null) => {
        currentSectionId.value = sectionId;
    };

    const setTaskModalVisible = (visible: boolean) => {
        taskModalVisible.value = visible;
        // Clear current task and section when closing
        if (!visible) {
            currentTask.value = null;
            currentSectionId.value = null;
        }
    };

    const openTaskModal = (sectionId: string, task: Task | null = null) => {
        currentSectionId.value = sectionId;
        currentTask.value = task;
        taskModalVisible.value = true;
    };

    const isTaskModalVisible = computed(() => taskModalVisible.value);

    const toggleTaskComplete = async (taskId: string) => {
        const task = getTaskById.value(taskId);
        if (!task) return;

        try {
            const updatedTask = await taskService.updateTask(taskId, {
                completed: !task.completed,
            });
            const index = tasks.value.findIndex(t => t.id === taskId);
            if (index !== -1) {
                tasks.value[index] = updatedTask;
            }
        } catch (err) {
            console.error('Error toggling task completion:', err);
        }
    }

    async function loadTasksForProject(projectId: string) {
        loading.value = true;
        error.value = null;
        try {
            tasks.value = await taskService.getTasks(projectId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load tasks';
            console.error('Error loading tasks:', err);
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
        currentSectionId,
        getTasksBySection,
        getTasksByProject,
        getTaskById,
        getCurrentTask,
        isTaskModalVisible,
        setCurrentTask,
        setCurrentSectionId,
        setTaskModalVisible,
        openTaskModal,
        toggleTaskComplete,
        loadTasksForProject,
        createTask,
        updateTask,
        deleteTask,
    };
});
