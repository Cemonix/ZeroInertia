<template>
    <div class="reminder-picker">
        <div class="reminder-field">
            <label for="reminder-time">Notify me</label>
            <Select
                id="reminder-time"
                v-model="minutesModel"
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
            <Button text size="small" @click="handleClear">
                Clear
            </Button>
            <Button size="small" @click="$emit('close')">
                Done
            </Button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import Select from "primevue/select";
import Button from "primevue/button";

interface Props {
    minutes: number | null;
}

interface Emits {
    (e: "update:minutes", value: number | null): void;
    (e: "close"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

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

const minutesModel = computed({
    get: () => props.minutes,
    set: (value: number | null) => emit("update:minutes", value),
});

function handleClear() {
    minutesModel.value = null;
    emit("close");
}
</script>

<style scoped>
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
</style>

