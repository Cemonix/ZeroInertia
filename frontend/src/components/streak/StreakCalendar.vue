<template>
    <div class="streak-calendar">
        <div class="streak-calendar-header">
            <div>
                <h2 class="title">Activity</h2>
                <p class="subtitle">Completed tasks per day</p>
            </div>
            <div class="legend" aria-hidden="true">
                <span class="legend-label">Less</span>
                <div class="legend-squares">
                    <span class="legend-square level-0" />
                    <span class="legend-square level-1" />
                    <span class="legend-square level-2" />
                    <span class="legend-square level-3" />
                    <span class="legend-square level-4" />
                </div>
                <span class="legend-label">More</span>
            </div>
        </div>

        <div v-if="loading" class="calendar-loading">
            Loading streak calendar...
        </div>
        <div v-else class="calendar-wrapper" :class="{ 'calendar-empty': !weeks.length }">
            <div v-if="!weeks.length" class="calendar-empty-state">
                <p>No completed tasks yet. Start finishing tasks to build your streak!</p>
            </div>
            <div v-else class="calendar-layout">
                <div class="calendar-body">
                    <div class="weekday-labels" aria-hidden="true">
                        <span class="weekday-label">Mon</span>
                        <span class="weekday-label" />
                        <span class="weekday-label">Wed</span>
                        <span class="weekday-label" />
                        <span class="weekday-label">Fri</span>
                        <span class="weekday-label" />
                        <span class="weekday-label" />
                    </div>
                    <div class="calendar-scroll-container">
                        <div class="month-labels">
                            <span
                                v-for="month in monthLabels"
                                :key="month.label"
                                class="month-label"
                                :style="{
                                    '--week-count': month.weekCount,
                                    width: `calc(${month.weekCount} * (var(--cell-size) + 3px) - 3px)`
                                }"
                            >
                                {{ month.label }}
                            </span>
                        </div>
                        <div class="calendar-grid" role="grid" aria-label="Daily completed tasks">
                            <div
                                v-for="(week, weekIndex) in weeks"
                                :key="weekIndex"
                                class="calendar-week"
                                role="row"
                            >
                                <div
                                    v-for="(cell, dayIndex) in week"
                                    :key="cell ? cell.isoDate : `empty-${weekIndex}-${dayIndex}`"
                                    class="calendar-day"
                                    :class="[
                                        cell
                                            ? [
                                                  `level-${getLevel(cell.count)}`,
                                                  { 'is-today': cell.isToday },
                                              ]
                                            : 'is-empty'
                                    ]"
                                    :title="cell ? getTooltip(cell) : ''"
                                    role="gridcell"
                                    :aria-label="cell ? getTooltip(cell) : undefined"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { StreakCalendarDay } from "@/models/streak";

interface CalendarCell {
    date: Date;
    isoDate: string;
    count: number;
    isToday: boolean;
}

const ACTIVITY_LEVELS = {
    NONE: 0,
    LOW: 1,
    MEDIUM: 2,
    HIGH: 3,
    VERY_HIGH: 4,
} as const;

const LEVEL_THRESHOLDS = {
    [ACTIVITY_LEVELS.LOW]: 1,
    [ACTIVITY_LEVELS.MEDIUM]: 3,
    [ACTIVITY_LEVELS.HIGH]: 5,
    [ACTIVITY_LEVELS.VERY_HIGH]: 8,
} as const;

const props = defineProps<{
    days: StreakCalendarDay[];
    loading?: boolean;
    /**
     * Optional explicit range for the calendar.
     * When provided, the heatmap will cover the full range
     * regardless of how many days have activity.
     */
    startDate?: string;
    endDate?: string;
}>();

const loading = computed(() => props.loading ?? false);

const parseIsoDate = (iso: string): Date => {
    const [year, month, day] = iso.split("-").map(Number);
    return new Date(year, month - 1, day);
};

const toIsoDate = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
};

const weeks = computed<(CalendarCell | null)[][]>(() => {
    // If we don't have any data and no explicit range, show nothing
    if (!props.days.length && (!props.startDate || !props.endDate)) return [];

    const countMap = new Map<string, number>();
    for (const day of props.days) {
        countMap.set(day.date, day.completed_count);
    }

    // Determine calendar range:
    // - Prefer explicit start/end from props
    // - Fallback to first/last activity date
    let rangeStart: Date;
    let rangeEnd: Date;

    if (props.startDate && props.endDate) {
        rangeStart = parseIsoDate(props.startDate);
        rangeEnd = parseIsoDate(props.endDate);
    } else {
        const sorted = [...props.days].sort(
            (a, b) => parseIsoDate(a.date).getTime() - parseIsoDate(b.date).getTime(),
        );
        rangeStart = parseIsoDate(sorted[0].date);
        rangeEnd = parseIsoDate(sorted[sorted.length - 1].date);
    }

    const todayIso = toIsoDate(new Date());
    const result: (CalendarCell | null)[][] = [];
    let currentWeek: (CalendarCell | null)[] = [];

    // Monday as first day of week
    const jsDay = rangeStart.getDay();
    const startDayIndex = jsDay === 0 ? 6 : jsDay - 1;
    for (let i = 0; i < startDayIndex; i++) {
        currentWeek.push(null);
    }

    // Fill in actual days from rangeStart to rangeEnd inclusive.
    for (let d = new Date(rangeStart.getTime()); d <= rangeEnd; d.setDate(d.getDate() + 1)) {
        const iso = toIsoDate(d);
        const cell: CalendarCell = {
            date: new Date(d.getTime()),
            isoDate: iso,
            count: countMap.get(iso) ?? 0,
            isToday: iso === todayIso,
        };

        currentWeek.push(cell);

        if (currentWeek.length === 7) {
            result.push(currentWeek);
            currentWeek = [];
        }
    }

    // Pad the final week with empty cells so it always has 7 rows.
    if (currentWeek.length > 0) {
        while (currentWeek.length < 7) {
            currentWeek.push(null);
        }
        result.push(currentWeek);
    }

    return result;
});

const getLevel = (count: number): number => {
    if (!count) return ACTIVITY_LEVELS.NONE;
    if (count >= LEVEL_THRESHOLDS[ACTIVITY_LEVELS.VERY_HIGH]) return ACTIVITY_LEVELS.VERY_HIGH;
    if (count >= LEVEL_THRESHOLDS[ACTIVITY_LEVELS.HIGH]) return ACTIVITY_LEVELS.HIGH;
    if (count >= LEVEL_THRESHOLDS[ACTIVITY_LEVELS.MEDIUM]) return ACTIVITY_LEVELS.MEDIUM;
    return ACTIVITY_LEVELS.LOW;
};

const formatDate = (date: Date): string => {
    return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
    });
};

const getTooltip = (cell: CalendarCell): string => {
    const count = cell.count;
    const tasksLabel = count === 1 ? "task" : "tasks";
    return `${count} completed ${tasksLabel} on ${formatDate(cell.date)}`;
};

const monthLabels = computed(() => {
    if (!weeks.value.length) return [];

    const labels: Array<{ label: string; weekCount: number }> = [];
    let currentMonth = -1;
    let currentMonthWeekCount = 0;

    for (let i = 0; i < weeks.value.length; i++) {
        const week = weeks.value[i];
        if (!week || week.length === 0) continue;

        const firstDayCell = week.find((cell) => cell !== null);
        if (!firstDayCell) continue;

        const month = firstDayCell.date.getMonth();

        if (month !== currentMonth) {
            if (currentMonthWeekCount > 0) {
                const firstWeekOfMonth = weeks.value[i - currentMonthWeekCount];
                const firstWeekDayCell = firstWeekOfMonth.find((cell) => cell !== null);
                if (!firstWeekDayCell) {
                    currentMonth = month;
                    currentMonthWeekCount = 1;
                    continue;
                }

                labels.push({
                    label: new Date(firstWeekDayCell.date).toLocaleDateString(undefined, {
                        month: "short",
                    }),
                    weekCount: currentMonthWeekCount,
                });
            }
            currentMonth = month;
            currentMonthWeekCount = 1;
        } else {
            currentMonthWeekCount++;
        }
    }

    if (currentMonthWeekCount > 0) {
        const firstWeekOfMonth = weeks.value[weeks.value.length - currentMonthWeekCount];
        const firstWeekDayCell = firstWeekOfMonth.find((cell) => cell !== null);
        if (firstWeekDayCell) {
            labels.push({
                label: new Date(firstWeekDayCell.date).toLocaleDateString(undefined, {
                    month: "short",
                }),
                weekCount: currentMonthWeekCount,
            });
        }
    }

    return labels;
});
</script>

<style scoped>
.streak-calendar {
    --cell-size: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.25rem;
    border-radius: 12px;
    background-color: var(--p-content-background);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.streak-calendar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.title {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--p-text-color);
}

.subtitle {
    margin: 0.15rem 0 0;
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}

.legend {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: var(--p-text-muted-color);
}

.legend-squares {
    display: flex;
    gap: 0.15rem;
}

.legend-square {
    width: var(--cell-size);
    height: var(--cell-size);
    border-radius: 3px;
}

.legend-square.level-0 {
    background-color: var(--p-content-hover-background);
}

.legend-square.level-1 {
    background-color: var(--p-green-200);
}

.legend-square.level-2 {
    background-color: var(--p-green-300);
}

.legend-square.level-3 {
    background-color: var(--p-green-500);
}

.legend-square.level-4 {
    background-color: var(--p-green-700);
}

.legend-label {
    white-space: nowrap;
}

.calendar-loading {
    padding: 1.5rem;
    font-size: 0.9rem;
    color: var(--p-text-muted-color);
}

.calendar-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.calendar-empty-state {
    padding: 1.25rem;
    border-radius: 8px;
    border: 1px dashed var(--p-content-border-color);
    background-color: var(--p-content-hover-background);
    font-size: 0.9rem;
    color: var(--p-text-muted-color);
}

.calendar-layout {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.calendar-body {
    display: flex;
    gap: 0.75rem;
    overflow: hidden;
}

.weekday-labels {
    display: grid;
    grid-template-rows: repeat(7, 1fr);
    gap: 3px;
    font-size: 0.75rem;
    color: var(--p-text-muted-color);
    min-width: 2.5rem;
    flex-shrink: 0;
}

.weekday-label {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    min-height: 0.9rem;
}

.calendar-scroll-container {
    flex: 1;
    overflow-x: auto;
    overflow-y: hidden;
}

.month-labels {
    display: flex;
    gap: 3px;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--p-text-color);
    margin-bottom: 0.25rem;
    min-height: 1.2rem;
}

.month-label {
    text-align: left;
    padding-left: 0.15rem;
    flex-shrink: 0;
}

.calendar-grid {
    display: flex;
    gap: 3px;
    padding-bottom: 0.25rem;
}

.calendar-week {
    display: grid;
    grid-template-rows: repeat(7, 1fr);
    gap: 3px;
}

.calendar-day {
    width: var(--cell-size);
    height: var(--cell-size);
    border-radius: 3px;
    transition: box-shadow 0.06s ease;
}

.calendar-day.level-0 {
    background-color: var(--p-content-hover-background);
}

.calendar-day.level-1 {
    background-color: var(--p-green-200);
}

.calendar-day.level-2 {
    background-color: var(--p-green-300);
}

.calendar-day.level-3 {
    background-color: var(--p-green-500);
}

.calendar-day.level-4 {
    background-color: var(--p-green-700);
}

.calendar-day:hover {
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.18);
}

.calendar-day.is-today {
    outline: 2px solid var(--p-primary-color);
    outline-offset: -1px;
}

.calendar-day.is-empty {
    background-color: transparent;
    box-shadow: none;
}

@media (max-width: 768px) {
    .streak-calendar {
        --cell-size: 0.8rem;
        padding: 1rem;
    }

    .streak-calendar-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
    }

    .legend {
        font-size: 0.7rem;
    }

    .calendar-day,
    .legend-square {
        width: var(--cell-size);
        height: var(--cell-size);
    }

    .month-labels {
        font-size: 0.7rem;
    }

    .weekday-labels {
        min-width: 2rem;
        font-size: 0.7rem;
    }

    .calendar-body {
        gap: 0.5rem;
    }
}

@media (max-width: 480px) {
    .streak-calendar {
        padding: 0.75rem;
    }

    .title {
        font-size: 1rem;
    }

    .subtitle {
        font-size: 0.8rem;
    }
}
</style>
