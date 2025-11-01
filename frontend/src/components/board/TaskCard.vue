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
                    <FontAwesomeIcon v-if="taskPriority" icon="flag" :style="{ color: taskPriority.color }" class="priority-flag" />
                    {{ task.title }}
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
                <div v-if="task.due_datetime" class="task-due-date" :class="{ 'overdue': isOverdue, 'future': isFuture }">
                    <FontAwesomeIcon icon="calendar" />
                    <span>{{ formattedDueDate }}</span>
                </div>
            </div>
        </div>

        <!-- Quick actions (shown on hover) -->
        <div class="task-actions">
            <Button
                text
                rounded
                size="small"
                severity="danger"
                class="task-delete-btn"
                @click.stop="handleDelete"
            >
                <template #icon>
                    <FontAwesomeIcon icon="trash" />
                </template>
            </Button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import type { Task } from "@/models/task";
import { useTaskStore } from "@/stores/task";
import { usePriorityStore } from "@/stores/priority";
import { useLabelStore } from "@/stores/label";
import type { Label } from "@/models/label";

const taskStore = useTaskStore();
const priorityStore = usePriorityStore();
const labelStore = useLabelStore();

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

// Format due date for display
const formattedDueDate = computed(() => {
    if (!props.task.due_datetime) return null;

    const dueDate = new Date(props.task.due_datetime);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const taskDate = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());

    const diffDays = Math.floor((taskDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    const timeStr = dueDate.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: false
    });

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
            hour: 'numeric',
            minute: '2-digit',
            hour12: false
        });
    }
});

const isOverdue = computed(() => {
    if (!props.task.due_datetime || props.task.completed) return false;
    return new Date(props.task.due_datetime) < new Date();
});

const isFuture = computed(() => {
    if (!props.task.due_datetime || props.task.completed) return false;

    const dueDate = new Date(props.task.due_datetime);
    const now = new Date();
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);

    return dueDate >= tomorrow;
});

const handleCardClick = (event: MouseEvent) => {
    // Don't trigger card click if clicking on checkbox or delete button
    const target = event.target as HTMLElement;
    if (
        target.closest(".task-checkbox") ||
        target.closest(".task-delete-btn")
    ) {
        return;
    }

    // Open task modal for editing
    taskStore.openTaskModal(props.task.section_id, props.task);
};

const handleToggleComplete = () => {
    taskStore.toggleTaskComplete(props.task.id);
};

const handleDelete = () => {
    taskStore.deleteTask(props.task.id);
};

onMounted(async () => {
    if (!labelStore.labels.length && props.task.label_ids?.length) {
        try {
            await labelStore.loadLabels();
        } catch (_error) {
            // Ignore label load errors for card display
        }
    }
});
</script>

<style scoped>
.task-card {
    background: white;
    border: 1px solid var(--p-surface-200);
    border-radius: 6px;
    padding: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: space-between;
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
    align-items: flex-start;
    gap: 0.75rem;
    flex: 1;
    min-width: 0; /* Allows text truncation */
}

.task-checkbox {
    flex-shrink: 0;
    padding-top: 0.125rem;
}

.task-details {
    flex: 1;
    min-width: 0;
}

.task-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9375rem;
    font-weight: 500;
    color: var(--p-text-color);
    margin-bottom: 0.25rem;
    word-wrap: break-word;
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
    opacity: 0;
    display: flex;
    gap: 0.25rem;
    flex-shrink: 0;
    transition: opacity 0.2s;
}

.task-card:hover .task-actions {
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

.task-due-date.future {
    color: var(--p-surface-500);
    opacity: 0.6;
}

/* Ensure actions are visible on touch devices */
@media (hover: none) {
    .task-actions {
        opacity: 1;
    }
}
</style>
