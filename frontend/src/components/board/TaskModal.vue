<template>
    <Dialog
        :visible="taskStore.isTaskModalVisible"
        @update:visible="taskStore.setTaskModalVisible($event)"
        :header="taskStore.getCurrentTask ? 'Edit Task' : 'New Task'"
        modal
    >
        <div>
            <div class="form-field">
                <label for="title">Title</label>
                <InputText
                    id="title"
                    v-model="title"
                    autofocus
                />
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
import { ref, watch, type Ref } from "vue";
import Textarea from "primevue/textarea";
import { useTaskStore } from "@/stores/task";

const props = defineProps<{
    projectId: string;
}>();

const taskStore = useTaskStore();

const isLoading = ref(false);
const title = ref("");
const description: Ref<string | null> = ref(null);
const taskCompleted = ref(false);

// Watch for modal visibility changes and load task data
watch(
    () => taskStore.isTaskModalVisible,
    (newVal) => {
        if (newVal) {
            const currentTask = taskStore.getCurrentTask;
            if (currentTask) {
                // Editing existing task
                title.value = currentTask.title;
                description.value = currentTask.description;
                taskCompleted.value = currentTask.completed;
            } else {
                // Creating new task
                resetForm();
            }
        }
    }
);

async function saveTask() {
    if (title.value.trim() === "" || !taskStore.currentSectionId) return;

    isLoading.value = true;
    const currentTask = taskStore.getCurrentTask;

    try {
        if (currentTask) {
            // Update existing task
            await taskStore.updateTask(currentTask.id, {
                title: title.value,
                description: description.value,
                completed: taskCompleted.value,
            });
        } else {
            // Create new task
            await taskStore.createTask({
                project_id: props.projectId,
                section_id: taskStore.currentSectionId,
                title: title.value,
                description: description.value,
            });
        }
        taskStore.setTaskModalVisible(false);
    } catch (error) {
        console.error("Failed to save task:", error);
    } finally {
        isLoading.value = false;
    }
}

function resetForm() {
    title.value = "";
    description.value = "";
    taskCompleted.value = false;
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
