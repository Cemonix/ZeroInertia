import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Task, TaskCreateInput, TaskUpdateInput, TaskReorderItem } from '@/models/task';
import { taskService } from '@/services/taskService';
import { playTaskCompletedSound } from '@/core/sound';
import type { PaginationParams } from '@/models/pagination';

export const useTaskStore = defineStore('task', () => {
    const tasks = ref<Task[]>([]);
    const currentTask = ref<Task | null>(null);
    const currentSectionId = ref<string | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const taskModalVisible = ref(false);

    const getTasksBySection = computed(() => {
        return (sectionId: string) =>
            tasks.value
                .filter(task => task.section_id === sectionId)
                .sort((a, b) => a.order_index - b.order_index);
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

        const wasRecurring = !!task.recurrence_type;
        const projectId = task.project_id;

        try {
            const updatedTask = await taskService.updateTask(taskId, {
                completed: !task.completed,
            });

            // If task was recurring and is now completed, it was archived and a new one was created
            // We need to reload the project's tasks to get the new task and remove the archived one
            if (wasRecurring && !task.completed && updatedTask.completed && updatedTask.archived) {
                // Remove the archived task from the list
                tasks.value = tasks.value.filter(t => t.id !== taskId);
                // Reload tasks for this project to get the new recurring task instance
                await loadTasksForProject(projectId);
            } else {
                // Normal task completion - just update in place
                const index = tasks.value.findIndex(t => t.id === taskId);
                if (index !== -1) {
                    tasks.value[index] = updatedTask;
                }
            }

            if (!task.completed && updatedTask.completed) {
                await playTaskCompletedSound();
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to toggle task completion";
        }
    }

    async function loadTasksForProject(projectId: string, pagination: PaginationParams = { page: 1, page_size: 500 }) {
        loading.value = true;
        error.value = null;
        try {
            const resp = await taskService.getTasks(projectId, pagination);
            const projectTasks = resp.items;
            // Merge project tasks into the store without dropping tasks from other projects
            const others = tasks.value.filter(t => t.project_id !== projectId);
            tasks.value = [...others, ...projectTasks];
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load tasks';
            // Don't clear all tasks on failure; keep existing cache to avoid UI flicker
        } finally {
            loading.value = false;
        }
    }

    async function loadAllTasks(pagination: PaginationParams = { page: 1, page_size: 500 }) {
        loading.value = true;
        error.value = null;
        try {
            const resp = await taskService.getTasks(undefined, pagination);
            tasks.value = resp.items;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load tasks';
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
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateTask(taskId: string, updates: TaskUpdateInput) {
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
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function reorderTasks(sectionId: string, reorderedTaskIds: string[]) {
        // Optimistically update the local state
        const tasksInSection = reorderedTaskIds.map(id =>
            tasks.value.find(t => t.id === id)
        ).filter(Boolean) as Task[];

        // Update order_index and section_id for each task
        tasksInSection.forEach((task, index) => {
            const taskIndex = tasks.value.findIndex(t => t.id === task.id);
            if (taskIndex !== -1) {
                tasks.value[taskIndex] = {
                    ...task,
                    order_index: index,
                    section_id: sectionId  // Update section_id in case task was moved
                };
            }
        });

        // Prepare the reorder payload - use the task's current section_id (which may have been updated)
        const reorderPayload: TaskReorderItem[] = tasksInSection.map((task, index) => ({
            id: task.id,
            section_id: task.section_id,  // Use task's section_id which reflects any cross-section moves
            order_index: index,
        }));

        try {
            await taskService.reorderTasks(reorderPayload);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to reorder tasks';
            // Reload tasks to restore correct order on failure
            const projectId = tasksInSection[0]?.project_id;
            if (projectId) {
                await loadTasksForProject(projectId);
            }
            throw err;
        }
    }

    async function duplicateTask(taskId: string) {
        const task = getTaskById.value(taskId);
        if (!task) {
            return null;
        }

        const labelIds = task.label_ids ?? task.labels?.map(label => label.id) ?? null;

        const duplicatePayload: TaskCreateInput = {
            title: task.title,
            description: task.description,
            project_id: task.project_id,
            section_id: task.section_id,
            priority_id: task.priority_id,
            due_datetime: task.due_datetime,
            recurrence_type: task.recurrence_type,
            recurrence_days: task.recurrence_days,
            ...(labelIds !== null ? { label_ids: labelIds } : {}),
        };

        try {
            return await createTask(duplicatePayload);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to duplicate task';
            throw err;
        }
    }

    async function snoozeTask(taskId: string) {
        error.value = null;
        try {
            const updatedTask = await taskService.snoozeTask(taskId);
            const index = tasks.value.findIndex(t => t.id === taskId);
            if (index !== -1) {
                tasks.value[index] = updatedTask;
            }
            return updatedTask;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to snooze task';
            throw err;
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
        loadAllTasks,
        createTask,
        updateTask,
        deleteTask,
        reorderTasks,
        duplicateTask,
        snoozeTask,
    };
});
