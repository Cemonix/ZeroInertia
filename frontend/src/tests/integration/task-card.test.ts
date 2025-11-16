import { describe, it, expect, vi } from 'vitest';
import { fireEvent } from '@testing-library/vue';
import { renderWithProviders, flushPromises } from '@/tests/utils/test-utils';
import TaskCard from '@/components/tasks/TaskCard.vue';
import type { Task } from '@/models/task';
import { useTaskStore } from '@/stores/task';
import { useChecklistStore } from '@/stores/checklist';

const baseTask: Task = {
    id: 'task-1',
    title: 'Test Task',
    description: 'Task description',
    completed: false,
    archived: false,
    snooze_count: 0,
    project_id: 'project-1',
    section_id: 'section-1',
    order_index: 0,
    priority_id: null,
    due_datetime: null,
    duration_minutes: null,
    reminder_minutes: null,
    recurrence_interval: null,
    recurrence_unit: null,
    recurrence_days: null,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    archived_at: null,
};

describe('TaskCard Integration', () => {
    it('renders task title and description', () => {
        const { getByText } = renderWithProviders(TaskCard, {
            props: {
                task: baseTask,
            },
        });

        expect(getByText('Test Task')).toBeTruthy();
        expect(getByText('Task description')).toBeTruthy();
    });

    it('calls openTaskModal when card (but not checkbox) is clicked', async () => {
        const { container } = renderWithProviders(TaskCard, {
            props: {
                task: baseTask,
            },
        });

        const taskStore = useTaskStore();
        const openSpy = vi.spyOn(taskStore, 'openTaskModal');

        const card = container.querySelector('.task-card') as HTMLElement;
        await fireEvent.click(card);

        expect(openSpy).toHaveBeenCalledTimes(1);
        expect(openSpy).toHaveBeenCalledWith(baseTask.section_id, baseTask);

        // Clicking checkbox should not open modal
        openSpy.mockClear();
        const checkboxWrapper = container.querySelector('.task-checkbox') as HTMLElement;
        await fireEvent.click(checkboxWrapper);

        expect(openSpy).not.toHaveBeenCalled();
    });

    it('toggles completion when checkbox is clicked', async () => {
        const { container } = renderWithProviders(TaskCard, {
            props: {
                task: baseTask,
            },
        });

        const taskStore = useTaskStore();
        const toggleSpy = vi.spyOn(taskStore, 'toggleTaskComplete').mockResolvedValue();

        const checkbox = container.querySelector('.task-checkbox input') as HTMLInputElement | null;
        if (checkbox) {
            await fireEvent.click(checkbox);
        } else {
            const checkboxWrapper = container.querySelector('.task-checkbox') as HTMLElement;
            await fireEvent.click(checkboxWrapper);
        }

        expect(toggleSpy).toHaveBeenCalledTimes(1);
        expect(toggleSpy).toHaveBeenCalledWith(baseTask.id);
    });

    it('shows checklist icon when task has checklists', async () => {
        const { container } = renderWithProviders(TaskCard, {
            props: {
                task: baseTask,
            },
        });

        const checklistStore = useChecklistStore();
        checklistStore.checklists = [
            {
                id: 'checklist-1',
                task_id: baseTask.id,
                title: 'Checklist',
                order_index: 0,
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z',
                items: [],
            },
        ];

        await flushPromises();

        const icon = container.querySelector('.task-checklist-icon');
        expect(icon).toBeTruthy();
    });

    it('shows reminder label when reminder_minutes is set', () => {
        const taskWithReminder: Task = {
            ...baseTask,
            reminder_minutes: 30,
        };

        const { container } = renderWithProviders(TaskCard, {
            props: {
                task: taskWithReminder,
            },
        });

        const reminder = container.querySelector('.task-reminder');
        expect(reminder).toBeTruthy();
        expect(reminder?.textContent).toContain('30m before');
    });
});

