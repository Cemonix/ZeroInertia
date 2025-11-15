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
                <div class="form-field">
                    <label for="title">Title</label>
                    <InputText
                        id="title"
                        v-model="title"
                        @keyup.enter="saveTask"
                        placeholder="Task name (use @ for dates, e.g., 'Meeting @tomorrow 3pm')"
                        autofocus
                    />
                    <div v-if="detectedDateText" class="date-detection-hint">
                        <FontAwesomeIcon icon="calendar" />
                        <span>Due date set: <strong>{{ detectedDateText }}</strong></span>
                        <button
                            type="button"
                            class="clear-detection-btn"
                            @click="clearDetectedDate"
                            title="Clear due date"
                        >
                            <FontAwesomeIcon icon="times" />
                        </button>
                    </div>
                </div>
                <div class="form-field">
                    <label for="description">Description</label>
                    <Textarea id="description" v-model="description" rows="4" />
                </div>

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
                <div class="label-picker">
                    <div v-if="labelStore.loading" class="label-picker-empty">
                        <FontAwesomeIcon icon="spinner" class="spinner" />
                        <span>Loading labels...</span>
                    </div>
                    <div
                        v-else-if="!labelStore.sortedLabels.length"
                        class="label-picker-empty"
                    >
                        <FontAwesomeIcon icon="tag" class="label-picker-icon" />
                        <span>No labels yet.</span>
                        <p>
                            Use the Labels workspace in the sidebar to create
                            one.
                        </p>
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
                            <span
                                class="label-picker-swatch"
                                :style="{ backgroundColor: label.color }"
                            />
                            <span class="label-picker-name">{{
                                label.name
                            }}</span>
                            <span
                                v-if="label.description"
                                class="label-picker-description"
                            >
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
                                v-for="(
                                    dayLabel, dayIndex
                                ) in JS_WEEKDAY_LABELS"
                                :key="dayLabel"
                                type="button"
                                class="weekday-chip"
                                :class="{
                                    active: recurrenceDaysOfWeek.includes(
                                        dayIndex
                                    ),
                                }"
                                @click="toggleWeekday(dayIndex)"
                            >
                                {{ dayLabel }}
                            </button>
                        </div>
                    </div>
                    <div class="recurrence-actions">
                        <Button text size="small" @click="clearRecurrence"
                            >Clear</Button
                        >
                        <Button
                            size="small"
                            @click="showRecurrencePicker = false"
                            >Done</Button
                        >
                    </div>
                </div>
            </Popover>

            <!-- Reminder Picker Popover -->
            <Popover
                v-model:visible="showReminderPicker"
                title="Reminder"
                width="360px"
            >
                <div class="reminder-picker">
                    <div class="reminder-field">
                        <label for="reminder-time">Notify me</label>
                        <Select
                            id="reminder-time"
                            v-model="reminderMinutes"
                            :options="REMINDER_OPTIONS"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="Select reminder time"
                            size="small"
                            showClear
                            variant="outlined"
                        />
                    </div>
                    <div class="reminder-actions">
                        <Button text size="small" @click="clearReminder"
                            >Clear</Button
                        >
                        <Button size="small" @click="showReminderPicker = false"
                            >Done</Button
                        >
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
import { ref, watch, computed, type Ref, onMounted, onBeforeUnmount } from "vue";
import Textarea from "primevue/textarea";
import Select from "primevue/select";
import DateTimePicker from "@/components/common/DateTimePicker.vue";
import { useTaskStore } from "@/stores/task";
import { useChecklistStore } from "@/stores/checklist";
import { usePriorityStore } from "@/stores/priority";
import { useLabelStore } from "@/stores/label";
import CheckList from "@/components/common/CheckList.vue";
import Popover from "@/components/common/Popover.vue";
import { useToast } from "primevue";
import type { Label } from "@/models/label";
import type { Task, TaskRecurrenceType } from "@/models/task";
import {
    jsDaysToPythonDays,
    pythonDaysToJsDays,
    JS_WEEKDAY_LABELS,
} from "@/utils/recurrenceUtils";
import { useNaturalLanguageParsing } from "@/composables/useNaturalLanguageParsing";

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
const durationMinutes: Ref<number | null> = ref(null);

// UI state for popovers
const showAddChecklist = ref(false);
const newChecklistTitle = ref("");
const showLabelPicker = ref(false);
const selectedLabelIds = ref<string[]>([]);
const showRecurrencePicker = ref(false);
const showReminderPicker = ref(false);

// Recurrence state (stored directly on task now)
const recurrenceType = ref<TaskRecurrenceType | null>(null);
const recurrenceDaysOfWeek = ref<number[]>([]); // JS convention: 0=Sunday

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

const RECURRENCE_OPTIONS: { label: string; value: TaskRecurrenceType }[] = [
    { label: "Daily", value: "daily" },
    { label: "Every Other Day", value: "alternate_days" },
    { label: "Specific Days", value: "weekly" },
];

const REMINDER_OPTIONS: { label: string; value: number }[] = [
    { label: "At time of event", value: 0 },
    { label: "5 minutes before", value: 5 },
    { label: "10 minutes before", value: 10 },
    { label: "15 minutes before", value: 15 },
    { label: "30 minutes before", value: 30 },
    { label: "1 hour before", value: 60 },
    { label: "2 hours before", value: 120 },
    { label: "1 day before", value: 1440 },
];

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
            .map((day) => JS_WEEKDAY_LABELS[day]);
        const daysLabel = selectedDays.length ? selectedDays.join(" ") : "Days";
        return `Weekly · ${daysLabel}`;
    }

    return "Repeat";
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

    // Load recurrence from task fields (convert Python days to JS convention)
    if (task.recurrence_type) {
        const recurrence = task.recurrence_type as TaskRecurrenceType;
        recurrenceType.value = recurrence;
        if (recurrence === "weekly" && task.recurrence_days) {
            recurrenceDaysOfWeek.value = pythonDaysToJsDays(task.recurrence_days);
        } else {
            recurrenceDaysOfWeek.value = [];
        }
    } else {
        resetRecurrence();
    }

    // Load reminder
    reminderMinutes.value = task.reminder_minutes ?? null;
}

function applyInitialValues() {
    const initialValues = taskStore.initialTaskValues;
    if (!initialValues) return;

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

    const currentTask = taskStore.getCurrentTask;
    if (currentTask) {
        // Editing existing task
        loadTaskData(currentTask);
        await loadChecklists(currentTask.id);
    } else {
        // Creating new task
        resetForm();
        applyInitialValues();
    }
}

function handleModalClose() {
    checklistStore.clearChecklists();
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

function toggleWeekday(dayIndex: number) {
    if (recurrenceDaysOfWeek.value.includes(dayIndex)) {
        recurrenceDaysOfWeek.value = recurrenceDaysOfWeek.value.filter(
            (day) => day !== dayIndex
        );
    } else {
        recurrenceDaysOfWeek.value = [
            ...recurrenceDaysOfWeek.value,
            dayIndex,
        ].sort((a, b) => a - b);
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

function clearReminder() {
    reminderMinutes.value = null;
    showReminderPicker.value = false;
}

function getRecurrencePayload(): {
    type: TaskRecurrenceType | null;
    days: number[] | null;
} {
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

    // Use cleaned title if date was detected, otherwise use original title
    const finalTitle = cleanedTitleBeforeSave.value || title.value;

    let recurrencePayload: {
        type: TaskRecurrenceType | null;
        days: number[] | null;
    };
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


    isLoading.value = true;

    try {
        if (currentTask) {
            await taskStore.updateTask(currentTask.id, {
                title: finalTitle,
                description: description.value,
                completed: taskCompleted.value,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                duration_minutes: durationMinutes.value,
                label_ids: selectedLabelIds.value,
                recurrence_type: recurrencePayload.type,
                recurrence_days: recurrencePayload.days,
                reminder_minutes: reminderMinutes.value,
            });
        } else {
            await taskStore.createTask({
                project_id: props.projectId ? props.projectId : null,
                section_id: sectionIdForCreate as string ? sectionIdForCreate as string : null,
                title: finalTitle,
                description: description.value,
                priority_id: priorityId.value,
                due_datetime: dueDateTimeString.value,
                duration_minutes: durationMinutes.value,
                label_ids: selectedLabelIds.value,
                recurrence_type: recurrencePayload.type,
                recurrence_days: recurrencePayload.days,
                reminder_minutes: reminderMinutes.value,
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
    showAddChecklist.value = false;
    newChecklistTitle.value = "";
    selectedLabelIds.value = [];
    showLabelPicker.value = false;
    showRecurrencePicker.value = false;
    showReminderPicker.value = false;
    reminderMinutes.value = null;
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

    .form-field {
        margin-bottom: 1rem;
    }

    .selected-labels {
        padding: 0 1rem 0.5rem;
    }

    .task-modal-footer {
        padding: 0.75rem 1rem;
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
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    transition: background-color 0.15s ease;
}

.label-picker-item:hover {
    background-color: var(--p-content-hover-background);
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

/* Mobile label picker */
@media (max-width: 480px) {
    .label-picker-item {
        padding: 0.75rem 0.5rem;
        gap: 0.625rem;
    }

    .label-picker-swatch {
        width: 28px;
        height: 28px;
    }

    .label-picker-name {
        font-size: 0.9375rem;
    }

    .label-chip {
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
    }
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

.reminder-picker {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.reminder-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.reminder-field label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--p-text-color);
}

.reminder-actions {
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

/* Natural language date detection hint */
.date-detection-hint {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.375rem;
    padding: 0.5rem 0.625rem;
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 6px;
    font-size: 0.8125rem;
    color: var(--p-text-color);
    animation: slideDown 0.2s ease-out;
}

.date-detection-hint svg {
    color: var(--p-text-muted-color);
    font-size: 0.875rem;
}

.date-detection-hint strong {
    color: var(--p-text-color);
    font-weight: 500;
}

.clear-detection-btn {
    margin-left: auto;
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    color: var(--p-text-muted-color);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.15s ease;
}

.clear-detection-btn:hover {
    background: var(--p-highlight-background);
    color: var(--p-highlight-color);
}

.clear-detection-btn svg {
    font-size: 0.75rem;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
