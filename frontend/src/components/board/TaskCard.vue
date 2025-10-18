<template>
    <div
        class="task-card"
        :class="{ 'task-completed': task.is_done }"
        @click="handleCardClick"
    >
        <div class="task-content">
            <!-- Checkbox for completion status -->
            <div class="task-checkbox" @click.stop>
                <Checkbox
                    :model-value="task.is_done"
                    binary
                    @update:model-value="handleToggleComplete"
                />
            </div>

            <!-- Task details -->
            <div class="task-details">
                <div
                    class="task-title"
                    :class="{ 'completed-text': task.is_done }"
                >
                    {{ task.title }}
                </div>
                <div v-if="task.description" class="task-description">
                    {{ task.description }}
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
                v-tooltip.top="'Delete task'"
            >
                <template #icon>
                    <FontAwesomeIcon icon="trash" />
                </template>
            </Button>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Task } from "@/models/task";

interface Props {
    task: Task;
}

defineProps<Props>();

const emit = defineEmits<{
    click: [];
    toggleComplete: [];
    delete: [];
}>();

const handleCardClick = (event: MouseEvent) => {
    // Don't trigger card click if clicking on checkbox or delete button
    const target = event.target as HTMLElement;
    if (
        target.closest(".task-checkbox") ||
        target.closest(".task-delete-btn")
    ) {
        return;
    }
    emit("click");
};

const handleToggleComplete = () => {
    emit("toggleComplete");
};

const handleDelete = () => {
    emit("delete");
};
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

/* Ensure actions are visible on touch devices */
@media (hover: none) {
    .task-actions {
        opacity: 1;
    }
}
</style>
