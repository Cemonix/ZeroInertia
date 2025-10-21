<template>
    <Dialog
        modal
        :visible="taskStore.isTaskModalVisible"
        @update:visible="taskStore.setTaskModalVisible($event)"
        :header="taskStore.getCurrentTask ? 'Edit Task' : 'New Task'"
        @hide="handleClose"
        :style="{ width: '768px' }"
        :pt="{
            root: { style: { maxWidth: '95vw', maxHeight: '90vh' } },
            content: { style: { padding: '0' } }
        }"
    >
        <div class="task-modal-content">
            <!-- Action Buttons Row -->
            <div v-if="currentTaskId" class="action-buttons-row">
                <Button
                    @click="showAddChecklist = true"
                    outlined
                    size="small"
                >
                    <FontAwesomeIcon icon="check-square" class="button-icon" />
                    <span>Checklist</span>
                </Button>
                <Button outlined size="small">
                    <FontAwesomeIcon icon="calendar" class="button-icon" />
                    <span>Date</span>
                </Button>
                <Button outlined size="small">
                    <FontAwesomeIcon icon="tag" class="button-icon" />
                    <span>Label</span>
                </Button>
            </div>

            <!-- Main Content Area -->
            <div class="task-main">
                <div class="form-field">
                    <label for="title">Title</label>
                    <InputText
                        id="title"
                        v-model="title"
                        @keyup.enter="saveTask"
                        autofocus
                    />
                </div>
                <div class="form-field">
                    <label for="description">Description</label>
                    <Textarea id="description" v-model="description" rows="4" />
                </div>

                <!-- Checklists Section -->
                <div v-if="currentTaskId && taskChecklists.length > 0" class="checklists-section">
                    <!-- Display existing checklists -->
                    <div v-for="checklist in taskChecklists" :key="checklist.id" class="checklist-wrapper">
                        <CheckList :checklist-id="checklist.id" />
                        <Button
                            label="Delete checklist"
                            text
                            severity="danger"
                            size="small"
                            @click="deleteChecklist(checklist.id)"
                            class="delete-checklist-btn"
                        > 
                            Delete checklist 
                            <FontAwesomeIcon icon="trash" class="button-icon" />
                        </Button>
                    </div>
                </div>

            </div>

            <!-- Add Checklist Popover -->
            <Popover
                v-model:visible="showAddChecklist"
                title="Add Checklist"
                width="300px"
            >
                <div class="checklist-form">
                    <label for="checklist-title">Title</label>
                    <InputText
                        id="checklist-title"
                        v-model="newChecklistTitle"
                        placeholder="Checklist"
                        @keyup.enter="addChecklist"
                        autofocus
                    />
                    <Button
                        label="Add"
                        @click="addChecklist"
                        :disabled="!newChecklistTitle.trim()"
                        class="add-button"
                    />
                </div>
            </Popover>

            <!-- Footer Actions -->
            <div class="task-modal-footer">
                <Button label="Cancel" text @click="handleClose" />
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
import { ref, watch, computed, type Ref } from "vue";
import Textarea from "primevue/textarea";
import { useTaskStore } from "@/stores/task";
import { useChecklistStore } from "@/stores/checklist";
import CheckList from "@/components/common/CheckList.vue";
import Popover from "@/components/common/Popover.vue";

const props = defineProps<{
    projectId: string;
}>();

const taskStore = useTaskStore();
const checklistStore = useChecklistStore();

const isLoading = ref(false);
const title = ref("");
const description: Ref<string | null> = ref(null);
const taskCompleted = ref(false);

// Checklist UI state
const showAddChecklist = ref(false);
const newChecklistTitle = ref("");

// Computed properties
const currentTaskId = computed(() => taskStore.getCurrentTask?.id || null);
const taskChecklists = computed(() => {
    if (!currentTaskId.value) return [];
    return checklistStore.getChecklistsByTask(currentTaskId.value);
});

// Watch for modal visibility changes and load task data
watch(
    () => taskStore.isTaskModalVisible,
    async (newVal) => {
        if (newVal) {
            const currentTask = taskStore.getCurrentTask;
            if (currentTask) {
                // Editing existing task
                title.value = currentTask.title;
                description.value = currentTask.description;
                taskCompleted.value = currentTask.completed;

                // Load checklists for this task
                await loadChecklists(currentTask.id);
            } else {
                // Creating new task
                resetForm();
            }
        } else {
            // Clear checklists when modal closes
            checklistStore.clearChecklists();
        }
    }
);

async function loadChecklists(taskId: string) {
    try {
        await checklistStore.loadChecklistsForTask(taskId);
        // Load details (items) for each checklist
        const checklists = checklistStore.getChecklistsByTask(taskId);
        await Promise.all(
            checklists.map(checklist => checklistStore.loadChecklistDetails(checklist.id))
        );
    } catch (error) {
        console.error("Failed to load checklists:", error);
    }
}

async function addChecklist() {
    if (!newChecklistTitle.value.trim() || !currentTaskId.value) return;

    try {
        const newChecklist = await checklistStore.createChecklist({
            task_id: currentTaskId.value,
            title: newChecklistTitle.value.trim()
        });
        // Load the checklist details to get items array
        await checklistStore.loadChecklistDetails(newChecklist.id);
        newChecklistTitle.value = "";
        showAddChecklist.value = false;
    } catch (error) {
        console.error("Failed to create checklist:", error);
    }
}

async function deleteChecklist(checklistId: string) {
    try {
        await checklistStore.deleteChecklist(checklistId);
    } catch (error) {
        console.error("Failed to delete checklist:", error);
    }
}

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

function handleClose() {
    taskStore.setTaskModalVisible(false);
    resetForm();
}

function resetForm() {
    title.value = "";
    description.value = "";
    taskCompleted.value = false;
    showAddChecklist.value = false;
    newChecklistTitle.value = "";
}
</script>

<style scoped>
.task-modal-content {
    display: flex;
    flex-direction: column;
    max-height: 80vh;
}

.action-buttons-row {
    display: flex;
    gap: 0.5rem;
    padding-left: 1.2rem;
    border-bottom: 1px solid var(--surface-border);
    background: var(--surface-0);
}

.task-main {
    flex: 1;
    padding: 1.5rem;
}

.form-field {
    display: flex;
    flex-direction: column;
    margin-bottom: 1.5rem;
}

.form-field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.section-header h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
}

.checklist-wrapper {
    background: var(--surface-50);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    position: relative;
}

.delete-checklist-btn {
    margin-top: 0.5rem;
}

/* Checklist Form (inside Popover) */
.checklist-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.checklist-form label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-color-secondary);
}

.checklist-form .add-button {
    width: 100%;
}

.button-group {
    display: flex;
    gap: 0.5rem;
}

.task-modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--surface-border);
    background: var(--surface-0);
}
</style>
