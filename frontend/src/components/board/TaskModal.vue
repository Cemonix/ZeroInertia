<template>
    <Dialog
        :visible="isVisible"
        @update:visible="isVisible = $event"
        :header="task ? 'Edit Task' : 'New Task'"
        modal
    >
        <div>
            <div class="form-field">
                <label for="title">Title</label>
                <InputText id="title" v-model="title" />
            </div>
            <div class="form-field">
                <label for="description">Description</label>
                <Textarea id="description" v-model="description" rows="4" />
            </div>
            <div class="button-group">
                <Button
                    label="Save"
                    @click="saveTask"
                    :disabled="title.trim() === '' || isLoading"
                />
            </div>
        </div>
    </Dialog>
</template>

<script lang="ts" setup>
import { ref, computed, watch, type Ref } from "vue";
import { taskService } from "@/services/taskService";
import type { Task } from "@/models/task";
import Dialog from "primevue/dialog";
import Textarea from "primevue/textarea";

const props = defineProps<{
    modelValue: boolean;
    taskId: string | null;
}>();

const emit = defineEmits<{
    (e: "update:modelValue", value: boolean): void;
    (e: "task-updated", task: Task): void;
    (e: "task-created", task: Task): void;
}>();

const task: Ref<Task | null> = ref(null);
const isLoading = ref(false);
const title = ref("");
const description: Ref<string | null> = ref(null);
const isDone = ref(false);

// Computed property for two-way binding with parent
const isVisible = computed({
    get: () => props.modelValue,
    set: (value) => emit("update:modelValue", value)
});

// Watch for modal opening to load task or reset form
watch(
    () => props.modelValue,
    (newVal) => {
        if (newVal && props.taskId) {
            loadTask(props.taskId);
        } else if (newVal) {
            resetForm();
        }
    }
);

async function loadTask(id: string) {
    isLoading.value = true;

    try {
        task.value = await taskService.getTaskById(id);
    } catch (error) {
        console.error("Failed to load task:", error);
        task.value = null;
    }

    if (task.value) {
        title.value = task.value.title;
        description.value = task.value.description;
        isDone.value = task.value.is_done;
    }
    isLoading.value = false;
}

function resetForm() {
    task.value = null;
    title.value = "";
    description.value = "";
}

async function saveTask() {
    if (title.value.trim() === "") return;

    isLoading.value = true;
    if (task.value) {
        // Update existing task
        try{
            const updatedTask = await taskService.updateTask(task.value.id, {
                title: title.value,
                description: description.value,
            });
            emit("task-updated", updatedTask);
        }
        catch(error){
            console.error("Failed to update task:", error);
            isLoading.value = false;
            return;
        }
    } else {
        // Create new task
        try{
            const newTask = await taskService.createTask({
                title: title.value,
                description: description.value,
            } as Task);
            emit("task-created", newTask);
        }
        catch(error){
            console.error("Failed to create task:", error);
            isLoading.value = false;
            return;
        }
    }
    isLoading.value = false;
    isVisible.value = false;
}
</script>

<style scoped>
.form-field {
    margin-bottom: 1rem;
}

.form-field label {
    display: block;
    margin-bottom: 0.5rem;
}

.button-group {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}
</style>
