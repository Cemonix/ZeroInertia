import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type { Label } from "@/models/label";
import { labelService } from "@/services/labelService";
import type { LabelCreateInput, LabelUpdateInput } from "@/models/label";

export const useLabelStore = defineStore("label", () => {
    const labels = ref<Label[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const sortedLabels = computed(() => {
        return [...labels.value].sort((a, b) => a.name.localeCompare(b.name));
    });

    const getLabelById = computed(() => {
        return (labelId: string) => labels.value.find(label => label.id === labelId) ?? null;
    });

    const setError = (message: string | null) => {
        error.value = message;
    };

    const loadLabels = async () => {
        // Prevent concurrent requests - if already loading, skip
        if (loading.value) {
            return;
        }

        loading.value = true;
        setError(null);
        try {
            labels.value = await labelService.getLabels();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load labels");
            labels.value = [];
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const createLabel = async (payload: LabelCreateInput) => {
        loading.value = true;
        setError(null);
        try {
            const label = await labelService.createLabel(payload);
            labels.value.push(label);
            return label;
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create label");
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const updateLabel = async (labelId: string, updates: LabelUpdateInput) => {
        loading.value = true;
        setError(null);
        try {
            const updated = await labelService.updateLabel(labelId, updates);
            const index = labels.value.findIndex(label => label.id === labelId);
            if (index !== -1) {
                labels.value.splice(index, 1, updated);
            }
            return updated;
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update label");
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const deleteLabel = async (labelId: string) => {
        loading.value = true;
        setError(null);
        try {
            await labelService.deleteLabel(labelId);
            labels.value = labels.value.filter(label => label.id !== labelId);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to delete label");
            throw err;
        } finally {
            loading.value = false;
        }
    };

    return {
        labels,
        loading,
        error,
        sortedLabels,
        getLabelById,
        setError,
        loadLabels,
        createLabel,
        updateLabel,
        deleteLabel,
    };
});
