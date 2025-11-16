<template>
    <div class="label-picker">
        <div v-if="loading" class="label-picker-empty">
            <FontAwesomeIcon icon="spinner" class="spinner" />
            <span>Loading labels...</span>
        </div>
        <div v-else-if="!labels.length" class="label-picker-empty">
            <FontAwesomeIcon icon="tag" class="label-picker-icon" />
            <span>No labels yet.</span>
            <p>
                Use the Labels workspace in the sidebar to create one.
            </p>
        </div>
        <div v-else class="label-picker-list">
            <label
                v-for="label in labels"
                :key="label.id"
                class="label-picker-item"
                :for="`label-${label.id}`"
            >
                <Checkbox
                    :inputId="`label-${label.id}`"
                    v-model="localSelectedIds"
                    :value="label.id"
                />
                <span
                    class="label-picker-swatch"
                    :style="{ backgroundColor: label.color }"
                />
                <span class="label-picker-name">
                    {{ label.name }}
                </span>
                <span
                    v-if="label.description"
                    class="label-picker-description"
                >
                    {{ label.description }}
                </span>
            </label>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Label } from "@/models/label";

interface Props {
    labels: Label[];
    selectedIds: string[];
    loading?: boolean;
}

interface Emits {
    (e: "update:selectedIds", value: string[]): void;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
});

const emit = defineEmits<Emits>();

const localSelectedIds = computed({
    get: () => props.selectedIds,
    set: (value: string[]) => emit("update:selectedIds", value),
});
</script>

<style scoped>
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

