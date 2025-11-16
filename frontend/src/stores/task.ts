import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Task, TaskCreateInput, TaskUpdateInput, TaskReorderItem } from '@/models/task';
import { taskService } from '@/services/taskService';
import { playTaskCompletedSound } from '@/core/sound';
import type { PaginationParams } from '@/models/pagination';
import { useStreakStore } from './streak';

export const useTaskStore = defineStore('task', () => {
    const tasks = ref<Task[]>([]);
    const currentTask = ref<Task | null>(null);
    const currentSectionId = ref<string | null>(null);
    const initialTaskValues = ref<Partial<TaskCreateInput> | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const taskModalVisible = ref(false);
    const draggedTaskId = ref<string | null>(null);

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
        // Clear current task, section, and initial values when closing
        if (!visible) {
            currentTask.value = null;
            currentSectionId.value = null;
            initialTaskValues.value = null;
        }
    };

    const openTaskModal = (sectionId: string | null, task: Task | null = null, initialValues: Partial<TaskCreateInput> | null = null) => {
        currentSectionId.value = sectionId;
        currentTask.value = task;
        initialTaskValues.value = initialValues;
        taskModalVisible.value = true;
    };

    const isTaskModalVisible = computed(() => taskModalVisible.value);

    const startDraggingTask = (taskId: string) => {
        draggedTaskId.value = taskId;
    };

    const stopDraggingTask = () => {
        draggedTaskId.value = null;
    };

    const toggleTaskComplete = async (taskId: string) => {
        const task = getTaskById.value(taskId);
        if (!task) return;

        const wasRecurring = !!(task.recurrence_interval && task.recurrence_unit);
        const projectId = task.project_id;
        const wasCompleted = task.completed;

        // Play sound immediately for better UX
        if (!wasCompleted) {
            await playTaskCompletedSound();
        }

        // Optimistically update the UI immediately without setting loading state
        const index = tasks.value.findIndex(t => t.id === taskId);
        if (index !== -1) {
            tasks.value[index] = {
                ...task,
                completed: !task.completed,
            };
        }

        try {
            const updatedTask = await taskService.updateTask(taskId, {
                completed: !wasCompleted,
            });

            // If task was recurring and is now completed, it was archived and a new one was created
            // We need to reload the project's tasks to get the new task and remove the archived one
            if (wasRecurring && !wasCompleted && updatedTask.completed && updatedTask.archived) {
                // Remove the archived task from the list
                tasks.value = tasks.value.filter(t => t.id !== taskId);
                // Reload tasks for this project to get the new recurring task instance
                // Use a silent reload that doesn't trigger loading state
                const currentLoading = loading.value;
                loading.value = false;
                await loadTasksForProject(projectId);
                loading.value = currentLoading;
            } else {
                // Skip update if only completion status changed (already optimistically updated)
                // This prevents double-rendering flicker in production builds
                const currentIndex = tasks.value.findIndex(t => t.id === taskId);
                if (currentIndex !== -1) {
                    // Check if there are meaningful changes beyond what we already optimistically updated
                    const hasSignificantChanges =
                        updatedTask.archived !== tasks.value[currentIndex].archived ||
                        updatedTask.snooze_count !== tasks.value[currentIndex].snooze_count ||
                        updatedTask.title !== tasks.value[currentIndex].title ||
                        updatedTask.description !== tasks.value[currentIndex].description;

                    if (hasSignificantChanges) {
                        tasks.value[currentIndex] = updatedTask;
                    }
                    // If no significant changes, keep the optimistic update (no re-render needed)
                }
            }

            // Refresh streak only when completing the first task of the day
            if (!wasCompleted) {
                const streakStore = useStreakStore();
                if (streakStore.hasLoadedStreak) {
                    const today = new Date().toISOString().split('T')[0];
                    const lastActivity = streakStore.lastActivityDate;

                    // Only reload if this is the first task completed today
                    if (!lastActivity || lastActivity !== today) {
                        await streakStore.loadStreak();

                        // Also refresh calendar if it's been loaded
                        if (streakStore.calendarStartDate && streakStore.calendarEndDate) {
                            await streakStore.loadCalendar(
                                streakStore.calendarStartDate,
                                streakStore.calendarEndDate
                            );
                        }
                    }
                }
            }
        } catch (err) {
            // Revert the optimistic update on error
            const currentIndex = tasks.value.findIndex(t => t.id === taskId);
            if (currentIndex !== -1) {
                tasks.value[currentIndex] = task;
            }
            error.value = err instanceof Error ? err.message : "Failed to toggle task completion";
            throw err;
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

    async function loadTasksByDateRange(dateFrom: Date, dateTo: Date): Promise<Task[]> {
        loading.value = true;
        error.value = null;
        try {
            const fetchedTasks = await taskService.getTasksByDateRange(dateFrom, dateTo);
            return fetchedTasks;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load tasks by date';
            return [];
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

    async function moveTaskToSection(taskId: string, targetProjectId: string, targetSectionId: string) {
        const task = getTaskById.value(taskId);
        if (!task) {
            return;
        }

        // Optimistic local update
        const existingIndex = tasks.value.findIndex(t => t.id === taskId);
        const originalTask = existingIndex !== -1 ? { ...tasks.value[existingIndex] } : null;

        const targetTasks = tasks.value
            .filter(t => t.project_id === targetProjectId && t.section_id === targetSectionId)
            .sort((a, b) => a.order_index - b.order_index);
        const nextOrderIndex = targetTasks.length > 0
            ? targetTasks[targetTasks.length - 1].order_index + 1
            : 0;

        if (existingIndex !== -1) {
            tasks.value[existingIndex] = {
                ...task,
                project_id: targetProjectId,
                section_id: targetSectionId,
                order_index: nextOrderIndex,
            };
        }

        try {
            const updatedTask = await taskService.updateTask(taskId, {
                project_id: targetProjectId,
                section_id: targetSectionId,
            });
            const idx = tasks.value.findIndex(t => t.id === taskId);
            if (idx !== -1) {
                tasks.value[idx] = updatedTask;
            }
        } catch (err) {
            if (existingIndex !== -1 && originalTask) {
                tasks.value[existingIndex] = originalTask;
            }
            error.value = err instanceof Error ? err.message : "Failed to move task";
            throw err;
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

        // Prepare the reorder payload - use the task's current section_id and project_id (which may have been updated)
        const reorderPayload: TaskReorderItem[] = tasksInSection.map((task, index) => ({
            id: task.id,
            project_id: task.project_id,  // Include project_id for cross-project moves
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
            duration_minutes: task.duration_minutes ?? null,
            recurrence_interval: task.recurrence_interval,
            recurrence_unit: task.recurrence_unit,
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

    function clearProjectTasks(projectId: string) {
        tasks.value = tasks.value.filter(t => t.project_id !== projectId);
    }

    function clearTasks() {
        tasks.value = [];
    }

    return {
        tasks,
        loading,
        error,
        currentSectionId,
        initialTaskValues,
        draggedTaskId,
        getTasksBySection,
        getTasksByProject,
        getTaskById,
        getCurrentTask,
        isTaskModalVisible,
        startDraggingTask,
        stopDraggingTask,
        setCurrentTask,
        setCurrentSectionId,
        setTaskModalVisible,
        openTaskModal,
        toggleTaskComplete,
        loadTasksForProject,
        loadAllTasks,
        loadTasksByDateRange,
        createTask,
        updateTask,
        deleteTask,
        reorderTasks,
        moveTaskToSection,
        duplicateTask,
        snoozeTask,
        clearProjectTasks,
        clearTasks,
    };
});
