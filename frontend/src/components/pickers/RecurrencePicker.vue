<template>
    <div class="recurrence-picker">
        <div class="recurrence-row">
            <div class="recurrence-field">
                <label for="recurrence-interval">Repeat every</label>
                <InputNumber
                    id="recurrence-interval"
                    v-model="localInterval"
                    :min="1"
                    :max="99"
                    showButtons
                    placeholder="Interval"
                />
            </div>
            <div class="recurrence-field">
                <label for="recurrence-unit">Unit</label>
                <Select
                    id="recurrence-unit"
                    v-model="localUnit"
                    :options="UNIT_OPTIONS"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select unit"
                    size="small"
                    variant="outlined"
                />
            </div>
        </div>

        <div v-if="localUnit === 'weeks'" class="recurrence-field">
            <label>Days of the week</label>
            <div class="weekday-selector">
                <button
                    v-for="(dayLabel, dayIndex) in JS_WEEKDAY_LABELS"
                    :key="dayLabel"
                    type="button"
                    class="weekday-chip"
                    :class="{ active: localDays.includes(dayIndex) }"
                    :disabled="!hasRecurrence"
                    @click="toggleWeekday(dayIndex)"
                >
                    {{ dayLabel }}
                </button>
            </div>
        </div>

        <div class="recurrence-actions">
            <Button text size="small" :disabled="!hasRecurrence" @click="clearRecurrence">
                Clear
            </Button>
            <Button
                size="small"
                :disabled="!hasRecurrence"
                :title="!hasRecurrence ? 'Set interval and unit first' : ''"
                @click="$emit('close')"
            >
                Done
            </Button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import type { TaskRecurrenceUnit } from "@/models/task";
import { JS_WEEKDAY_LABELS, jsDaysToPythonDays, pythonDaysToJsDays } from "@/utils/recurrenceUtils";
import InputNumber from "primevue/inputnumber";
import Select from "primevue/select";
import Button from "primevue/button";

interface Props {
    interval: number | null;
    unit: TaskRecurrenceUnit | null;
    days: number[] | null; // Python convention: 0=Mon, 6=Sun
}

interface Emits {
    (e: "update:interval", value: number | null): void;
    (e: "update:unit", value: TaskRecurrenceUnit | null): void;
    (e: "update:days", value: number[] | null): void;
    (e: "close"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const UNIT_OPTIONS: { label: string; value: TaskRecurrenceUnit }[] = [
    { label: "Days", value: "days" },
    { label: "Weeks", value: "weeks" },
    { label: "Months", value: "months" },
    { label: "Years", value: "years" },
];

// Local state (using JS convention for days)
const localInterval = ref<number | null>(props.interval);
const localUnit = ref<TaskRecurrenceUnit | null>(props.unit);
const localDays = ref<number[]>(
    props.days ? pythonDaysToJsDays(props.days) : []
);

const hasRecurrence = computed(() => {
    return (
        localInterval.value !== null &&
        localInterval.value > 0 &&
        localUnit.value !== null
    );
});

// Watch local changes and emit to parent
watch(localInterval, (newVal) => {
    if (newVal !== null && newVal > 0) {
        emit("update:interval", newVal);
    } else if (newVal === null) {
        emit("update:interval", null);
    }
});

watch(localUnit, (newVal) => {
    emit("update:unit", newVal);
    // Clear days when switching away from weeks
    if (newVal !== "weeks") {
        localDays.value = [];
        emit("update:days", null);
    }
});

watch(
    localDays,
    (newVal) => {
        if (localUnit.value === "weeks" && newVal.length > 0) {
            // Convert from JS to Python convention before emitting
            emit("update:days", jsDaysToPythonDays(newVal));
        } else {
            emit("update:days", null);
        }
    },
    { deep: true }
);

// Watch props to sync local state when parent changes
watch(
    () => props.interval,
    (newVal) => {
        localInterval.value = newVal;
    }
);

watch(
    () => props.unit,
    (newVal) => {
        localUnit.value = newVal;
    }
);

watch(
    () => props.days,
    (newVal) => {
        const convertedDays = newVal ? pythonDaysToJsDays(newVal) : [];
        const isSame = convertedDays.length === localDays.value.length &&
            convertedDays.every((day, idx) => day === localDays.value[idx]);
        if (!isSame) {
            localDays.value = convertedDays;
        }
    }
);

function toggleWeekday(dayIndex: number) {
    if (localDays.value.includes(dayIndex)) {
        localDays.value = localDays.value.filter((d) => d !== dayIndex);
    } else {
        localDays.value = [...localDays.value, dayIndex].sort((a, b) => a - b);
    }
}

function clearRecurrence() {
    localInterval.value = null;
    localUnit.value = null;
    localDays.value = [];
    emit("update:interval", null);
    emit("update:unit", null);
    emit("update:days", null);
}
</script>

<style scoped>
.recurrence-picker {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 0.25rem 0;
}

.recurrence-row {
    display: flex;
    gap: 0.75rem;
}

.recurrence-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    flex: 1;
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

.weekday-chip:hover:not(:disabled) {
    border-color: var(--p-primary-color);
}

.weekday-chip.active {
    background: var(--p-primary-color);
    color: #fff;
    border-color: var(--p-primary-color);
}

.weekday-chip:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.recurrence-actions {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    padding-top: 0.5rem;
}

@media (max-width: 480px) {
    .recurrence-row {
        flex-direction: column;
    }

    .weekday-selector {
        gap: 0.3rem;
    }

    .weekday-chip {
        padding: 0.5rem 0.25rem;
        font-size: 0.75rem;
    }
}
</style>
