<template>
    <Dialog
        modal
        :visible="taskStore.isTaskModalVisible"
        @update:visible="taskStore.setTaskModalVisible($event)"
        :header="taskStore.getCurrentTask ? 'Edit Task' : 'New Task'"
        @hide="handleClose"
        :pt="{
            root: { style: { maxWidth: '95vw', maxHeight: '90vh' } },
            content: { style: { padding: '0' } }
        }"
    >
        <div class="task-modal-content">
            <!-- Action Buttons Row -->
            <div class="action-buttons-row">
                <Button
                    v-if="currentTaskId"
                    @click="showAddChecklist = true"
                    outlined
                    size="small"
                >
                    <FontAwesomeIcon icon="check-square" class="button-icon" />
                    <span>Checklist</span>
                </Button>
                <Select
                    v-model="priorityId"
                    :options="priorityStore.priorities"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Priority"
                    size="small"
                    showClear
                    variant="outlined"
                >
                    <template #option="slotProps">
                        <div class="priority-option">
                            <FontAwesomeIcon
                                icon="flag"
                                :style="{ color: slotProps.option.color }"
                            />
                            <span>{{ slotProps.option.name }}</span>
                        </div>
                    </template>
                    <template #value="slotProps">
                        <div class="priority-option">
                            <FontAwesomeIcon
                                icon="flag"
                                :style="{ color: selectedPriority?.color }"
                            />
                            <span>{{ slotProps.value ? selectedPriority?.name : 'Priority' }}</span>
                        </div>
                    </template>
                </Select>
                <DatePicker
                    v-model="dueDateTime"
                    placeholder="Due Date"
                    size="small"
                    showIcon
                    showClear
                    iconDisplay="input"
                    :showTime="true"
                    hourFormat="24"
                />
                <Button outlined size="small" @click="showRecurrencePicker = true">
                    <FontAwesomeIcon icon="repeat" class="button-icon" />
                    <span>{{ recurrenceButtonText }}</span>
                </Button>
                <Button outlined size="small" @click="showLabelPicker = true">
                    <FontAwesomeIcon icon="tag" class="button-icon" />
                    <span>{{ labelButtonText }}</span>
                </Button>
            </div>
            <div v-if="selectedLabels.length" class="selected-labels">
                <span
                    v-for="label in selectedLabels"
                    :key="label.id"
                    class="label-chip"
                >
                    <span class="label-chip-swatch" :style="{ backgroundColor: label.color }" />
                    {{ label.name }}
                </span>
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

            <!-- Label Picker Popover -->
            <Popover
                v-model:visible="showLabelPicker"
                title="Labels"
                width="360px"
            >
                <div class="label-picker">
                    <div v-if="labelStore.loading" class="label-picker-empty">
                        <FontAwesomeIcon icon="spinner" class="spinner" />
                        <span>Loading labels...</span>
                    </div>
                    <div v-else-if="!labelStore.sortedLabels.length" class="label-picker-empty">
                        <FontAwesomeIcon icon="tag" class="label-picker-icon" />
                        <span>No labels yet.</span>
                        <p>Use the Labels workspace in the sidebar to create one.</p>
                    </div>
                    <div v-else class="label-picker-list">
                        <label
                            v-for="label in labelStore.sortedLabels"
                            :key="label.id"
                            class="label-picker-item"
                            :for="`label-${label.id}`"
                        >
                            <Checkbox
                                :inputId="`label-${label.id}`"
                                v-model="selectedLabelIds"
                                :value="label.id"
                            />
                            <span class="label-picker-swatch" :style="{ backgroundColor: label.color }" />
                            <span class="label-picker-name">{{ label.name }}</span>
                            <span v-if="label.description" class="label-picker-description">
                                {{ label.description }}
                            </span>
                        </label>
                    </div>
                </div>
            </Popover>

            <!-- Recurrence Picker Popover -->
            <Popover
                v-model:visible="showRecurrencePicker"
                title="Recurring Task"
                width="360px"
            >
                <div class="recurrence-picker">
                    <div class="recurrence-field">
                        <label for="recurrence-frequency">Frequency</label>
                        <Select
                            id="recurrence-frequency"
                            v-model="recurrenceType"
                            :options="RECURRENCE_OPTIONS"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="Select frequency"
                            size="small"
                            showClear
                            variant="outlined"
                        />
                    </div>
                    <div
                        v-if="recurrenceType === 'weekly'"
                        class="recurrence-field"
                    >
                        <label>Days of the week</label>
                        <div class="weekday-selector">
                            <button
                                v-for="(dayLabel, dayIndex) in JS_WEEKDAY_LABELS"
                                :key="dayLabel"
                                type="button"
                                class="weekday-chip"
                                :class="{ active: recurrenceDaysOfWeek.includes(dayIndex) }"
                                @click="toggleWeekday(dayIndex)"
                            >
                                {{ dayLabel }}
                            </button>
                        </div>
                    </div>
                    <div class="recurrence-actions">
                        <Button text size="small" @click="clearRecurrence">Clear</Button>
                        <Button size="small" @click="showRecurrencePicker = false">Done</Button>
                    </div>
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
import { ref, watch, computed, type Ref, onMounted } from "vue";
import Textarea from "primevue/textarea";
import Select from "primevue/select";
import DatePicker from "primevue/datepicker";
import { useTaskStore } from "@/stores/task";
import { useChecklistStore } from "@/stores/checklist";
import { usePriorityStore } from "@/stores/priority";
import { useLabelStore } from "@/stores/label";
import CheckList from "@/components/common/CheckList.vue";
import Popover from "@/components/common/Popover.vue";
import { useToast } from "primevue";
import type { Label } from "@/models/label";
import type { TaskRecurrenceType } from "@/models/task";
import {
    jsDaysToPythonDays,
    pythonDaysToJsDays,
    JS_WEEKDAY_LABELS
} from "@/utils/recurrenceUtils";

const toast = useToast();

const props = defineProps<{
    projectId: string;
}>();

const taskStore = useTaskStore();
const checklistStore = useChecklistStore();
const priorityStore = usePriorityStore();
const labelStore = useLabelStore();

const isLoading = ref(false);
const title = ref("");
const description: Ref<string | null> = ref(null);
const taskCompleted = ref(false);
const priorityId: Ref<string | null> = ref(null);
const dueDateTimeString: Ref<string | null> = ref(null);

// UI state for popovers
const showAddChecklist = ref(false);
const newChecklistTitle = ref("");
const showLabelPicker = ref(false);
const selectedLabelIds = ref<string[]>([]);
const showRecurrencePicker = ref(false);

// Recurrence state (stored directly on task now)
const recurrenceType = ref<TaskRecurrenceType | null>(null);
const recurrenceDaysOfWeek = ref<number[]>([]); // JS convention: 0=Sunday

const RECURRENCE_OPTIONS: { label: string; value: TaskRecurrenceType }[] = [
    { label: "Daily", value: "daily" },
    { label: "Every Other Day", value: "alternate_days" },
    { label: "Specific Days", value: "weekly" },
];

// Computed properties for display
const selectedPriority = computed(() => {
    if (!priorityId.value) return null;
    return priorityStore.getPriorityById(priorityId.value);
});

// Convert between Date object (for DatePicker) and ISO string (for backend)
const dueDateTime = computed({
    get: () => {
        if (!dueDateTimeString.value) return null;
        return new Date(dueDateTimeString.value);
    },
    set: (value: Date | null) => {
        dueDateTimeString.value = value ? value.toISOString() : null;
    }
});

// Computed properties
const currentTaskId = computed(() => taskStore.getCurrentTask?.id || null);
const taskChecklists = computed(() => {
    if (!currentTaskId.value) return [];
    return checklistStore.getChecklistsByTask(currentTaskId.value);
});

const selectedLabels = computed<Label[]>(() => {
    return selectedLabelIds.value
        .map(id => labelStore.getLabelById(id))
        .filter((label): label is Label => Boolean(label));
});

const labelButtonText = computed(() => {
    const count = selectedLabelIds.value.length;
    if (count === 0) return "Label";
    if (count === 1) return selectedLabels.value[0]?.name ?? "Label";
    return `${count} Labels`;
});

const recurrenceButtonText = computed(() => {
    if (!recurrenceType.value) {
        return "Repeat";
    }

    if (recurrenceType.value === "daily") {
        return "Daily";
    }

    if (recurrenceType.value === "alternate_days") {
        return "Every Other Day";
    }

    if (recurrenceType.value === "weekly") {
        const selectedDays = recurrenceDaysOfWeek.value
            .sort((a, b) => a - b)
            .map(day => JS_WEEKDAY_LABELS[day]);
        const daysLabel = selectedDays.length ? selectedDays.join(" ") : "Days";
        return `Weekly · ${daysLabel}`;
    }

    return "Repeat";
});

// Watch for modal visibility changes and load task data
watch(
    () => taskStore.isTaskModalVisible,
    async (newVal) => {
        if (newVal) {
            const currentTask = taskStore.getCurrentTask;
            if (!labelStore.labels.length) {
                try {
                    await labelStore.loadLabels();
                } catch (error) {
                    toast.add({ severity: "error", summary: "Error", detail: "Failed to load labels" });
                }
            }
            if (currentTask) {
                // Editing existing task
                title.value = currentTask.title;
                description.value = currentTask.description;
                taskCompleted.value = currentTask.completed;
                priorityId.value = currentTask.priority_id;
                dueDateTimeString.value = currentTask.due_datetime;
                selectedLabelIds.value =
                    currentTask.label_ids?.slice() ??
                    (currentTask.labels ? currentTask.labels.map(label => label.id) : []);

                // Load recurrence from task fields (convert Python days to JS convention)
                if (currentTask.recurrence_type) {
                    const recurrence = currentTask.recurrence_type as TaskRecurrenceType;
                    recurrenceType.value = recurrence;
                    if (recurrence === "weekly" && currentTask.recurrence_days) {
                        recurrenceDaysOfWeek.value = pythonDaysToJsDays(currentTask.recurrence_days);
                    } else {
                        recurrenceDaysOfWeek.value = [];
                    }
                } else {
                    resetRecurrence();
                }

                await loadChecklists(currentTask.id);
            } else {
                // Creating new task
                resetForm();
            }
        } else {
            // Clear checklists when modal closes
            checklistStore.clearChecklists();
            showLabelPicker.value = false;
            showRecurrencePicker.value = false;
            resetForm();
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
        toast.add({ severity: "error", summary: "Error", detail: "Failed to load checklists" });
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
        toast.add({ severity: "error", summary: "Error", detail: "Failed to create checklist" });
    }
}

function toggleWeekday(dayIndex: number) {
    if (recurrenceDaysOfWeek.value.includes(dayIndex)) {
        recurrenceDaysOfWeek.value = recurrenceDaysOfWeek.value.filter(day => day !== dayIndex);
    } else {
        recurrenceDaysOfWeek.value = [...recurrenceDaysOfWeek.value, dayIndex].sort((a, b) => a - b);
    }
}

function resetRecurrence() {
    recurrenceType.value = null;
    recurrenceDaysOfWeek.value = [];
}

function clearRecurrence() {
    resetRecurrence();
    showRecurrencePicker.value = false;
}

function getRecurrencePayload(): { type: TaskRecurrenceType | null; days: number[] | null } {
    if (!recurrenceType.value) {
        return { type: null, days: null };
    }

    if (recurrenceType.value === "weekly") {
        if (!recurrenceDaysOfWeek.value.length) {
            throw new Error("Select at least one day for weekly recurrence.");
        }
        // Convert from JS convention (0=Sunday) to Python convention (0=Monday)
        return {
            type: recurrenceType.value,
            days: jsDaysToPythonDays(recurrenceDaysOfWeek.value),
        };
    }

    return {
        type: recurrenceType.value,
        days: null,
    };
}

async function saveTask() {
    if (title.value.trim() === "") return;

    let recurrencePayload: { type: TaskRecurrenceType | null; days: number[] | null };
    try {
        recurrencePayload = getRecurrencePayload();
    } catch (validationError) {
        const detail =
            validationError instanceof Error
                ? validationError.message
                : "Invalid recurrence configuration.";
        toast.add({ severity: "warn", summary: "Recurring Task", detail });
        return;
    }

    const currentTask = taskStore.getCurrentTask;
    const sectionIdForCreate = currentTask
        ? currentTask.section_id
        : taskStore.currentSectionId;

    if (!currentTask && !sectionIdForCreate) {
        toast.add({
            severity: "warn",
            summary: "Task",
            detail: "Select a section before creating a task."
        });
        return;
    }

    isLoading.value = true;

    try {
        if (currentTask) {
            await taskStore.updateTask(currentTask.id, {
                title: title.value,
                description: description.value,
                completed: taskCompleted.value,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                label_ids: selectedLabelIds.value,
                recurrence_type: recurrencePayload.type,
                recurrence_days: recurrencePayload.days,
            });
        } else {
            await taskStore.createTask({
                project_id: props.projectId,
                section_id: sectionIdForCreate as string,
                title: title.value,
                description: description.value,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                label_ids: selectedLabelIds.value,
                recurrence_type: recurrencePayload.type,
                recurrence_days: recurrencePayload.days,
            });
        }

        taskStore.setTaskModalVisible(false);
    } catch (error) {
        const detail = error instanceof Error ? error.message : "Failed to save task";
        toast.add({ severity: "error", summary: "Error", detail });
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
    priorityId.value = null;
    dueDateTimeString.value = null;
    showAddChecklist.value = false;
    newChecklistTitle.value = "";
    selectedLabelIds.value = [];
    showLabelPicker.value = false;
    showRecurrencePicker.value = false;
    resetRecurrence();
}

onMounted(async () => {
    if (priorityStore.priorities.length === 0) {
        await priorityStore.loadPriorities();
    }
    if (labelStore.labels.length === 0) {
        try {
            await labelStore.loadLabels();
        } catch (error) {
            toast.add({ severity: "error", summary: "Error", detail: "Failed to load labels" });
        }
    }
});
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
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--p-gray-200);
}

.task-main {
    flex: 1;
    padding: 1rem 1.5rem;
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
    background: var(--p-content-hover-background);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    position: relative;
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
    color: var(--p-text-color);
}

.checklist-form .add-button {
    width: 100%;
}

.button-group {
    display: flex;
    gap: 0.5rem;
}

.selected-labels {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding: 0 1.5rem 0.5rem;
}

.label-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    background-color: var(--p-content-hover-background);
    color: var(--p-text-color);
    font-size: 0.8125rem;
}

.label-chip-swatch {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    border: 1px solid rgba(0, 0, 0, 0.2);
}

.task-modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--p-gray-200);
}

/* Priority picker styles */
.priority-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.label-picker {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.label-picker-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.label-picker-item {
    display: grid;
    grid-template-columns: auto 24px 1fr;
    gap: 0.75rem;
    align-items: center;
    font-size: 0.95rem;
}

.label-picker-swatch {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.12);
}

.label-picker-name {
    font-weight: 600;
    color: var(--p-text-color);
}

.label-picker-description {
    grid-column: 2 / span 2;
    font-size: 0.8125rem;
    color: var(--p-text-muted-color);
}

.label-picker-empty {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
    text-align: center;
    color: var(--p-text-muted-color);
}

.label-picker-empty .spinner {
    font-size: 1.5rem;
    animation: spin 1s linear infinite;
}

.label-picker-icon {
    font-size: 1.5rem;
    color: var(--p-primary-color);
}

/* Match Select styling with outlined buttons */
.action-buttons-row :deep(.p-select) {
    border-color: var(--p-button-outlined-primary-border-color);
    background: transparent;
}

.action-buttons-row :deep(.p-select .p-select-label),
.action-buttons-row :deep(.p-select .p-placeholder) {
    color: var(--p-button-outlined-primary-color);
}

.action-buttons-row :deep(.p-select:hover) {
    border-color: var(--p-button-outlined-primary-border-color);
    background: var(--p-button-outlined-primary-hover-background);
}

.action-buttons-row :deep(.p-select:hover .p-select-label),
.action-buttons-row :deep(.p-select:hover .p-placeholder) {
    color: var(--p-button-outlined-primary-color);
}

/* Match DatePicker styling with outlined buttons */
.action-buttons-row :deep(.p-datepicker) {
    border-color: var(--p-button-outlined-primary-border-color);
    background: transparent;
}

.action-buttons-row :deep(.p-datepicker .p-inputtext),
.action-buttons-row :deep(.p-datepicker input) {
    color: var(--p-button-outlined-primary-color);
    border-color: var(--p-button-outlined-primary-border-color);
    background: transparent;
}

.action-buttons-row :deep(.p-datepicker input::placeholder) {
    color: var(--p-button-outlined-primary-color);
    opacity: 1;
}

.action-buttons-row :deep(.p-datepicker:hover) {
    border-color: var(--p-button-outlined-primary-border-color);
    background: var(--p-button-outlined-primary-hover-background);
}

.button-icon {
    margin-right: 0.4rem;
}

.recurrence-picker {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.recurrence-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.recurrence-field label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--p-text-color);
}

.weekday-selector {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.4rem;
}

.weekday-chip {
    padding: 0.4rem 0;
    border-radius: 6px;
    border: 1px solid var(--p-content-border-color);
    background: var(--p-content-hover-background);
    color: var(--p-text-color);
    font-size: 0.8125rem;
    text-align: center;
    cursor: pointer;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.weekday-chip:hover {
    border-color: var(--p-primary-color);
}

.weekday-chip.active {
    background: var(--p-primary-color);
    color: #fff;
    border-color: var(--p-primary-color);
}

.recurrence-time-input {
    padding: 0.5rem;
    border-radius: 6px;
    border: 1px solid var(--p-content-border-color);
    background: var(--p-content-background);
    color: var(--p-text-color);
}

.recurrence-time-input:focus {
    outline: none;
    border-color: var(--p-primary-color);
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.03);
}

.recurrence-actions {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    padding-top: 0.5rem;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
</style>
