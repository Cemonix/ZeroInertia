<template>
    <div
        class="task-card"
        :class="{ 'task-completed': task.completed }"
        @click="handleCardClick"
    >
        <div class="task-content">
            <!-- Checkbox for completion status -->
            <div class="task-checkbox" @click.stop>
                <Checkbox
                    :model-value="task.completed"
                    binary
                    @update:model-value="handleToggleComplete"
                />
            </div>

            <!-- Task details -->
            <div class="task-details">
                <div
                    class="task-title"
                    :class="{ 'completed-text': task.completed }"
                >
                    <FontAwesomeIcon
                        v-if="taskPriority"
                        icon="flag"
                        :style="{ color: taskPriority.color }"
                        class="priority-flag"
                    />
                    <FontAwesomeIcon
                        v-if="hasChecklist"
                        icon="check-square"
                        class="task-checklist-icon"
                    />
                    <span class="task-title-text">{{ task.title }}</span>
                    <span v-if="isRecurring" class="recurring-pill">
                        <FontAwesomeIcon icon="repeat" />
                        <span>{{ recurrenceSummary }}</span>
                    </span>
                </div>
                <div v-if="task.description" class="task-description">
                    {{ task.description }}
                </div>
                <div v-if="taskLabels.length" class="task-labels">
                    <span
                        v-for="label in taskLabels"
                        :key="label.id"
                        class="task-label"
                        :style="{ backgroundColor: label.color + '33', color: label.color }"
                    >
                        {{ label.name }}
                    </span>
                </div>
                <div class="task-meta-row">
                    <div
                        v-if="task.due_datetime"
                        class="task-due-date"
                        :class="{ 'overdue': isOverdue, 'tomorrow': isTomorrow, 'future': isFuture }"
                    >
                        <FontAwesomeIcon icon="calendar" />
                        <span>{{ formattedDueDate }}</span>
                    </div>
                    <div v-if="reminderLabel" class="task-reminder">
                        <FontAwesomeIcon icon="bell" />
                        <span>{{ reminderLabel }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick actions (shown on hover) -->
        <div class="task-actions">
            <TaskQuickActions :task="task" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Task } from "@/models/task";
import { useTaskStore } from "@/stores/task";
import { usePriorityStore } from "@/stores/priority";
import { useLabelStore } from "@/stores/label";
import { useChecklistStore } from "@/stores/checklist";
import type { Label } from "@/models/label";
import { formatRecurrence } from "@/utils/recurrenceUtils";
import { useToast } from "primevue/usetoast";
import TaskQuickActions from "@/components/tasks/TaskQuickActions.vue";

const taskStore = useTaskStore();
const priorityStore = usePriorityStore();
const labelStore = useLabelStore();
const checklistStore = useChecklistStore();
const toast = useToast();


interface Props {
    task: Task;
}

const props = defineProps<Props>();

// Get the full priority object for this task
const taskPriority = computed(() => {
    if (!props.task.priority_id) return null;
    return priorityStore.getPriorityById(props.task.priority_id);
});

const taskLabels = computed<Label[]>(() => {
    if (props.task.labels?.length) {
        return props.task.labels;
    }

    if (props.task.label_ids?.length) {
        return props.task.label_ids
            .map(id => labelStore.getLabelById(id))
            .filter((label): label is Label => Boolean(label));
    }

    return [];
});

const hasChecklist = computed(() => {
    const taskId = props.task.id;
    const lists = checklistStore.getChecklistsByTask(taskId);
    return lists.length > 0;
});

const recurrenceSummary = computed(() => {
    return formatRecurrence(
        props.task.recurrence_interval,
        props.task.recurrence_unit,
        props.task.recurrence_days
    ) || null;
});

const isRecurring = computed(() => Boolean(recurrenceSummary.value));

// Format due date for display
const formattedDueDate = computed(() => {
    if (!props.task.due_datetime) return null;

    const dueDate = new Date(props.task.due_datetime);
    const duration = props.task.duration_minutes ?? null;
    const endDate = duration && duration > 0
        ? new Date(dueDate.getTime() + duration * 60_000)
        : null;

    const fmtTime = (d: Date) => d.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
    });
    const fmtShortDate = (d: Date) => d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
    });

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const taskDate = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());
    const diffDays = Math.floor((taskDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    // If duration crosses day boundary, show full date for both ends
    if (endDate) {
        const sameDay = dueDate.getFullYear() === endDate.getFullYear() &&
            dueDate.getMonth() === endDate.getMonth() &&
            dueDate.getDate() === endDate.getDate();
        const startTime = fmtTime(dueDate);
        const endTime = fmtTime(endDate);
        if (!sameDay) {
            return `${fmtShortDate(dueDate)}, ${startTime} - ${fmtShortDate(endDate)}, ${endTime}`;
        }

        if (diffDays === 0) {
            return `Today ${startTime} - ${endTime}`;
        } else if (diffDays === 1) {
            return `Tomorrow ${startTime} - ${endTime}`;
        } else if (diffDays === -1) {
            return `Yesterday ${startTime} - ${endTime}`;
        } else if (diffDays > 1 && diffDays < 7) {
            const dayName = dueDate.toLocaleDateString('en-US', { weekday: 'long' });
            return `${dayName} ${startTime} - ${endTime}`;
        } else {
            return `${fmtShortDate(dueDate)}, ${startTime} - ${endTime}`;
        }
    }

    // No duration: keep previous format
    const timeStr = fmtTime(dueDate);
    if (diffDays === 0) {
        return `Today at ${timeStr}`;
    } else if (diffDays === 1) {
        return `Tomorrow at ${timeStr}`;
    } else if (diffDays === -1) {
        return `Yesterday at ${timeStr}`;
    } else if (diffDays > 1 && diffDays < 7) {
        const dayName = dueDate.toLocaleDateString('en-US', { weekday: 'long' });
        return `${dayName} at ${timeStr}`;
    } else {
        return dueDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        });
    }
});

const isOverdue = computed(() => {
    if (!props.task.due_datetime || props.task.completed) return false;
    return new Date(props.task.due_datetime) < new Date();
});

const isTomorrow = computed(() => {
    if (!props.task.due_datetime || props.task.completed) return false;

    const dueDate = new Date(props.task.due_datetime);
    const now = new Date();
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    const dayAfterTomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 2);

    return dueDate >= tomorrow && dueDate < dayAfterTomorrow;
});

const isFuture = computed(() => {
    if (!props.task.due_datetime || props.task.completed) return false;

    const dueDate = new Date(props.task.due_datetime);
    const now = new Date();
    const dayAfterTomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 2);

    return dueDate >= dayAfterTomorrow;
});


const handleCardClick = (event: MouseEvent) => {
    // Ignore clicks originating from interactive controls
    const target = event.target as HTMLElement;
    if (
        target.closest(".task-checkbox") ||
        target.closest(".task-actions")
    ) {
        return;
    }

    taskStore.openTaskModal(props.task.section_id, props.task);
};

const handleToggleComplete = async () => {
    const wasCompleted = props.task.completed;
    try {
        await taskStore.toggleTaskComplete(props.task.id);
        if (!wasCompleted) {
            toast.add({
                severity: "success",
                summary: "Task completed",
                detail: `"${props.task.title}" marked as complete.`,
                life: 3000,
            });
        }
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Failed to update task",
            detail: error instanceof Error ? error.message : "Unknown error",
            life: 3000,
        });
    }
};

const formatReminderLabel = (minutes: number) => {
    if (minutes === 0) return "Reminder at due time";
    if (minutes < 60) return `${minutes}m before`;
    if (minutes < 1440 && minutes % 60 === 0) return `${minutes / 60}h before`;
    if (minutes >= 1440 && minutes % 1440 === 0) return `${minutes / 1440}d before`;
    if (minutes < 1440) return `${minutes}m before`;
    return `${(minutes / 1440).toFixed(1)}d before`;
};

const reminderLabel = computed(() => {
    const minutes = props.task.reminder_minutes;
    if (minutes === null || minutes === undefined) {
        return null;
    }

    return formatReminderLabel(minutes);
});
</script>

<style scoped>
.task-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 6px;
    padding: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    gap: 0.5rem;
}

.task-card:hover {
    border-color: var(--p-primary-color);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.task-card.task-completed {
    opacity: 0.7;
}

.task-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
    min-width: 0; /* Allows text truncation */
}

.task-checkbox {
    flex-shrink: 0;
    display: flex;
    align-items: center;
}

.task-details {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.task-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9375rem;
    font-weight: 500;
    color: var(--p-text-color);
    word-wrap: break-word;
}

.task-title-text {
    flex: 1;
    min-width: 0;
}

.recurring-pill {
    display: inline-flex;
    align-items: flex-start;
    gap: 0.3rem;
    border-radius: 10px;
    padding: 0.125rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 500;
    background: rgba(59, 130, 246, 0.15);
    color: var(--p-primary-color);
    flex-shrink: 0;
    max-width: 7rem;
}

.recurring-pill span:last-child {
    white-space: normal;
    line-height: 1.1;
}

.task-title.completed-text {
    text-decoration: line-through;
    color: var(--p-text-color);
    opacity: 0.5;
}

.task-description {
    font-size: 0.875rem;
   color: var(--p-text-color);
    opacity: 0.7;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.task-labels {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.35rem;
}

.task-label {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.125rem 0.5rem;
    border-radius: 5px;
    color: var(--p-text-color);
    font-size: 0.75rem;
}

.task-actions {
    display: flex;
    gap: 0.5rem;
    flex-shrink: 0;
    align-items: center;
}

.task-actions :deep(.task-menu-trigger) {
    opacity: 0;
    transition: opacity 0.2s;
}

.task-card:hover .task-actions :deep(.task-menu-trigger) {
    opacity: 1;
}

.reminder-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--p-primary-color);
    font-size: 0.875rem;
    opacity: 0.8;
    transition: opacity 0.2s;
}

.task-card:hover .reminder-indicator {
    opacity: 1;
}

.task-due-date {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: var(--p-green-600);
    opacity: 0.7;
    margin-top: 0.25rem;
}

.task-due-date.overdue {
    color: var(--p-red-500);
    opacity: 1;
}

.task-due-date.tomorrow {
    color: var(--p-orange-500);
    opacity: 0.9;
}

.task-due-date.future {
    color: var(--p-text-muted-color);
    opacity: 0.6;
}

.task-reminder {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    color: var(--p-primary-color);
    opacity: 0.75;
}

.task-meta-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.25rem;
}

.task-checklist-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--p-text-muted-color);
    font-size: 0.8rem;
}

/* Ensure menu trigger is visible on touch devices */
@media (hover: none) {
    .task-actions :deep(.task-menu-trigger) {
        opacity: 1;
    }
}
</style>
