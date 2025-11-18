import { describe, it, expect, vi } from 'vitest';
import { fireEvent } from '@testing-library/vue';
import { renderWithProviders, flushPromises } from '@/tests/utils/test-utils';
import BoardSection from '@/components/board/BoardSection.vue';
import type { Task } from '@/models/task';
import type { Section } from '@/models/section';
import { useTaskStore } from '@/stores/task';

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

const section: Section = {
    id: 'section-1',
    title: 'To Do',
    project_id: 'project-1',
    order_index: 0,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
};

describe('BoardSection Integration', () => {
    it('renders tasks for the section with drag handles', async () => {
        const { container } = renderWithProviders(BoardSection, {
            props: {
                projectId: 'project-1',
                section,
            },
        });

        const taskStore = useTaskStore();
        taskStore.tasks = [
            { ...baseTask, id: 'task-1', title: 'First task', order_index: 0 },
            { ...baseTask, id: 'task-2', title: 'Second task', order_index: 1 },
        ];

        await flushPromises();

        const cards = container.querySelectorAll('.task-card');
        const dragHandles = container.querySelectorAll('.task-drag-handle');

        expect(cards.length).toBe(2);
        expect(dragHandles.length).toBe(2);
    });

    it('shows "Show completed" toggle when section has completed tasks', async () => {
        const { getByText } = renderWithProviders(BoardSection, {
            props: {
                projectId: 'project-1',
                section,
            },
        });

        const taskStore = useTaskStore();
        taskStore.tasks = [
            { ...baseTask, id: 'task-1', completed: false },
            { ...baseTask, id: 'task-2', completed: true },
        ];

        await flushPromises();

        expect(getByText('Show completed')).toBeTruthy();
    });

    it('calls openTaskModal with section id when "Add task" is clicked', async () => {
        const { container } = renderWithProviders(BoardSection, {
            props: {
                projectId: 'project-1',
                section,
            },
        });

        const taskStore = useTaskStore();
        const openSpy = vi.spyOn(taskStore, 'openTaskModal');

        const addButton = container.querySelector('.add-task-button') as HTMLElement;
        expect(addButton).toBeTruthy();

        await fireEvent.click(addButton);

        expect(openSpy).toHaveBeenCalledTimes(1);
        expect(openSpy).toHaveBeenCalledWith(section.id);
    });
}
);

