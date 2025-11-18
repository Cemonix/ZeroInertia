<template>
    <Dialog
        modal
        :visible="taskStore.isTaskModalVisible"
        @update:visible="taskStore.setTaskModalVisible($event)"
        :header="taskStore.getCurrentTask ? 'Edit Task' : 'New Task'"
        @hide="handleClose"
        :pt="{
            root: {
                style: { maxWidth: '95vw', maxHeight: '90vh' },
                class: 'task-modal-dialog',
            },
            content: { style: { padding: '0' } },
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
                            <span>{{
                                slotProps.value
                                    ? selectedPriority?.name
                                    : "Priority"
                            }}</span>
                        </div>
                    </template>
                </Select>
                <DateTimePicker v-model="dueDateTimeString" v-model:duration="durationMinutes" />
                <Button
                    outlined
                    size="small"
                    @click="showReminderPicker = true"
                    :disabled="!dueDateTimeString"
                    :title="!dueDateTimeString ? 'Set a due date first' : ''"
                >
                    <FontAwesomeIcon icon="bell" class="button-icon" />
                    <span>{{ reminderButtonText }}</span>
                </Button>
                <Button
                    outlined
                    size="small"
                    @click="showRecurrencePicker = true"
                    :disabled="!dueDateTimeString"
                    :title="!dueDateTimeString ? 'Set a due date first' : ''"
                >
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
                    <span
                        class="label-chip-swatch"
                        :style="{ backgroundColor: label.color }"
                    />
                    {{ label.name }}
                </span>
            </div>

            <!-- Main Content Area -->
            <div class="task-main">
                <TaskForm
                    v-model:title="title"
                    v-model:description="description"
                    v-model:project-id="selectedProjectId"
                    v-model:section-id="selectedSectionId"
                    :detected-date-text="detectedDateText"
                    :loading="isLoading"
                    @clear-detected-date="clearDetectedDate"
                    @save="saveTask"
                />

                <!-- Checklists Section -->
                <div
                    v-if="currentTaskId && taskChecklists.length > 0"
                    class="checklists-section"
                >
                    <!-- Display existing checklists -->
                    <div
                        v-for="checklist in taskChecklists"
                        :key="checklist.id"
                        class="checklist-wrapper"
                    >
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
                <LabelPicker
                    :labels="labelStore.sortedLabels"
                    :loading="labelStore.loading"
                    v-model:selected-ids="selectedLabelIds"
                />
            </Popover>

            <!-- Recurrence Picker Popover -->
            <Popover
                v-model:visible="showRecurrencePicker"
                title="Recurring Task"
                width="500px"
            >
                <RecurrencePicker
                    :interval="recurrenceInterval"
                    :unit="recurrenceUnit"
                    :days="recurrenceDays"
                    @update:interval="recurrenceInterval = $event"
                    @update:unit="recurrenceUnit = $event"
                    @update:days="recurrenceDays = $event"
                    @close="showRecurrencePicker = false"
                />
            </Popover>

            <!-- Reminder Picker Popover -->
            <Popover
                v-model:visible="showReminderPicker"
                title="Reminder"
                width="360px"
            >
                <ReminderPicker
                    :minutes="reminderMinutes"
                    @update:minutes="reminderMinutes = $event"
                    @close="showReminderPicker = false"
                />
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
import { ref, watch, computed, type Ref, onMounted, onBeforeUnmount } from "vue";
import Select from "primevue/select";
import DateTimePicker from "@/components/pickers/DateTimePicker.vue";
import { useTaskStore } from "@/stores/task";
import { useChecklistStore } from "@/stores/checklist";
import { usePriorityStore } from "@/stores/priority";
import { useLabelStore } from "@/stores/label";
import { useProjectStore } from "@/stores/project";
import { useSectionStore } from "@/stores/section";
import CheckList from "@/components/common/CheckList.vue";
import Popover from "@/components/common/Popover.vue";
import RecurrencePicker from "@/components/pickers/RecurrencePicker.vue";
import ReminderPicker from "@/components/pickers/ReminderPicker.vue";
import LabelPicker from "@/components/pickers/LabelPicker.vue";
import TaskForm from "@/components/tasks/TaskForm.vue";
import { useToast } from "primevue";
import type { Label } from "@/models/label";
import type { Task, TaskRecurrenceUnit } from "@/models/task";
import { formatRecurrence } from "@/utils/recurrenceUtils";
import { useNaturalLanguageParsing } from "@/composables/useNaturalLanguageParsing";

const toast = useToast();

const props = defineProps<{
    projectId: string;
}>();

const taskStore = useTaskStore();
const checklistStore = useChecklistStore();
const priorityStore = usePriorityStore();
const labelStore = useLabelStore();
const projectStore = useProjectStore();
const sectionStore = useSectionStore();

const isLoading = ref(false);
const title = ref("");
const description: Ref<string | null> = ref(null);
const taskCompleted = ref(false);
const priorityId: Ref<string | null> = ref(null);
const dueDateTimeString: Ref<string | null> = ref(null);
const durationMinutes: Ref<number | null> = ref(null);

// Project and Section selection
const selectedProjectId: Ref<string | null> = ref(null);
const selectedSectionId: Ref<string | null> = ref(null);

// UI state for popovers
const showAddChecklist = ref(false);
const newChecklistTitle = ref("");
const showLabelPicker = ref(false);
const selectedLabelIds = ref<string[]>([]);
const showRecurrencePicker = ref(false);
const showReminderPicker = ref(false);

// Recurrence state
const recurrenceInterval = ref<number | null>(null);
const recurrenceUnit = ref<TaskRecurrenceUnit | null>(null);
const recurrenceDays = ref<number[] | null>(null); // Python convention: 0=Mon, 6=Sun

// Reminder state
const reminderMinutes = ref<number | null>(null);

// Natural language parsing state
const detectedDateText = ref<string>("");
const cleanedTitleBeforeSave = ref<string>(""); // Store cleaned title for saving
const { parseTaskDate } = useNaturalLanguageParsing();
let parseTimeout: ReturnType<typeof setTimeout> | null = null;

// Watch title and parse natural language dates with @ trigger
watch(title, (newTitle) => {
    // Clear previous timeout
    if (parseTimeout) {
        clearTimeout(parseTimeout);
    }

    // Debounce parsing by 300ms to avoid parsing on every keystroke
    parseTimeout = setTimeout(() => {
        if (!newTitle || newTitle.trim() === '') {
            detectedDateText.value = '';
            dueDateTimeString.value = null;
            cleanedTitleBeforeSave.value = '';
            return;
        }

        // Only parse if there's an @ symbol (manual trigger)
        const atIndex = newTitle.lastIndexOf('@');
        if (atIndex === -1) {
            // No @ found - clear any previous detection
            detectedDateText.value = '';
            cleanedTitleBeforeSave.value = '';
            return;
        }

        // Extract the part after @ for parsing
        const beforeAt = newTitle.substring(0, atIndex).trim();
        const afterAt = newTitle.substring(atIndex + 1).trim();

        if (!afterAt) {
            // @ exists but nothing after it yet
            detectedDateText.value = '';
            cleanedTitleBeforeSave.value = '';
            return;
        }

        // Parse the text after @
        const result = parseTaskDate(afterAt);

        if (result.date && result.matchedText) {
            // Date detected - show the hint and update due date
            // DON'T modify the title yet - wait until save
            detectedDateText.value = result.matchedText + (result.matchedDurationText ? ` ${result.matchedDurationText}` : '');
            dueDateTimeString.value = result.date.toISOString();
            cleanedTitleBeforeSave.value = beforeAt; // Store for later use
            // Also set duration (if parsed) and clamp to 24h max
            if (typeof result.durationMinutes === 'number') {
                const max = 24 * 60;
                durationMinutes.value = Math.max(0, Math.min(max, result.durationMinutes));
            }
        } else {
            // No valid date found after @
            detectedDateText.value = '';
            cleanedTitleBeforeSave.value = '';
        }
    }, 300);
});

// Clear detected date manually
function clearDetectedDate() {
    detectedDateText.value = '';
    dueDateTimeString.value = null;
    cleanedTitleBeforeSave.value = '';
    durationMinutes.value = null;
}

// Cleanup timeout on unmount to prevent memory leak
onBeforeUnmount(() => {
    if (parseTimeout) {
        clearTimeout(parseTimeout);
    }
});

// Computed properties for display
const selectedPriority = computed(() => {
    if (!priorityId.value) return null;
    return priorityStore.getPriorityById(priorityId.value);
});

// DateTime composition handled inside DateTimePicker

// Computed properties
const currentTaskId = computed(() => taskStore.getCurrentTask?.id || null);
const taskChecklists = computed(() => {
    if (!currentTaskId.value) return [];
    return checklistStore.getChecklistsByTask(currentTaskId.value);
});

const selectedLabels = computed<Label[]>(() => {
    return selectedLabelIds.value
        .map((id) => labelStore.getLabelById(id))
        .filter((label): label is Label => Boolean(label));
});

const labelButtonText = computed(() => {
    const count = selectedLabelIds.value.length;
    if (count === 0) return "Label";
    if (count === 1) return selectedLabels.value[0]?.name ?? "Label";
    return `${count} Labels`;
});

const recurrenceButtonText = computed(() => {
    const formatted = formatRecurrence(
        recurrenceInterval.value,
        recurrenceUnit.value,
        recurrenceDays.value
    );
    return formatted || "Repeat";
});

const reminderButtonText = computed(() => {
    if (reminderMinutes.value === null) {
        return "Reminder";
    }

    const minutes = reminderMinutes.value;
    if (minutes === 0) return "At time";
    if (minutes < 60) return `${minutes}m before`;
    if (minutes < 1440) return `${minutes / 60}h before`;
    return `${minutes / 1440}d before`;
});

function loadTaskData(task: Task) {
    title.value = task.title;
    description.value = task.description;
    taskCompleted.value = task.completed;
    priorityId.value = task.priority_id;
    dueDateTimeString.value = task.due_datetime;
    durationMinutes.value = task.duration_minutes ?? null;
    selectedLabelIds.value =
        task.label_ids?.slice() ??
        (task.labels ? task.labels.map((label) => label.id) : []);

    // Load project and section
    selectedProjectId.value = task.project_id;
    selectedSectionId.value = task.section_id;

    // Load recurrence from task fields
    recurrenceInterval.value = task.recurrence_interval;
    recurrenceUnit.value = task.recurrence_unit;
    recurrenceDays.value = task.recurrence_days;

    // Load reminder
    reminderMinutes.value = task.reminder_minutes ?? null;
}

function applyInitialValues() {
    const initialValues = taskStore.initialTaskValues;
    if (!initialValues) {
        // No initial values from store, use props for project/section
        if (props.projectId) {
            selectedProjectId.value = props.projectId;
        }
        if (taskStore.currentSectionId) {
            selectedSectionId.value = taskStore.currentSectionId;
        }
        return;
    }

    if (initialValues.due_datetime) {
        dueDateTimeString.value = initialValues.due_datetime;
    }
    if (initialValues.duration_minutes !== undefined) {
        durationMinutes.value = initialValues.duration_minutes;
    }
    if (initialValues.title) {
        title.value = initialValues.title;
    }
    if (initialValues.description) {
        description.value = initialValues.description;
    }
    if (initialValues.priority_id) {
        priorityId.value = initialValues.priority_id;
    }
    if (initialValues.label_ids) {
        selectedLabelIds.value = initialValues.label_ids.slice();
    }
    // Apply project and section from initial values if provided
    if (initialValues.project_id !== undefined) {
        selectedProjectId.value = initialValues.project_id;
    } else if (props.projectId) {
        selectedProjectId.value = props.projectId;
    }
    if (initialValues.section_id !== undefined) {
        selectedSectionId.value = initialValues.section_id;
    } else if (taskStore.currentSectionId) {
        selectedSectionId.value = taskStore.currentSectionId;
    }
}

async function handleModalOpen() {
    // Load labels if not already loaded
    if (!labelStore.labels.length) {
        try {
            await labelStore.loadLabels();
        } catch (error) {
            toast.add({
                severity: "error",
                summary: "Error",
                detail: "Failed to load labels",
            });
        }
    }

    // Load projects if not already loaded
    if (!projectStore.projects.length) {
        try {
            await projectStore.loadProjects();
        } catch (error) {
            toast.add({
                severity: "error",
                summary: "Error",
                detail: "Failed to load projects",
            });
        }
    }

    const currentTask = taskStore.getCurrentTask;
    if (currentTask) {
        // Editing existing task
        loadTaskData(currentTask);
        await loadChecklists(currentTask.id);

        // Load sections for the task's project
        if (currentTask.project_id) {
            try {
                await sectionStore.loadSectionsForProject(currentTask.project_id);
            } catch (error) {
                // Silently fail - sections are optional
            }
        }
    } else {
        // Creating new task
        resetForm();
        applyInitialValues();

        // Load sections for the pre-selected project if any
        const projectId = props.projectId || selectedProjectId.value;
        if (projectId) {
            try {
                await sectionStore.loadSectionsForProject(projectId);
            } catch (error) {
                // Silently fail - sections are optional
            }
        }
    }
}

function handleModalClose() {
    showLabelPicker.value = false;
    showRecurrencePicker.value = false;
    showReminderPicker.value = false;
    resetForm();
}

watch(
    () => taskStore.isTaskModalVisible,
    async (isVisible) => {
        if (isVisible) {
            await handleModalOpen();
        } else {
            handleModalClose();
        }
    }
);

watch(
    () => dueDateTimeString.value,
    (newValue) => {
        if (!newValue) {
            reminderMinutes.value = null;
            recurrenceInterval.value = null;
            recurrenceUnit.value = null;
            recurrenceDays.value = null;
        }
    }
);

// Watch selected project to load sections
watch(
    () => selectedProjectId.value,
    async (newProjectId) => {
        if (newProjectId) {
            try {
                await sectionStore.loadSectionsForProject(newProjectId);
            } catch (error) {
                // Silently fail - sections are optional
            }
        }
    }
);

async function loadChecklists(taskId: string) {
    try {
        await checklistStore.loadChecklistsForTask(taskId);
        // Load details (items) for each checklist
        const checklists = checklistStore.getChecklistsByTask(taskId);
        await Promise.all(
            checklists.map((checklist) =>
                checklistStore.loadChecklistDetails(checklist.id)
            )
        );
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to load checklists",
        });
    }
}

async function addChecklist() {
    if (!newChecklistTitle.value.trim() || !currentTaskId.value) return;

    try {
        const newChecklist = await checklistStore.createChecklist({
            task_id: currentTaskId.value,
            title: newChecklistTitle.value.trim(),
        });
        // Load the checklist details to get items array
        await checklistStore.loadChecklistDetails(newChecklist.id);
        newChecklistTitle.value = "";
        showAddChecklist.value = false;
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Error",
            detail: "Failed to create checklist",
        });
    }
}

async function saveTask() {
    if (title.value.trim() === "") return;

    // Use cleaned title if date was detected, otherwise use original title
    const finalTitle = cleanedTitleBeforeSave.value || title.value;

    // Validate weekly recurrence has at least one day selected
    if (recurrenceUnit.value === "weeks" && recurrenceInterval.value && (!recurrenceDays.value || recurrenceDays.value.length === 0)) {
        toast.add({
            severity: "warn",
            summary: "Recurring Task",
            detail: "Select at least one day for weekly recurrence."
        });
        return;
    }

    const currentTask = taskStore.getCurrentTask;

    isLoading.value = true;

    try {
        if (currentTask) {
            await taskStore.updateTask(currentTask.id, {
                title: finalTitle,
                description: description.value,
                completed: taskCompleted.value,
                project_id: selectedProjectId.value ?? undefined,
                section_id: selectedSectionId.value ?? undefined,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                duration_minutes: durationMinutes.value,
                label_ids: selectedLabelIds.value,
                recurrence_interval: recurrenceInterval.value,
                recurrence_unit: recurrenceUnit.value,
                recurrence_days: recurrenceDays.value,
                reminder_minutes: reminderMinutes.value,
            });
            toast.add({
                severity: "success",
                summary: "Task updated",
                detail: `"${finalTitle}" has been updated.`,
                life: 3000,
            });
        } else {
            await taskStore.createTask({
                project_id: selectedProjectId.value,
                section_id: selectedSectionId.value,
                title: finalTitle,
                description: description.value,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                duration_minutes: durationMinutes.value,
                label_ids: selectedLabelIds.value,
                recurrence_interval: recurrenceInterval.value,
                recurrence_unit: recurrenceUnit.value,
                recurrence_days: recurrenceDays.value,
                reminder_minutes: reminderMinutes.value,
            });
            toast.add({
                severity: "success",
                summary: "Task created",
                detail: `"${finalTitle}" has been added.`,
                life: 3000,
            });
        }

        taskStore.setTaskModalVisible(false);
    } catch (error) {
        const detail =
            error instanceof Error ? error.message : "Failed to save task";
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
    durationMinutes.value = null;
    selectedProjectId.value = null;
    selectedSectionId.value = null;
    showAddChecklist.value = false;
    newChecklistTitle.value = "";
    selectedLabelIds.value = [];
    showLabelPicker.value = false;
    showRecurrencePicker.value = false;
    showReminderPicker.value = false;
    reminderMinutes.value = null;
    recurrenceInterval.value = null;
    recurrenceUnit.value = null;
    recurrenceDays.value = null;
}

onMounted(async () => {
    if (priorityStore.priorities.length === 0) {
        await priorityStore.loadPriorities();
    }
    if (labelStore.labels.length === 0) {
        try {
            await labelStore.loadLabels();
        } catch (error) {
            toast.add({
                severity: "error",
                summary: "Error",
                detail: "Failed to load labels",
            });
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
    flex-wrap: wrap;
}

.datepicker-with-time {
    position: relative;
}

.task-main {
    flex: 1;
    padding: 1rem 1.5rem;
    overflow-y: auto;
}

/* Mobile responsive styles */
@media (max-width: 768px) {
    :deep(.task-modal-dialog) {
        width: 95vw !important;
        margin: 1rem;
    }

    .action-buttons-row {
        padding: 0.75rem 1rem;
        gap: 0.4rem;
    }

    .action-buttons-row :deep(.p-button) {
        flex: 1 1 auto;
        min-width: 0;
        justify-content: center;
        font-size: 0.8125rem;
        padding: 0.4rem 0.6rem;
    }

    .action-buttons-row :deep(.p-select),
    .action-buttons-row :deep(.p-datepicker) {
        flex: 1 1 auto;
        min-width: 110px;
        max-width: 200px;
    }

    .task-main {
        padding: 0.75rem 1rem;
    }

    .selected-labels {
        padding: 0 1rem 0.5rem;
    }

    .task-modal-footer {
        padding: 0.75rem 1rem;
    }

    .label-chip {
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
    }
}

@media (max-width: 480px) {
    :deep(.task-modal-dialog) {
        margin: 0;
        border-radius: 0;
    }

    .action-buttons-row {
        gap: 0.3rem;
    }

    /* Priority and Date */
    .action-buttons-row :deep(.p-select) {
        flex: 0 0 calc(40% - 0.15rem);
        min-width: 0;
        order: -2;
        /* Override previous max-width caps for phones */
        max-width: none;
        width: 100%;
    }

    .action-buttons-row :deep(.p-datepicker) {
        flex: 0 0 calc(60% - 0.15rem);
        min-width: 0;
        order: -1;
        /* Override previous max-width caps for phones */
        max-width: none;
        width: 100%;
    }

    /* Regular buttons with icons - 3 per row */
    .action-buttons-row :deep(.p-button) {
        flex: 1 1 calc(33.333% - 0.2rem);
        min-width: 0;
        max-width: none;
        padding: 0.5rem 0.4rem;
    }

    .button-icon {
        margin-right: 0 !important;
        font-size: 1rem;
    }

    /* Ensure the DatePicker input fills its container on phones */
    .action-buttons-row :deep(.p-datepicker .p-inputtext) {
        width: 100%;
    }
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

/* Mobile weekday selector */
@media (max-width: 480px) {
    .weekday-selector {
        gap: 0.3rem;
    }

    .weekday-chip {
        padding: 0.5rem 0.25rem;
        font-size: 0.75rem;
    }
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
