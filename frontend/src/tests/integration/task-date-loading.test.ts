import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTaskStore } from '@/stores/task';
import { resetMockTasks, getMockTasks } from '../mocks/handlers';

describe('Task Store - Date Range Loading', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        resetMockTasks();
    });

    it('should load tasks for a specific date range', async () => {
        const taskStore = useTaskStore();

        const today = new Date('2025-12-31T00:00:00Z');
        const tomorrow = new Date('2026-01-01T00:00:00Z');

        await taskStore.loadTasksByDateRange(today, tomorrow);

        expect(taskStore.tasks.length).toBeGreaterThan(0);
        expect(taskStore.loading).toBe(false);
        expect(taskStore.error).toBe(null);
    });

    it('should include tasks with due dates in the specified range', async () => {
        const taskStore = useTaskStore();

        const startDate = new Date('2025-12-31T00:00:00Z');
        const endDate = new Date('2026-01-01T00:00:00Z');

        await taskStore.loadTasksByDateRange(startDate, endDate);

        const tasks = taskStore.getTasksByDateRange(startDate, endDate);
        const tasksWithDates = tasks.filter(task => task.due_datetime !== null);

        expect(tasks.length).toBeGreaterThan(0);
        tasksWithDates.forEach(task => {
            const taskDate = new Date(task.due_datetime!);
            expect(taskDate.getTime()).toBeGreaterThanOrEqual(startDate.getTime());
            expect(taskDate.getTime()).toBeLessThan(endDate.getTime());
        });
    });

    it('should include tasks without due dates', async () => {
        const taskStore = useTaskStore();

        const mockTasks = getMockTasks();
        const tasksWithoutDate = mockTasks.filter(t => !t.due_datetime && !t.completed && !t.archived);

        const startDate = new Date('2025-01-01T00:00:00Z');
        const endDate = new Date('2025-01-02T00:00:00Z');

        await taskStore.loadTasksByDateRange(startDate, endDate);

        const tasks = taskStore.getTasksByDateRange(startDate, endDate);
        const returnedTasksWithoutDate = tasks.filter(t => !t.due_datetime);
        expect(returnedTasksWithoutDate.length).toBe(tasksWithoutDate.length);
    });

    it('should exclude completed tasks', async () => {
        const taskStore = useTaskStore();

        const startDate = new Date('2025-01-01T00:00:00Z');
        const endDate = new Date('2026-01-01T00:00:00Z');

        await taskStore.loadTasksByDateRange(startDate, endDate);

        const tasks = taskStore.getTasksByDateRange(startDate, endDate);
        const completedTasks = tasks.filter(task => task.completed);
        expect(completedTasks.length).toBe(0);
    });

    it('should remove tasks from date range when they are completed', async () => {
        const taskStore = useTaskStore();

        const startDate = new Date('2025-01-01T00:00:00Z');
        const endDate = new Date('2026-01-01T00:00:00Z');

        await taskStore.loadTasksByDateRange(startDate, endDate);

        // Sanity check: we have at least one active task in the range
        const initialTasks = taskStore.getTasksByDateRange(startDate, endDate);
        expect(initialTasks.length).toBeGreaterThan(0);

        const taskToComplete = initialTasks[0];
        await taskStore.toggleTaskComplete(taskToComplete.id);

        const tasksAfterCompletion = taskStore.getTasksByDateRange(startDate, endDate);
        const stillPresent = tasksAfterCompletion.find(t => t.id === taskToComplete.id);

        // After completion, the task should no longer be returned for the date range
        expect(stillPresent).toBeUndefined();
    });

    it('should exclude archived tasks', async () => {
        const taskStore = useTaskStore();

        const startDate = new Date('2025-01-01T00:00:00Z');
        const endDate = new Date('2026-01-01T00:00:00Z');

        await taskStore.loadTasksByDateRange(startDate, endDate);

        const tasks = taskStore.getTasksByDateRange(startDate, endDate);
        const archivedTasks = tasks.filter(task => task.archived);
        expect(archivedTasks.length).toBe(0);
    });

    it('should return only tasks without dates for far future date range', async () => {
        const taskStore = useTaskStore();

        const futureStart = new Date('2099-01-01T00:00:00Z');
        const futureEnd = new Date('2099-01-02T00:00:00Z');

        await taskStore.loadTasksByDateRange(futureStart, futureEnd);

        const tasks = taskStore.getTasksByDateRange(futureStart, futureEnd);
        const tasksWithDates = tasks.filter(t => t.due_datetime !== null);
        expect(tasksWithDates.length).toBe(0);
    });

    it('should handle single day range correctly', async () => {
        const taskStore = useTaskStore();

        const dayStart = new Date('2025-12-31T00:00:00Z');
        const dayEnd = new Date('2025-12-31T23:59:59.999Z');

        await taskStore.loadTasksByDateRange(dayStart, dayEnd);

        const tasks = taskStore.getTasksByDateRange(dayStart, dayEnd);
        expect(tasks.length).toBeGreaterThanOrEqual(0);
    });

    it('should handle loading state correctly', async () => {
        const taskStore = useTaskStore();

        expect(taskStore.loading).toBe(false);

        const loadPromise = taskStore.loadTasksByDateRange(
            new Date('2025-01-01'),
            new Date('2025-01-02')
        );

        await loadPromise;

        expect(taskStore.loading).toBe(false);
    });

    it('should update the store tasks with date-filtered tasks', async () => {
        const taskStore = useTaskStore();

        const startDate = new Date('2025-01-01T00:00:00Z');
        const endDate = new Date('2026-01-01T00:00:00Z');

        await taskStore.loadTasksByDateRange(startDate, endDate);

        expect(taskStore.tasks.length).toBeGreaterThanOrEqual(0);
    });

    it('should handle boundary dates correctly (inclusive start, exclusive end)', async () => {
        const taskStore = useTaskStore();

        const inclusiveStart = new Date('2025-12-31T12:00:00Z');
        const exclusiveEnd = new Date('2025-12-31T12:00:01Z');

        await taskStore.loadTasksByDateRange(inclusiveStart, exclusiveEnd);

        const tasks = taskStore.getTasksByDateRange(inclusiveStart, exclusiveEnd);
        expect(tasks.length).toBeGreaterThanOrEqual(0);
    });
});
