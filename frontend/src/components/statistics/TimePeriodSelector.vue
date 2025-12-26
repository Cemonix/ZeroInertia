<template>
    <div class="time-period-selector">
        <div class="period-buttons">
            <button
                v-for="period in periods"
                :key="period.value"
                :class="['period-btn', { active: selectedPeriod === period.value }]"
                @click="selectPeriod(period.value)"
            >
                <FontAwesomeIcon :icon="period.icon" />
                <span>{{ period.label }}</span>
            </button>
            <button
                :class="['period-btn period-btn-custom', { active: selectedPeriod === 'custom' }]"
                @click="toggleCustom"
            >
                <FontAwesomeIcon icon="calendar" />
                <span>Custom</span>
            </button>
        </div>

        <div v-if="showCustomPicker && selectedPeriod === 'custom'" class="custom-picker-overlay" @click="closeCustomPicker">
            <div class="custom-picker-panel" @click.stop>
                <h4>Select Date Range</h4>
                <DatePicker
                    v-model="customRange"
                    selection-mode="range"
                    date-format="yy-mm-dd"
                    :inline="true"
                    show-button-bar
                />
                <div class="picker-actions">
                    <Button label="Cancel" severity="secondary" size="small" @click="closeCustomPicker" />
                    <Button label="Apply" size="small" @click="applyCustomRange" :disabled="!isValidRange" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import DatePicker from "primevue/datepicker";
import Button from "primevue/button";
import type { TimePeriod } from "@/models/statistics";
import { format } from "date-fns";

interface Props {
    modelValue: TimePeriod;
}

interface Emits {
    (event: "update:modelValue", value: TimePeriod): void;
    (event: "customRangeApplied", range: { start: string; end: string }): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const periods = [
    { value: "week" as TimePeriod, label: "This Week", icon: "calendar-week" },
    { value: "month" as TimePeriod, label: "This Month", icon: "calendar-day" },
    { value: "all" as TimePeriod, label: "All Time", icon: "infinity" },
];

const customRange = ref<Date[] | null>(null);
const showCustomPicker = ref(false);

const selectedPeriod = computed(() => props.modelValue);

const isValidRange = computed(() => {
    return customRange.value && customRange.value.length === 2 && customRange.value[0] && customRange.value[1];
});

function selectPeriod(period: TimePeriod) {
    if (period !== "custom") {
        showCustomPicker.value = false;
    }
    emit("update:modelValue", period);
}

function toggleCustom() {
    if (selectedPeriod.value === "custom") {
        showCustomPicker.value = !showCustomPicker.value;
    } else {
        emit("update:modelValue", "custom");
        showCustomPicker.value = true;
    }
}

function closeCustomPicker() {
    showCustomPicker.value = false;
}

function applyCustomRange() {
    if (isValidRange.value && customRange.value) {
        const start = format(customRange.value[0], "yyyy-MM-dd");
        const end = format(customRange.value[1], "yyyy-MM-dd");
        emit("customRangeApplied", { start, end });
        showCustomPicker.value = false;
    }
}
</script>

<style scoped>
.time-period-selector {
    position: relative;
    margin-bottom: 24px;
}

.period-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.period-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    border: 1px solid var(--p-content-border-color);
    background: var(--p-content-background);
    color: var(--p-text-color);
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.period-btn:hover {
    background: var(--p-content-hover-background);
    border-color: var(--p-primary-color);
}

.period-btn.active {
    background: var(--p-primary-color);
    color: white;
    border-color: var(--p-primary-color);
}

.period-btn svg {
    font-size: 16px;
}

.custom-picker-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;
}

.custom-picker-panel {
    background: var(--p-content-background);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    max-width: 90vw;
    animation: slideUp 0.3s ease;
}

.custom-picker-panel h4 {
    margin: 0 0 16px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--p-text-color);
}

.picker-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 16px;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes slideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@media (max-width: 768px) {
    .period-buttons {
        justify-content: stretch;
    }

    .period-btn {
        flex: 1;
        justify-content: center;
        min-width: 120px;
    }
}
</style>
