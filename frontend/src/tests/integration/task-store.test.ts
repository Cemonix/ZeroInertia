import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTaskStore } from '@/stores/task';
import { mockTasks } from '../mocks/handlers';

describe('Task Store Integration', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        mockTasks.length = 0;
        mockTasks.push(
            {
                id: 'task-1',
                title: 'Test Task 1',
                description: 'Description for test task 1',
                completed: false,
                archived: false,
                snooze_count: 0,
                project_id: 'project-1',
                section_id: 'section-1',
                order_index: 0,
                priority_id: 'priority-medium',
                due_datetime: null,
                duration_minutes: null,
                reminder_minutes: null,
                recurrence_interval: null,
                recurrence_unit: null,
                recurrence_days: null,
                labels: [],
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z',
                archived_at: null,
            },
            {
                id: 'task-2',
                title: 'Test Task 2',
                description: 'Description for test task 2',
                completed: true,
                archived: false,
                snooze_count: 0,
                project_id: 'project-1',
                section_id: 'section-1',
                order_index: 1,
                priority_id: 'priority-high',
                due_datetime: '2025-12-31T12:00:00Z',
                duration_minutes: 60,
                reminder_minutes: 15,
                recurrence_interval: null,
                recurrence_unit: null,
                recurrence_days: null,
                labels: [],
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z',
                archived_at: null,
            }
        );
    });

    it('should load tasks for a project successfully', async () => {
        const taskStore = useTaskStore();

        await taskStore.loadTasksForProject('project-1');

        expect(taskStore.tasks).toHaveLength(2);
        expect(taskStore.tasks[0].title).toBe('Test Task 1');
        expect(taskStore.tasks[1].title).toBe('Test Task 2');
        expect(taskStore.loading).toBe(false);
        expect(taskStore.error).toBe(null);
    });

    it('should filter tasks by section', async () => {
        const taskStore = useTaskStore();
        await taskStore.loadTasksForProject('project-1');

        const sectionTasks = taskStore.getTasksBySection('section-1');

        expect(sectionTasks).toHaveLength(2);
        expect(sectionTasks[0].section_id).toBe('section-1');
        expect(sectionTasks[1].section_id).toBe('section-1');
    });

    it('should filter tasks by project', async () => {
        const taskStore = useTaskStore();
        await taskStore.loadTasksForProject('project-1');

        const projectTasks = taskStore.getTasksByProject('project-1');

        expect(projectTasks).toHaveLength(2);
        expect(projectTasks[0].project_id).toBe('project-1');
    });

    it('should create a new task', async () => {
        const taskStore = useTaskStore();

        const newTaskData = {
            title: 'New Integration Test Task',
            description: 'Created from integration test',
            project_id: 'project-1',
            section_id: 'section-1',
            priority_id: 'priority-low',
            due_datetime: null,
        };

        const createdTask = await taskStore.createTask(newTaskData);

        expect(createdTask).toBeDefined();
        expect(createdTask?.title).toBe('New Integration Test Task');
        expect(createdTask?.description).toBe('Created from integration test');
        expect(taskStore.tasks).toContainEqual(
            expect.objectContaining({
                title: 'New Integration Test Task',
            })
        );
    });

    it('should update an existing task', async () => {
        const taskStore = useTaskStore();
        await taskStore.loadTasksForProject('project-1');

        const taskToUpdate = taskStore.tasks[0];
        const updatedData = {
            title: 'Updated Task Title',
            completed: true,
        };

        await taskStore.updateTask(taskToUpdate.id, updatedData);

        const updatedTask = taskStore.getTaskById(taskToUpdate.id);
        expect(updatedTask?.title).toBe('Updated Task Title');
        expect(updatedTask?.completed).toBe(true);
    });

    it('should delete a task', async () => {
        const taskStore = useTaskStore();
        await taskStore.loadTasksForProject('project-1');

        const initialTaskCount = taskStore.tasks.length;
        const taskToDelete = taskStore.tasks[0];

        await taskStore.deleteTask(taskToDelete.id);

        expect(taskStore.tasks).toHaveLength(initialTaskCount - 1);
        expect(taskStore.getTaskById(taskToDelete.id)).toBeNull();
    });

    it('should toggle task completion', async () => {
        const taskStore = useTaskStore();
        await taskStore.loadTasksForProject('project-1');

        const task = taskStore.tasks[0];
        const initialCompletedState = task.completed;

        await taskStore.toggleTaskComplete(task.id);

        const updatedTask = taskStore.getTaskById(task.id);
        expect(updatedTask?.completed).toBe(!initialCompletedState);
    });

    it('should set loading state during load', async () => {
        const taskStore = useTaskStore();

        const loadPromise = taskStore.loadTasksForProject('project-1');
        expect(taskStore.loading).toBe(true);

        await loadPromise;
        expect(taskStore.loading).toBe(false);
    });

    it('should get task by id', async () => {
        const taskStore = useTaskStore();
        await taskStore.loadTasksForProject('project-1');

        const task = taskStore.getTaskById('task-1');

        expect(task).toBeDefined();
        expect(task?.id).toBe('task-1');
        expect(task?.title).toBe('Test Task 1');
    });

    it('should return null for non-existent task id', async () => {
        const taskStore = useTaskStore();
        await taskStore.loadTasksForProject('project-1');

        const task = taskStore.getTaskById('non-existent-id');

        expect(task).toBeNull();
    });
});
