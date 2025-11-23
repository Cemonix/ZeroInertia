<template>
    <div class="task-quick-actions">
        <Button
            text
            rounded
            size="small"
            class="task-menu-trigger"
            aria-haspopup="true"
            :aria-controls="menuId"
            aria-label="Task options"
            @click.stop="toggleMenu"
        >
            <template #icon>
                <FontAwesomeIcon icon="ellipsis" />
            </template>
        </Button>
        <Menu
            :id="menuId"
            ref="menuRef"
            :model="menuItems"
            :popup="true"
        >
            <template #item="{ item }">
                <div class="menu-item-content">
                    <FontAwesomeIcon v-if="item.icon" :icon="item.icon" class="menu-item-icon" />
                    <span>{{ item.label }}</span>
                </div>
            </template>
        </Menu>

        <TaskMoveModal
            v-model:visible="showMoveModal"
            :task="task"
        />
    </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import Button from "primevue/button";
import Menu from "primevue/menu";
import type { MenuItem } from "primevue/menuitem";
import { useToast } from "primevue/usetoast";
import type { Task } from "@/models/task";
import { useTaskStore } from "@/stores/task";
import TaskMoveModal from "@/components/tasks/TaskMoveModal.vue";

const props = defineProps<{
    task: Task;
}>();

const emit = defineEmits<{
    deleted: [taskId: string];
    snoozed: [Task];
    duplicated: [Task | null];
}>();

type TaskMenuInstance = {
    toggle: (event: MouseEvent) => void;
    hide: () => void;
};

const taskStore = useTaskStore();
const toast = useToast();

const menuRef = ref<TaskMenuInstance | null>(null);
const showMoveModal = ref(false);

const menuId = computed(() => `task_menu_${props.task.id}`);

const toggleMenu = (event: MouseEvent) => {
    menuRef.value?.toggle(event);
};

const closeMenu = () => {
    menuRef.value?.hide();
};

const handleDelete = async () => {
    closeMenu();
    try {
        await taskStore.deleteTask(props.task.id);
        emit("deleted", props.task.id);
        toast.add({
            severity: "success",
            summary: "Task deleted",
            detail: `"${props.task.title}" has been removed.`,
            life: 3000,
        });
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Failed to delete task",
            detail: error instanceof Error ? error.message : "Unknown error",
            life: 3000,
        });
    }
};

const handleDuplicate = async () => {
    closeMenu();
    try {
        const newTask = await taskStore.duplicateTask(props.task.id);
        emit("duplicated", newTask ?? null);
        toast.add({
            severity: "success",
            summary: "Task duplicated",
            detail: `Created a copy of "${props.task.title}".`,
            life: 3000,
        });
    } catch (error) {
        emit("duplicated", null);
        toast.add({
            severity: "error",
            summary: "Failed to duplicate task",
            detail: error instanceof Error ? error.message : "Unknown error",
            life: 3000,
        });
    }
};

const handleSnooze = async () => {
    closeMenu();
    try {
        const updatedTask = await taskStore.snoozeTask(props.task.id);
        emit("snoozed", updatedTask);

        if (updatedTask?.due_datetime) {
            const dueDate = new Date(updatedTask.due_datetime);
            const formatted = dueDate.toLocaleString(undefined, {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            });
            toast.add({
                severity: "info",
                summary: "Task snoozed",
                detail: `Next due ${formatted}`,
                life: 3500,
            });
        } else {
            toast.add({
                severity: "info",
                summary: "Task snoozed",
                detail: "Task snoozed successfully.",
                life: 3500,
            });
        }
    } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to snooze task";
        toast.add({
            severity: "error",
            summary: "Error",
            detail: message,
            life: 4000,
        });
    }
};

const menuItems = computed<MenuItem[]>(() => {
    const items: MenuItem[] = [];

    if (props.task.due_datetime && !props.task.completed) {
        items.push({
            label: "Snooze Task",
            icon: "calendar-day",
            command: () => handleSnooze(),
        });
    }

    items.push({
        label: "Move to project",
        icon: "inbox",
        command: () => {
            closeMenu();
            showMoveModal.value = true;
        },
    });

    items.push(
        {
            label: "Duplicate Task",
            icon: "plus",
            command: () => handleDuplicate(),
        },
        {
            label: "Delete Task",
            icon: "trash",
            command: () => handleDelete(),
        },
    );

    return items;
});
</script>

<style scoped>
.task-quick-actions {
    display: flex;
    align-items: center;
    justify-content: center;
}

.menu-item-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem;
    width: 100%;
    cursor: pointer;
    user-select: none;
}

.menu-item-icon {
    width: 1rem;
    color: var(--p-text-muted-color);
}
</style>

