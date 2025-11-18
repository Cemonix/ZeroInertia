import { describe, it, expect } from 'vitest';
import { fireEvent, waitFor } from '@testing-library/vue';
import { renderWithProviders, flushPromises } from '@/tests/utils/test-utils';
import TodayBoard from '@/components/today/TodayBoard.vue';

describe('TodayBoard Integration', () => {
    it('renders list view by default and hides drag handles', async () => {
        window.localStorage.clear();
        const { container } = renderWithProviders(TodayBoard);

        await flushPromises();

        // Wait for list view to render
        await waitFor(() => {
            expect(container.querySelector('.list-view')).toBeTruthy();
        });

        // Verify drag handles are not shown in TodayBoard
        const dragHandles = container.querySelectorAll('.task-drag-handle');
        expect(dragHandles.length).toBe(0);

        // Verify the view toggle buttons exist
        expect(container.querySelector('.view-toggle')).toBeTruthy();
    });

    it('toggles between list and calendar views and persists view mode', async () => {
        window.localStorage.clear();
        const { getByText, container } = renderWithProviders(TodayBoard);

        await flushPromises();

        // Starts in list view (after data load)
        await waitFor(() => {
            expect(container.querySelector('.list-view')).toBeTruthy();
        });

        const calendarButton = getByText('Calendar');
        await fireEvent.click(calendarButton);

        await waitFor(() => {
            expect(container.querySelector('.today-calendar-container')).toBeTruthy();
        });

        // View mode should be saved to localStorage
        const stored = window.localStorage.getItem('today-view-mode');
        expect(stored === 'calendar').toBe(true);

        const listButton = getByText('List');
        await fireEvent.click(listButton);

        await waitFor(() => {
            expect(container.querySelector('.list-view')).toBeTruthy();
        });
    });
});
