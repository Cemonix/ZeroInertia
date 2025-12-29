<template>
    <div class="duration-picker">
        <div class="duration-row">
            <label class="duration-label" :for="hoursId">Duration</label>
            <div class="duration-inputs">
                <div class="hm-input">
                    <input
                        :id="hoursId"
                        class="duration-input"
                        type="number"
                        min="0"
                        :max="maxHours"
                        step="1"
                        v-model.number="hours"
                        aria-label="Hours"
                    />
                    <span class="hm-suffix">h</span>
                </div>
                <div class="hm-input">
                    <input
                        class="duration-input"
                        type="number"
                        min="0"
                        :max="59"
                        step="5"
                        v-model.number="minutes"
                        aria-label="Minutes"
                    />
                    <span class="hm-suffix">m</span>
                </div>
                <Button text size="small" @click="clear">Clear</Button>
            </div>
        </div>

        <div v-if="quickDurations.length" class="quick-picks">
            <span class="quick-label">Quick:</span>
            <button
                v-for="d in quickDurations"
                :key="d"
                type="button"
                class="quick-chip"
                @click.prevent="selectQuick(d)"
            >
                {{ formatMinutes(d) }}
            </button>
        </div>
    </div>
    
</template>

<script setup lang="ts">
import { ref, computed, watch, useId } from 'vue';

const props = withDefaults(defineProps<{
    modelValue: number | null; // minutes
    maxMinutes?: number;
    quickDurations?: number[]; // in minutes
}>(), {
    maxMinutes: 24 * 60,
    quickDurations: () => [15, 30, 45, 60, 90],
});

const emit = defineEmits<{
    (e: 'update:modelValue', value: number | null): void;
}>();

const hoursId = useId();

// Internal state mirrored as hours/minutes
const hours = ref<number>(0);
const minutes = ref<number>(0);
const maxHours = computed(() => Math.floor(props.maxMinutes / 60));

// Initialize from modelValue
watch(() => props.modelValue, (val) => {
    if (val === null || val === undefined) {
        hours.value = 0;
        minutes.value = 0;
        return;
    }
    const clamped = Math.max(0, Math.min(props.maxMinutes, Math.round(val)));
    hours.value = Math.floor(clamped / 60);
    minutes.value = clamped % 60;
}, { immediate: true });

function normalize() {
    // Ensure minutes within 0..59, roll over to hours
    let h = isFinite(hours.value) ? Math.max(0, Math.floor(hours.value)) : 0;
    let m = isFinite(minutes.value) ? Math.max(0, Math.floor(minutes.value)) : 0;

    if (m >= 60) {
        h += Math.floor(m / 60);
        m = m % 60;
    }

    const total = Math.min(props.maxMinutes, h * 60 + m);
    hours.value = Math.floor(total / 60);
    minutes.value = total % 60;
    emit('update:modelValue', total === 0 ? null : total);
}

watch([hours, minutes], normalize);

function clear() {
    hours.value = 0;
    minutes.value = 0;
    emit('update:modelValue', null);
}

function selectQuick(mins: number) {
    const total = Math.min(props.maxMinutes, Math.max(0, mins));
    hours.value = Math.floor(total / 60);
    minutes.value = total % 60;
    emit('update:modelValue', total);
}

function formatMinutes(mins: number): string {
    if (mins < 60) return `${mins}m`;
    if (mins % 60 === 0) return `${mins / 60}h`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}
</script>

<style scoped>
.duration-picker {
    padding-top: 0.5rem;
}

.duration-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.duration-label {
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}

.duration-inputs {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.hm-input {
    position: relative;
}

.duration-input {
    height: 2.25rem;
    width: 5.25rem; /* enough for 3 digits + suffix */
    padding: 0.5rem 1.25rem 0.5rem 0.75rem; /* leave room for suffix */
    border-radius: 8px;
    border: 1px solid var(--p-button-outlined-primary-border-color);
    background: var(--p-button-outlined-primary-background);
    color: var(--p-button-outlined-primary-color);
    transition: border-color 0.15s ease, background-color 0.15s ease;
}

.duration-input:hover {
    border-color: var(--p-button-outlined-primary-border-color);
    background: var(--p-button-outlined-primary-hover-background);
}

.duration-input:focus {
    outline: none;
    border-color: var(--p-primary-color);
}

.hm-suffix {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.8rem;
    color: var(--p-text-muted-color);
}

.quick-picks {
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.4rem;
}

.quick-label {
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
</style>
