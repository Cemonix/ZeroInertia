import { describe, it, expect } from 'vitest';
import { renderWithProviders } from '@/tests/utils/test-utils';
import { fireEvent } from '@testing-library/vue';
import RecurrencePicker from '@/components/pickers/RecurrencePicker.vue';

describe('RecurrencePicker Integration', () => {
    it('should render with default props', () => {
        const { container } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: null,
                unit: null,
                days: null,
            },
        });

        expect(container.querySelector('.recurrence-picker')).toBeTruthy();
    });

    it('should display weekday selector when unit is weeks', () => {
        const { container } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 1,
                unit: 'weeks',
                days: null,
            },
        });

        const weekdayButtons = container.querySelectorAll('.weekday-chip');
        expect(weekdayButtons.length).toBe(7);
    });

    it('should emit update:days when weekday is clicked', async () => {
        const { container, emitted } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 1,
                unit: 'weeks',
                days: null,
            },
        });

        const weekdayButtons = container.querySelectorAll('.weekday-chip');
        const mondayButton = weekdayButtons[1]; // Monday in display order

        await fireEvent.click(mondayButton);

        expect(emitted()['update:days']).toBeTruthy();
        // Should emit Python convention (0 = Monday)
        expect(emitted()['update:days'][0]).toEqual([[0]]);
    });

    it('should toggle weekday active state', async () => {
        const { container } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 1,
                unit: 'weeks',
                days: null,
            },
        });

        const weekdayButtons = container.querySelectorAll('.weekday-chip');
        const mondayButton = weekdayButtons[1];

        // Initially not active
        expect(mondayButton.classList.contains('active')).toBe(false);

        // Click to activate
        await fireEvent.click(mondayButton);
        expect(mondayButton.classList.contains('active')).toBe(true);

        // Click again to deactivate
        await fireEvent.click(mondayButton);
        expect(mondayButton.classList.contains('active')).toBe(false);
    });

    it('should not cause infinite loop when clicking multiple weekdays', async () => {
        const { container, emitted } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 1,
                unit: 'weeks',
                days: null,
            },
        });

        const weekdayButtons = container.querySelectorAll('.weekday-chip');

        // Click Monday, Wednesday, Friday
        await fireEvent.click(weekdayButtons[1]); // Monday
        await fireEvent.click(weekdayButtons[3]); // Wednesday
        await fireEvent.click(weekdayButtons[5]); // Friday

        const daysEmitted = emitted()['update:days'] as unknown[][];
        expect(daysEmitted).toBeTruthy();
        expect(daysEmitted.length).toBe(3);

        // Final emit should have all three days in Python convention
        expect(daysEmitted[2][0]).toEqual([0, 2, 4]); // Mon, Wed, Fri
    });

    it('should emit close when done button is clicked', async () => {
        const { getByText, emitted } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 1,
                unit: 'days',
                days: null,
            },
        });

        const doneButton = getByText('Done');
        await fireEvent.click(doneButton);

        expect(emitted()['close']).toBeTruthy();
    });

    it('should clear all recurrence values when clear button is clicked', async () => {
        const { getByText, emitted } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 2,
                unit: 'weeks',
                days: [0, 2],
            },
        });

        const clearButton = getByText('Clear');
        await fireEvent.click(clearButton);

        const intervalEmits = emitted()['update:interval'];
        const unitEmits = emitted()['update:unit'];
        const daysEmits = emitted()['update:days'];

        expect(intervalEmits[intervalEmits.length - 1]).toEqual([null]);
        expect(unitEmits[unitEmits.length - 1]).toEqual([null]);
        expect(daysEmits[daysEmits.length - 1]).toEqual([null]);
    });

    it('should disable weekday buttons when no recurrence is set', () => {
        const { container } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: null,
                unit: null,
                days: null,
            },
        });

        const weekdayButtons = container.querySelectorAll('.weekday-chip');
        weekdayButtons.forEach(btn => {
            expect(btn.hasAttribute('disabled')).toBe(true);
        });
    });

    it('should enable weekday buttons when recurrence is set', () => {
        const { container } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 1,
                unit: 'weeks',
                days: null,
            },
        });

        const weekdayButtons = container.querySelectorAll('.weekday-chip');
        weekdayButtons.forEach(btn => {
            expect(btn.hasAttribute('disabled')).toBe(false);
        });
    });

    it('should show selected days as active', () => {
        const { container } = renderWithProviders(RecurrencePicker, {
            props: {
                interval: 1,
                unit: 'weeks',
                days: [0, 2, 4], // Mon, Wed, Fri in Python convention
            },
        });

        const weekdayButtons = container.querySelectorAll('.weekday-chip');
        // Mon, Wed, Fri should be active (indices 1, 3, 5 in display order)
        expect(weekdayButtons[1].classList.contains('active')).toBe(true);
        expect(weekdayButtons[3].classList.contains('active')).toBe(true);
        expect(weekdayButtons[5].classList.contains('active')).toBe(true);

        // Others should not be active
        expect(weekdayButtons[0].classList.contains('active')).toBe(false);
        expect(weekdayButtons[2].classList.contains('active')).toBe(false);
    });
});
