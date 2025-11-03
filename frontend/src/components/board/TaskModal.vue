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
                    <div class="recurrence-field">
                        <label for="recurrence-time">Time of day</label>
                        <input
                            id="recurrence-time"
                            v-model="recurrenceTime"
                            type="time"
                            class="recurrence-time-input"
                            step="60"
                        />
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
import { useRecurringTaskStore } from "@/stores/recurringTask";
import CheckList from "@/components/common/CheckList.vue";
import Popover from "@/components/common/Popover.vue";
import { useToast } from "primevue";
import type { Label } from "@/models/label";
import type { RecurringTaskCreateInput, RecurringTaskUpdateInput } from "@/models/recurringTask";
import type { Task, TaskRecurrence, TaskRecurrenceType } from "@/models/task";
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
const recurringTaskStore = useRecurringTaskStore();

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
const existingRecurringTaskId = ref<string | null>(null);

const recurrenceType = ref<TaskRecurrenceType | null>(null);
const recurrenceTime = ref<string | null>(null);
const recurrenceDaysOfWeek = ref<number[]>([]);

const RECURRENCE_OPTIONS: { label: string; value: TaskRecurrenceType }[] = [
    { label: "Daily", value: "daily" },
    { label: "Every Other Day", value: "alternate_days" },
    { label: "Specific Days", value: "weekly" },
];

function getRecurrenceFromTemplate(templateId: string | null): TaskRecurrence | null {
    if (!templateId) return null;
    const template = recurringTaskStore.getRecurringTaskById(templateId);
    if (!template) return null;

    const recurrence: TaskRecurrence = {
        type: template.recurrence_type,
        time: template.recurrence_time,
    };

    // Convert from backend Python convention (0=Monday) to frontend JS convention (0=Sunday)
    if (template.recurrence_type === "weekly") {
        const days = template.recurrence_days && template.recurrence_days.length
            ? pythonDaysToJsDays(template.recurrence_days)
            : [];
        recurrence.days_of_week = days;
    } else if (template.recurrence_days && template.recurrence_days.length) {
        recurrence.days_of_week = pythonDaysToJsDays(template.recurrence_days);
    }

    return recurrence;
}

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

    const timeDisplay = recurrenceTime.value ? ` · ${recurrenceTime.value}` : "";

    if (recurrenceType.value === "daily") {
        return `Daily${timeDisplay}`;
    }

    if (recurrenceType.value === "alternate_days") {
        return `Every Other Day${timeDisplay}`;
    }

    if (recurrenceType.value === "weekly") {
        const selectedDays = recurrenceDaysOfWeek.value
            .sort((a, b) => a - b)
            .map(day => JS_WEEKDAY_LABELS[day]);
        const daysLabel = selectedDays.length ? selectedDays.join(" ") : "Days";
        return `Weekly · ${daysLabel}${timeDisplay}`;
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

                existingRecurringTaskId.value = currentTask.recurring_task_id ?? null;
                const recurrenceSource = currentTask.recurrence ?? getRecurrenceFromTemplate(existingRecurringTaskId.value);
                setRecurrenceState(recurrenceSource);
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

function setRecurrenceState(recurrence: TaskRecurrence | null) {
    if (recurrence) {
        recurrenceType.value = recurrence.type;
        recurrenceTime.value = recurrence.time ?? null;
        recurrenceDaysOfWeek.value = recurrence.days_of_week ? [...recurrence.days_of_week] : [];
    } else {
        resetRecurrence();
    }
}

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
    recurrenceTime.value = null;
    recurrenceDaysOfWeek.value = [];
}

function clearRecurrence() {
    resetRecurrence();
    showRecurrencePicker.value = false;
}

function getRecurrencePayload(): TaskRecurrence | null {
    if (!recurrenceType.value) {
        return null;
    }

    if (!recurrenceTime.value) {
        throw new Error("Select a time for the recurrence.");
    }

    if (recurrenceType.value === "weekly") {
        if (!recurrenceDaysOfWeek.value.length) {
            throw new Error("Select at least one day for weekly recurrence.");
        }

        return {
            type: recurrenceType.value,
            time: recurrenceTime.value,
            days_of_week: [...recurrenceDaysOfWeek.value].sort((a, b) => a - b),
        };
    }

    return {
        type: recurrenceType.value,
        time: recurrenceTime.value,
    };
}

function computeStartDate(): string {
    const source = dueDateTimeString.value ? new Date(dueDateTimeString.value) : new Date();
    return source.toISOString().split("T")[0];
}

function getLabelIdsPayload(): string[] | null {
    return selectedLabelIds.value.length ? [...selectedLabelIds.value] : null;
}

function buildRecurringTaskCreatePayload(task: Task, recurrence: TaskRecurrence): RecurringTaskCreateInput {
    // Convert from JS convention (0=Sunday) to Python convention (0=Monday) for backend
    const recurrenceDays =
        recurrence.type === "weekly" && recurrence.days_of_week
            ? jsDaysToPythonDays(recurrence.days_of_week)
            : null;

    return {
        title: title.value.trim(),
        description: description.value,
        project_id: task.project_id,
        section_id: task.section_id,
        priority_id: priorityId.value ?? null,
        label_ids: getLabelIdsPayload(),
        recurrence_type: recurrence.type,
        recurrence_days: recurrenceDays,
        recurrence_time: recurrence.time,
        start_date: computeStartDate(),
        end_date: null,
        is_active: true,
    };
}

function buildRecurringTaskUpdatePayload(recurrence: TaskRecurrence): RecurringTaskUpdateInput {
    // Convert from JS convention (0=Sunday) to Python convention (0=Monday) for backend
    const recurrenceDays =
        recurrence.type === "weekly" && recurrence.days_of_week
            ? jsDaysToPythonDays(recurrence.days_of_week)
            : null;

    const payload: RecurringTaskUpdateInput = {
        title: title.value.trim(),
        description: description.value,
        priority_id: priorityId.value ?? null,
        label_ids: getLabelIdsPayload(),
        recurrence_type: recurrence.type,
        recurrence_days: recurrenceDays,
        recurrence_time: recurrence.time,
    };

    if (dueDateTimeString.value) {
        payload.start_date = computeStartDate();
    }

    return payload;
}

async function syncRecurringTemplate(task: Task, recurrence: TaskRecurrence | null) {
    const targetTask = taskStore.getTaskById(task.id) ?? task;

    try {
        if (!recurrence) {
            if (existingRecurringTaskId.value) {
                await recurringTaskStore.deleteRecurringTask(existingRecurringTaskId.value);
                existingRecurringTaskId.value = null;
            }
            taskStore.setTaskRecurrence(task.id, null, null);
            return;
        }

        if (existingRecurringTaskId.value) {
            const updatePayload = buildRecurringTaskUpdatePayload(recurrence);
            await recurringTaskStore.updateRecurringTask(
                existingRecurringTaskId.value,
                updatePayload
            );
            taskStore.setTaskRecurrence(task.id, recurrence, existingRecurringTaskId.value);
        } else {
            const createPayload = buildRecurringTaskCreatePayload(targetTask, recurrence);
            const created = await recurringTaskStore.createRecurringTask(createPayload);
            existingRecurringTaskId.value = created.id;
            taskStore.setTaskRecurrence(task.id, recurrence, created.id);
        }
    } catch (error) {
        throw error instanceof Error ? error : new Error("Failed to synchronize recurring task");
    }
}

async function saveTask() {
    if (title.value.trim() === "") return;

    let recurrencePayload: TaskRecurrence | null;
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
        let savedTask: Task;

        if (currentTask) {
            savedTask = await taskStore.updateTask(currentTask.id, {
                title: title.value,
                description: description.value,
                completed: taskCompleted.value,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                label_ids: selectedLabelIds.value,
            });
        } else {
            savedTask = await taskStore.createTask({
                project_id: props.projectId,
                section_id: sectionIdForCreate as string,
                title: title.value,
                description: description.value,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                label_ids: selectedLabelIds.value,
            });
        }

        await syncRecurringTemplate(savedTask, recurrencePayload);

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
    existingRecurringTaskId.value = null;
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
