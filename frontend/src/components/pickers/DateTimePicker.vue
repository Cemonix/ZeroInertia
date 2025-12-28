<template>
    <DatePicker
        ref="datePickerRef"
        v-model="dateForPicker"
        :placeholder="placeholder"
        :size="size"
        :showIcon="showIcon"
        :showClear="showClear"
        iconDisplay="input"
        :showTime="true"
        hourFormat="24"
        :labelId="timelabelId + '-picker'"
    >
        <template #dropdownicon>
            <FontAwesomeIcon icon="calendar" />
        </template>
        <template #footer>
            <div class="dtp-footer">
                <div class="dtp-time-row">
                    <label class="dtp-time-label" :for="timelabelId">Time</label>
                    <input
                        :id="timelabelId"
                        class="dtp-time-input"
                        type="time"
                        v-model="time"
                        step="60"
                        aria-label="Time"
                    />
                    <Button text size="small" @click="clear">Clear</Button>
                </div>
                <div v-if="quickTimes.length" class="dtp-quick-picks">
                    <span class="quick-label">Quick:</span>
                    <button
                        v-for="t in quickTimes"
                        :key="t"
                        type="button"
                        class="quick-chip"
                        @click.prevent="setQuickTime(t)"
                    >
                        {{ t }}
                    </button>
                    <button type="button" class="quick-chip" @click.prevent="setNow">Now</button>
                </div>
                <DurationPicker
                    class="dtp-duration"
                    :modelValue="duration"
                    @update:modelValue="val => emit('update:duration', val)"
                />
            </div>
        </template>
    </DatePicker>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import DatePicker from 'primevue/datepicker';
import DurationPicker from '@/components/pickers/DurationPicker.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

const props = withDefaults(defineProps<{
    modelValue: string | null;
    placeholder?: string;
    size?: string;
    showIcon?: boolean;
    showClear?: boolean;
    quickTimes?: string[];
    duration?: number | null; // minutes
}>(), {
    placeholder: 'Due Date',
    size: 'small',
    showIcon: true,
    showClear: true,
    quickTimes: () => ['09:00', '13:00', '18:00', '21:00'],
    duration: null,
});

const emit = defineEmits<{
    (e: 'update:modelValue', value: string | null): void;
    (e: 'update:duration', value: number | null): void;
}>();

const date = ref<Date | null>(null);
const time = ref<string | null>(null); // HH:mm
const timelabelId = `dtp-time-${Math.random().toString(36).slice(2, 8)}`;
const syncing = ref(false); // Flag to prevent re-emission during sync
const datePickerRef = ref<InstanceType<typeof DatePicker> | null>(null);
const mutationObserver = ref<MutationObserver | null>(null);
const inputEventHandler = ref<(() => void) | null>(null);

// Keep internal state in sync when parent modelValue changes
watch(() => props.modelValue, (val) => {
    syncing.value = true;
    if (!val) {
        date.value = null;
        time.value = null;
        syncing.value = false;
        return;
    }
    const dt = new Date(val);
    if (isNaN(dt.getTime())) {
        date.value = null;
        time.value = null;
        syncing.value = false;
        return;
    }
    date.value = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate());
    const hh = String(dt.getHours()).padStart(2, '0');
    const mm = String(dt.getMinutes()).padStart(2, '0');
    time.value = `${hh}:${mm}`;
    syncing.value = false;
}, { immediate: true });

function recomputeAndEmit() {
    if (syncing.value) return; // Don't emit during sync

    if (!date.value || !time.value) {
        emit('update:modelValue', null);
        return;
    }
    const [hh, mm] = time.value.split(':').map((s) => parseInt(s, 10));
    const y = date.value.getFullYear();
    const m = date.value.getMonth();
    const d = date.value.getDate();
    const local = new Date(y, m, d, isNaN(hh) ? 0 : hh, isNaN(mm) ? 0 : mm, 0, 0);
    emit('update:modelValue', local.toISOString());
}

watch([date, time], recomputeAndEmit);

// If date is cleared via calendar clear, also clear time
watch(date, (newVal) => {
    if (!newVal) time.value = null;
});

function clear() {
    date.value = null;
    time.value = null;
    emit('update:modelValue', null);
}

function setQuickTime(t: string) {
    time.value = t;
}

function setNow() {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    time.value = `${hh}:${mm}`;
}

// Compose Date sent to DatePicker, including time for correct input rendering
const dateForPicker = computed<Date | null>({
    get() {
        if (!date.value) return null;
        const [hh, mm] = (time.value ?? '00:00').split(':').map((s) => parseInt(s, 10));
        return new Date(
            date.value.getFullYear(),
            date.value.getMonth(),
            date.value.getDate(),
            isNaN(hh) ? 0 : hh,
            isNaN(mm) ? 0 : mm,
            0,
            0
        );
    },
    set(val: Date | null) {
        if (!val) {
            date.value = null;
            return;
        }
        date.value = new Date(val.getFullYear(), val.getMonth(), val.getDate());

        // Ensure time is always set when date is selected
        if (!time.value) {
            const now = new Date();
            const hh = String(now.getHours()).padStart(2, '0');
            const mm = String(now.getMinutes()).padStart(2, '0');
            time.value = `${hh}:${mm}`;
        }
    },
});

// Format the display string
function getFormattedDisplay(): string {
    if (!date.value || !time.value) return '';

    const dt = dateForPicker.value;
    if (!dt) return '';

    // Format date as M/D/YYYY
    const month = dt.getMonth() + 1;
    const day = dt.getDate();
    const year = dt.getFullYear();
    const dateStr = `${month}/${day}/${year}`;

    // Format start time as HH:mm
    const startHH = String(dt.getHours()).padStart(2, '0');
    const startMM = String(dt.getMinutes()).padStart(2, '0');
    const startTime = `${startHH}:${startMM}`;

    // Calculate and format end time if duration is provided
    if (props.duration && props.duration > 0) {
        const endDt = new Date(dt.getTime() + props.duration * 60000);
        const endHH = String(endDt.getHours()).padStart(2, '0');
        const endMM = String(endDt.getMinutes()).padStart(2, '0');
        const endTime = `${endHH}:${endMM}`;
        return `${dateStr} ${startTime} - ${endTime}`;
    }

    return `${dateStr} ${startTime}`;
}

// Update the input element display to show time range
function updateInputDisplay() {
    nextTick(() => {
        const inputElement = document.getElementById(timelabelId + '-picker') as HTMLInputElement;
        if (!inputElement) return;

        const formattedValue = getFormattedDisplay();
        if (formattedValue && inputElement.value !== formattedValue) {
            inputElement.value = formattedValue;
        }
    });
}

// Watch for changes to update the display
watch([date, time, () => props.duration], updateInputDisplay);

// Re-apply custom formatting after DatePicker updates
watch(dateForPicker, () => {
    setTimeout(updateInputDisplay, 50);
});

// Setup MutationObserver to watch for PrimeVue overwriting our value
onMounted(() => {
    updateInputDisplay();

    // Watch for changes to the input value and re-apply our format
    nextTick(() => {
        const inputElement = document.getElementById(timelabelId + '-picker') as HTMLInputElement;
        if (!inputElement) return;

        // Use MutationObserver to detect when PrimeVue changes the input value
        mutationObserver.value = new MutationObserver(() => {
            const formattedValue = getFormattedDisplay();
            if (formattedValue && inputElement.value !== formattedValue) {
                inputElement.value = formattedValue;
            }
        });

        // Also listen to input events
        inputEventHandler.value = () => {
            setTimeout(updateInputDisplay, 10);
        };
        inputElement.addEventListener('input', inputEventHandler.value);

        // Observe changes to input element attributes
        mutationObserver.value.observe(inputElement, {
            attributes: true,
            attributeFilter: ['value']
        });
    });
});

// Cleanup event listeners and observers
onBeforeUnmount(() => {
    if (mutationObserver.value) {
        mutationObserver.value.disconnect();
    }

    if (inputEventHandler.value) {
        const inputElement = document.getElementById(timelabelId + '-picker') as HTMLInputElement;
        if (inputElement) {
            inputElement.removeEventListener('input', inputEventHandler.value);
        }
    }
});
</script>

<style>
/*
 * WARNING: Global style override!
 * This hides PrimeVue's built-in time picker across ALL DatePicker instances.
 * Why? Because we use a custom browser time input instead (better UX).
 *
 * DO NOT use PrimeVue's showTime prop elsewhere in the app without understanding this!
 * Time-only pickers (.p-datepicker-timeonly) are still allowed.
 */
.p-datepicker-calendar-container + .p-datepicker-time-picker {
    display: none !important;
}

/* Keep time-only pickers working (just in case we need them someday) */
.p-datepicker-timeonly .p-datepicker-time-picker {
    display: block !important;
}
</style>

<style scoped>
.dtp-footer {
    padding: 0.5rem 0.75rem 0.75rem;
    border-top: 1px solid var(--p-content-border-color);
}

.dtp-time-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.dtp-time-label {
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}

.dtp-time-input {
    height: 2.25rem;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    border: 1px solid var(--p-button-outlined-primary-border-color);
    background: var(--p-button-outlined-primary-background);
    color: var(--p-button-outlined-primary-color);
    transition: border-color 0.15s ease, background-color 0.15s ease;
}

.dtp-time-input:hover {
    border-color: var(--p-button-outlined-primary-border-color);
    background: var(--p-button-outlined-primary-hover-background);
}

.dtp-time-input:focus {
    outline: none;
    border-color: var(--p-primary-color);
}

.dtp-quick-picks {
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.4rem;
}

.dtp-quick-picks .quick-label {
    font-size: 0.8rem;
    color: var(--p-text-muted-color);
    margin-right: 0.25rem;
}

.quick-chip {
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    border: 1px solid var(--p-content-border-color);
    background: var(--p-content-hover-background);
    color: var(--p-text-color);
    font-size: 0.75rem;
}

.quick-chip:hover {
    border-color: var(--p-primary-color);
}

/* Override DatePicker input width to accommodate time range display */
:deep(.p-inputtext) {
    width: 100%;
    max-width: 240px;
}
</style>
