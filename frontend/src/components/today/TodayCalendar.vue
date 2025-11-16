<template>
    <div class="today-calendar-container">
        <VueCal
            ref="vuecalRef"
            :views-bar="false"
            :time="true"
            :time-from="timeFrom"
            :time-to="timeTo"
            :time-step="30"
            :events="calendarEvents"
            :editable-events="{ create: true, resize: true, drag: true, delete: false }"
            :snap-to-interval="15"
            :watch-real-time="true"
            :dark="isDarkMode"
            view="day"
            :views="['day']"
            :hide-view-selector="true"
            :disable-views="['years', 'year', 'month', 'week']"
            all-day-events
            class="vuecal-instance"
            @event-click="handleEventClick"
            @event-drop="handleEventDrop"
            @event-resize-end="handleEventResize"
            @event-create="handleEventCreate"
            @ready="onCalendarReady"
            @view-change="handleViewChange"
        >
            <template #event="{ event }">
                <div class="calendar-event-content" :class="{ 'compact-event': event.isCompact }">
                    <div class="event-title-row">
                        <div class="event-checkbox" @click.stop>
                            <Checkbox
                                :model-value="event.task.completed"
                                binary
                                @update:model-value="() => handleToggleComplete(event)"
                            />
                        </div>
                        <FontAwesomeIcon
                            v-if="event.priority"
                            icon="flag"
                            :style="{ color: event.priority.color }"
                            class="event-priority-flag"
                        />
                        <span class="event-title">{{ event.title }}</span>
                        <span
                            v-if="event.isCompact"
                            class="event-time event-time-compact"
                        >
                            {{ formatEventTime(event) }}
                        </span>
                    </div>
                    <div class="event-meta" v-if="!event.isCompact">
                        <span class="event-time">
                            {{ formatEventTime(event) }}
                        </span>
                        <div v-if="event.labels && event.labels.length" class="event-labels">
                            <span
                                v-for="label in event.labels"
                                :key="label.id"
                                class="event-label"
                                :style="{ backgroundColor: label.color }"
                                :title="label.name"
                            ></span>
                        </div>
                    </div>
                    <div
                        v-else-if="event.labels && event.labels.length"
                        class="event-labels event-labels-compact"
                    >
                        <span
                            v-for="label in event.labels"
                            :key="label.id"
                            class="event-label"
                            :style="{ backgroundColor: label.color }"
                            :title="label.name"
                        ></span>
                    </div>
                </div>
            </template>
        </VueCal>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
// @ts-expect-error - vue-cal doesn't have proper TypeScript declarations
import { VueCal } from 'vue-cal';
import 'vue-cal/style.css';
import Checkbox from 'primevue/checkbox';
import type { Task } from '@/models/task';
import type { Priority } from '@/models/priority';
import type { Label } from '@/models/label';
import { useTaskStore } from '@/stores/task';
import { usePriorityStore } from '@/stores/priority';
import { useToast } from 'primevue/usetoast';
import { useTheme } from '@/composables/useTheme';

interface VueCalEvent {
    start: Date | string;
    end: Date | string;
    startMinutes: number;
    endMinutes: number;
    title: string;
    content: string;
    class: string;
    backgroundColor: string;
    color: string;
    allDay: boolean;
    taskId: string;
    priority: Priority | null;
    labels: Label[];
    task: Task;
    isCompact: boolean;
}

interface VueCalEventClickPayload {
    event: VueCalEvent;
}

interface VueCalEventDropPayload {
    event: VueCalEvent;
}

interface VueCalEventResizePayload {
    event: VueCalEvent;
}

interface VueCalEventCreatePayload {
    event: VueCalEvent;
    cell: {
        date: Date;
    };
    cursor: {
        x: number;
        y: number;
        date: Date;
    };
    resolve: (value: boolean | VueCalEvent) => void;
}

interface VueCalReadyPayload {
    view: {
        scrollToTime: (minutes: number) => void;
        scrollToCurrentTime: () => void;
        scrollTop: () => void;
    };
}

interface Props {
    currentDate?: Date;
}

const props = withDefaults(defineProps<Props>(), {
    currentDate: () => new Date(),
});

const emit = defineEmits<{
    'update:currentDate': [date: Date];
}>();

const taskStore = useTaskStore();
const priorityStore = usePriorityStore();
const toast = useToast();
const { isDarkMode } = useTheme();

const vuecalRef = ref<InstanceType<typeof VueCal> | null>(null);
const tasks = ref<Task[]>([]);
const isLoadingTasks = ref(false);
const currentLoadedDate = ref<string>('');

const timeFrom = 0;
const timeTo = 24 * 60;

// Load tasks for a specific date
async function loadTasksForDate(date: Date) {
    const dateKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;

    // Avoid loading the same date twice
    if (currentLoadedDate.value === dateKey) {
        return;
    }

    isLoadingTasks.value = true;
    try {
        const startOfDay = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0);
        const endOfDay = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1, 0, 0, 0);

        tasks.value = await taskStore.loadTasksByDateRange(startOfDay, endOfDay);
        currentLoadedDate.value = dateKey;
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Failed to load tasks',
            detail: 'Please try again',
            life: 3000,
        });
    } finally {
        isLoadingTasks.value = false;
    }
}

// Transform tasks into vue-cal events format
const calendarEvents = computed(() => {
    const events = tasks.value.map(task => {
        // If no due_datetime, treat as all-day event for today
        let startDate: Date;
        let isAllDay: boolean;

        if (!task.due_datetime) {
            // No date set - create all-day event for today
            const today = new Date();
            startDate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 0, 0, 0);
            isAllDay = true;
        } else {
            startDate = new Date(task.due_datetime);
            // Determine if this is an all-day event (no specific time set - midnight)
            isAllDay = startDate.getHours() === 0 && startDate.getMinutes() === 0 && startDate.getSeconds() === 0;
        }

        const scheduledDurationMinutes =
            !isAllDay && task.duration_minutes && task.duration_minutes > 0
                ? task.duration_minutes
                : 30;

        let endDate: Date;
        let start: Date | string;
        let end: Date | string;

        // Calculate end time based on duration
        if (isAllDay) {
            // For all-day events, use YYYY-MM-DD string format
            // End date should be the next day for proper rendering
            const year = startDate.getFullYear();
            const month = String(startDate.getMonth() + 1).padStart(2, '0');
            const day = String(startDate.getDate()).padStart(2, '0');
            start = `${year}-${month}-${day}`;

            // End should be the next day
            const nextDay = new Date(startDate);
            nextDay.setDate(nextDay.getDate() + 1);
            const endYear = nextDay.getFullYear();
            const endMonth = String(nextDay.getMonth() + 1).padStart(2, '0');
            const endDay = String(nextDay.getDate()).padStart(2, '0');
            end = `${endYear}-${endMonth}-${endDay}`;
        } else {
            // For timed events, use Date objects
            start = startDate;
            endDate = new Date(startDate.getTime() + scheduledDurationMinutes * 60000);
            end = endDate;
        }

        // Get priority and labels for styling
        const priority = task.priority_id ? priorityStore.getPriorityById(task.priority_id) : null;
        const labels = task.labels || [];

        // Determine event background color
        let backgroundColor = 'var(--p-primary-color)';
        if (priority) {
            backgroundColor = priority.color + 'cc'; // Add transparency
        } else if (labels.length > 0) {
            backgroundColor = labels[0].color + 'cc';
        }

        const isCompact = !isAllDay && scheduledDurationMinutes <= 15;

        return {
            start,
            end,
            title: task.title,
            content: task.description || '',
            class: `task-event priority-${task.priority_id || 'none'}${isAllDay ? ' all-day-task' : ''}`,
            backgroundColor,
            color: '#ffffff',
            allDay: isAllDay,
            // Store original task data for editing
            taskId: task.id,
            priority,
            labels,
            task,
            isCompact,
        };
    });

    return events;
});

// Format event time range for display
function formatEventTime(event: VueCalEvent): string {
    // Don't show time for all-day events
    if (event.allDay) {
        return 'All day';
    }

    const start = new Date(event.start);
    const end = new Date(event.end);

    const formatTime = (date: Date): string => {
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    };

    return `${formatTime(start)} - ${formatTime(end)}`;
}

const handleToggleComplete = (event: VueCalEvent) => {
    taskStore.toggleTaskComplete(event.taskId);
};

const handleEventClick = ({ event }: VueCalEventClickPayload) => {
    const task = event.task;
    // Open task modal with the task's section
    taskStore.openTaskModal(task.section_id, task);
};

// Handle event drag & drop - update task due_datetime
const handleEventDrop = async ({ event }: VueCalEventDropPayload) => {
    const task = event.task;
    const newDueDateTime = typeof event.start === 'string' ? new Date(event.start) : event.start;

    try {
        await taskStore.updateTask(task.id, {
            due_datetime: newDueDateTime.toISOString(),
        });

        const timeDisplay = event.allDay
            ? 'all day'
            : newDueDateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        toast.add({
            severity: 'success',
            summary: 'Task rescheduled',
            detail: `"${task.title}" moved to ${timeDisplay}`,
            life: 3000,
        });
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Failed to reschedule task',
            detail: 'Please try again',
            life: 3000,
        });
        // Revert the event position by rejecting the drop
        return false;
    }
};

const handleEventResize = async ({ event }: VueCalEventResizePayload) => {
    const task = event.task;
    const startTime = typeof event.start === 'string' ? new Date(event.start) : event.start;
    const endTime = typeof event.end === 'string' ? new Date(event.end) : event.end;
    const newDuration = Math.round((endTime.getTime() - startTime.getTime()) / 60000);

    try {
        await taskStore.updateTask(task.id, {
            duration_minutes: newDuration,
        });

        toast.add({
            severity: 'success',
            summary: 'Task duration updated',
            detail: `"${task.title}" is now ${newDuration} minutes`,
            life: 3000,
        });
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Failed to update duration',
            detail: 'Please try again',
            life: 3000,
        });
        // Revert the resize by rejecting
        return false;
    }
};

const handleEventCreate = async ({ event, resolve }: VueCalEventCreatePayload) => {
    // Extract start time and compute duration from event object
    const startDateTime = new Date(event.start);
    const durationMinutes = event.endMinutes - event.startMinutes;

    // Round to nearest 15-minute interval
    const minutes = startDateTime.getMinutes();
    const roundedMinutes = Math.round(minutes / 15) * 15;
    startDateTime.setMinutes(roundedMinutes, 0, 0);

    resolve(false);

    const initialValues = {
        due_datetime: startDateTime.toISOString(),
        duration_minutes: durationMinutes,
        project_id: null,
        section_id: null,
    };

    taskStore.openTaskModal(null, null, initialValues);
};

// Scroll to current time when calendar is ready
const onCalendarReady = ({ view }: VueCalReadyPayload) => {
    // Scroll to current time or 8 AM, whichever is later
    const now = new Date();
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    const scrollToMinutes = Math.max(currentMinutes - 60, 8 * 60); // 1 hour before current or 8 AM

    view.scrollToTime(scrollToMinutes);
};

const handleViewChange = (payload: any) => {
    // Vue-cal passes the view object with start/end dates
    let newDate: Date;

    if (payload.start) {
        newDate = new Date(payload.start);
    } else if (payload.startDate) {
        newDate = new Date(payload.startDate);
    } else if (payload.view?.start) {
        newDate = new Date(payload.view.start);
    } else if (payload.date) {
        newDate = new Date(payload.date);
    } else {
        console.warn('Vue-cal view-change: unknown payload structure', payload);
        return;
    }

    // Ensure we have a valid date
    if (isNaN(newDate.getTime())) {
        console.warn('Vue-cal view-change: invalid date', newDate);
        return;
    }

    emit('update:currentDate', newDate);
    loadTasksForDate(newDate);
};

watch(() => props.currentDate, (newDate: Date | undefined, oldDate: Date | undefined) => {
    if (newDate) {
        // Check if date actually changed to avoid infinite loops
        const newKey = `${newDate.getFullYear()}-${newDate.getMonth()}-${newDate.getDate()}`;
        const oldKey = oldDate ? `${oldDate.getFullYear()}-${oldDate.getMonth()}-${oldDate.getDate()}` : '';

        if (newKey !== oldKey) {
            loadTasksForDate(newDate);

            // Update vue-cal's view if we have a reference
            if (vuecalRef.value && typeof vuecalRef.value.switchToNarrower === 'function') {
                try {
                    vuecalRef.value.switchToNarrower(newDate);
                } catch (e) {
                    // Silently ignore if method doesn't exist or fails
                }
            }
        }
    }
});

onMounted(() => {
    loadTasksForDate(props.currentDate);
});
</script>

<style scoped>
.today-calendar-container {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
}

/* Vue-cal custom styling to match your theme */
:deep(.vuecal) {
    --vuecal-primary-color: var(--p-primary-color);
    --vuecal-base-color: var(--p-content-background);
    --vuecal-contrast-color: var(--p-text-color);
    --vuecal-border-color: var(--p-content-border-color);
    --vuecal-header-color: var(--p-content-background);
    --vuecal-event-color: var(--p-content-background);
    --vuecal-border-radius: 6px;
    --vuecal-transition-duration: 0.2s;

    box-sizing: border-box;
    max-height: calc(100vh - 220px);
    min-height: 400px; /* Minimum usable height */
    border-radius: var(--vuecal-border-radius);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    font-family: var(--p-font-family);
    background: var(--p-content-background);
    overflow: hidden; /* Prevent calendar from growing beyond bounds */
}

/* Ensure the VueCal instance takes full container space */
.vuecal-instance {
    flex: 1;
    width: 100%;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .today-calendar-container {
        padding: 0.75rem;
    }
    
    :deep(.vuecal) {
        height: calc(100vh - 180px);
        max-height: calc(100vh - 180px);
        min-height: 350px;
    }
}

@media (max-width: 480px) {
    .today-calendar-container {
        padding: 0.5rem;
    }
    
    :deep(.vuecal) {
        height: calc(100vh - 150px);
        max-height: calc(100vh - 150px);
        min-height: 300px;
    }
}

:deep(.vuecal__title) {
    font-size: 1rem;
    color: var(--p-text-color);
}

:deep(.vuecal__time-cell) {
    color: var(--p-text-muted-color);
    font-size: 0.875rem;
}

:deep(.vuecal__now-line) {
    color: var(--p-text-color);
    text-shadow: 0 0 2px var(--p-content-background);
    font-weight: 600;
}

/* Event styling */
:deep(.vuecal__event) {
    border: none;
    border-radius: 4px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

:deep(.vuecal__event.task-event) {
    min-height: 22px;
}

:deep(.vuecal__event:hover) {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

:deep(.vuecal__event--dragging-ghost) {
    opacity: 0.7;
    transform: scale(1.05);
}

:deep(.vuecal__event--all-day) {
    border-left: 3px solid currentColor;
    background: linear-gradient(to right, currentColor 3px, var(--vuecal-event-color) 3px);
}

/* Custom event content styling */
.calendar-event-content {
    padding: 4px 8px;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 4px;
    overflow: hidden;
}

.event-title-row {
    display: flex;
    align-items: center;
    gap: 2px;
    font-weight: 500;
}

.event-priority-flag {
    font-size: 0.75rem;
    flex-shrink: 0;
}

.event-title {
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 0.875rem;
}

.event-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    font-size: 0.75rem;
}

.event-time {
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.7rem;
    white-space: nowrap;
    flex-shrink: 0;
}

.event-labels {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
}

.calendar-event-content.compact-event {
    padding: 2px 8px;
    gap: 3px;
}

.calendar-event-content.compact-event .event-title {
    flex: 0 1 auto;
    min-width: 0;
}

.calendar-event-content.compact-event .event-meta {
    font-size: 0.7rem;
}

.event-time-compact {
    opacity: 0.9;
    display: inline-flex;
    align-items: center;
    font-size: 0.875rem;
    line-height: 1;
    margin-left: 0.35rem;
}

.event-labels-compact {
    margin-top: 2px;
}

.event-label {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    flex-shrink: 0;
}

.event-checkbox {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

.event-checkbox :deep(.p-checkbox-box) {
    width: 14px;
    height: 14px;
    padding: 0;
    position: absolute;
    top: 50%;
    left: 35%;
    transform: translate(-50%, -50%);
}

/* All-day bar styling */
:deep(.vuecal__all-day-bar) {
    background: color-mix(in srgb, var(--p-content-background) 95%, var(--p-text-color) 5%);
    border-bottom: 1px solid var(--p-content-border-color);
    min-height: 60px;
}

:deep(.vuecal__all-day-bar .vuecal__cell-date) {
    font-weight: 600;
    color: var(--p-text-color);
}

:deep(.vuecal__all-day-bar .vuecal__no-event) {
    display: none;
}

/* All-day event styling - ensure readable text on colored backgrounds */
:deep(.vuecal__all-day-label) {
    color: var(--p-text-color);
}

/* Scrollbar styling */
:deep(.vuecal__scrollable::-webkit-scrollbar) {
    width: 8px;
}

:deep(.vuecal__scrollable::-webkit-scrollbar-track) {
    background: color-mix(in srgb, var(--p-content-background) 95%, var(--p-text-color) 5%);
}

:deep(.vuecal__scrollable::-webkit-scrollbar-thumb) {
    background: color-mix(in srgb, var(--p-content-background) 70%, var(--p-text-color) 30%);
    border-radius: 4px;
}

:deep(.vuecal__scrollable::-webkit-scrollbar-thumb:hover) {
    background: color-mix(in srgb, var(--p-content-background) 50%, var(--p-text-color) 50%);
}
</style>
