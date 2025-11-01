<template>
    <div class="label-manager">
        <header class="label-manager-header">
            <div>
                <h2>Labels</h2>
                <p>Organize tasks by applying color-coded labels.</p>
            </div>
            <Button class="button-with-icon" @click="openCreateDialog">
                <FontAwesomeIcon icon="fa fa-plus" />
                <span>New Label</span>
            </Button>
        </header>

        <section class="label-manager-body">
            <div
                v-if="labelStore.loading && !labelStore.labels.length"
                class="label-manager-loading"
            >
                <FontAwesomeIcon icon="fa fa-spinner" class="spinner" />
                <span>Loading labels...</span>
            </div>

            <div
                v-else-if="!labelStore.sortedLabels.length"
                class="label-manager-empty"
            >
                <FontAwesomeIcon icon="fa fa-tag" class="label-manager-icon" />
                <h3>No labels yet</h3>
                <p>Create your first label to start grouping tasks.</p>
                <Button class="button-with-icon" @click="openCreateDialog">
                    <FontAwesomeIcon icon="fa fa-plus" />
                    <span>Create Label</span>
                </Button>
            </div>

            <ul v-else class="label-list">
                <li v-for="label in labelStore.sortedLabels" :key="label.id" class="label-row">
                    <div class="label-info">
                        <span class="label-swatch" :style="{ backgroundColor: label.color }" />
                        <div>
                            <h3>{{ label.name }}</h3>
                            <p v-if="label.description">{{ label.description }}</p>
                        </div>
                    </div>
                    <div class="label-meta">
                        <span class="label-color">{{ label.color }}</span>
                        <small>Updated {{ formatDate(label.updated_at) }}</small>
                    </div>
                    <div class="label-actions">
                        <Button text class="icon-button" @click="openEditDialog(label.id)">
                            <FontAwesomeIcon icon="fa fa-pen" />
                        </Button>
                        <Button text class="icon-button danger" @click="confirmDelete(label.id)">
                            <FontAwesomeIcon icon="fa fa-trash" />
                        </Button>
                    </div>
                </li>
            </ul>
        </section>

        <Dialog
            v-model:visible="dialogVisible"
            modal
            :header="dialogHeader"
            :style="{ width: '480px' }"
            @hide="resetDialog"
        >
            <form class="label-form" @submit.prevent="handleSubmit">
                <div class="form-field">
                    <label for="label-name">Label name</label>
                    <InputText
                        id="label-name"
                        v-model="form.name"
                        placeholder="e.g. Urgent"
                        autocomplete="off"
                    />
                </div>

                <div class="form-field">
                    <label for="label-color">Color</label>
                    <input
                        id="label-color"
                        v-model="form.color"
                        class="color-input"
                        type="color"
                        aria-label="Pick label color"
                    >
                    <span class="color-value">{{ form.color }}</span>
                </div>

                <div class="form-field">
                    <label for="label-description">Description</label>
                    <Textarea
                        id="label-description"
                        v-model="form.description"
                        rows="3"
                        auto-resize
                        placeholder="Optional details about how to use this label"
                    />
                </div>

                <div class="dialog-actions">
                    <Button
                        label="Cancel"
                        text
                        type="button"
                        @click="closeDialog"
                    />
                    <Button
                        label="Save"
                        type="submit"
                        :loading="isSubmitting"
                        :disabled="!isFormValid || isSubmitting"
                    />
                </div>
            </form>
        </Dialog>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import Textarea from "primevue/textarea";
import { useToast } from "primevue";
import { useConfirm } from "primevue/useconfirm";
import { useLabelStore } from "@/stores/label";
import type { Label } from "@/models/label";

const labelStore = useLabelStore();
const toast = useToast();
const confirm = useConfirm();

const dialogVisible = ref(false);
const isSubmitting = ref(false);
const editingLabelId = ref<string | null>(null);

const form = reactive({
    name: "",
    color: "#3b82f6",
    description: "",
});

const dialogHeader = computed(() => editingLabelId.value ? "Edit Label" : "Create Label");

const isFormValid = computed(() => form.name.trim().length > 0);

const formatDate = (isoDate: string) => {
    try {
        const date = new Date(isoDate);
        return date.toLocaleDateString(undefined, {
            month: "short",
            day: "numeric",
            year: "numeric",
        });
    } catch {
        return "recently";
    }
};

const openCreateDialog = () => {
    editingLabelId.value = null;
    form.name = "";
    form.color = "#3b82f6";
    form.description = "";
    dialogVisible.value = true;
};

const openEditDialog = (labelId: string) => {
    const label = labelStore.getLabelById(labelId) as Label | null;
    if (!label) {
        toast.add({ severity: "warn", summary: "Label missing", detail: "Unable to find that label.", life: 3000 });
        return;
    }
    editingLabelId.value = label.id;
    form.name = label.name;
    form.color = label.color;
    form.description = label.description || "";
    dialogVisible.value = true;
};

const closeDialog = () => {
    dialogVisible.value = false;
};

const resetDialog = () => {
    editingLabelId.value = null;
    isSubmitting.value = false;
};

const handleSubmit = async () => {
    if (!isFormValid.value) return;
    isSubmitting.value = true;

    const payload = {
        name: form.name.trim(),
        color: form.color,
        description: form.description.trim() ? form.description.trim() : null,
    };

    try {
        if (editingLabelId.value) {
            await labelStore.updateLabel(editingLabelId.value, payload);
            toast.add({ severity: "success", summary: "Label updated", detail: `${payload.name} saved.`, life: 3000 });
        } else {
            await labelStore.createLabel(payload);
            toast.add({ severity: "success", summary: "Label created", detail: `${payload.name} added.`, life: 3000 });
        }
        closeDialog();
    } catch (error) {
        const message = error instanceof Error ? error.message : "Something went wrong while saving the label.";
        toast.add({ severity: "error", summary: "Unable to save label", detail: message, life: 4500 });
    } finally {
        isSubmitting.value = false;
    }
};

const confirmDelete = (labelId: string) => {
    const label = labelStore.getLabelById(labelId);
    if (!label) {
        toast.add({ severity: "warn", summary: "Label missing", detail: "That label has already been removed.", life: 3000 });
        return;
    }

    confirm.require({
        message: `Delete "${label.name}"? This action cannot be undone.`,
        header: "Delete Label",
        icon: "fa fa-triangle-exclamation",
        rejectLabel: "Cancel",
        acceptLabel: "Delete",
        acceptClass: "p-button-danger",
        accept: async () => {
            try {
                await labelStore.deleteLabel(label.id);
                toast.add({ severity: "success", summary: "Label deleted", detail: `${label.name} removed.`, life: 3000 });
            } catch (error) {
                const message = error instanceof Error ? error.message : "Failed to delete label.";
                toast.add({ severity: "error", summary: "Unable to delete", detail: message, life: 4500 });
            }
        },
    });
};

onMounted(async () => {
    if (labelStore.labels.length) return;
    try {
        await labelStore.loadLabels();
    } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to load labels.";
        toast.add({ severity: "error", summary: "Load failed", detail: message, life: 4500 });
    }
});
</script>

<style scoped>
.label-manager {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.label-manager-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.label-manager-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
}

.label-manager-header p {
    margin: 0.25rem 0 0;
    color: var(--p-text-muted-color);
}

.label-manager-body {
    flex: 1;
    padding: 1rem 0;
    border: 1px solid var(--p-surface-300);
    border-radius: 12px;
    background-color: var(--p-surface-0);
}

.label-manager-loading,
.label-manager-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    text-align: center;
    padding: 2rem;
    color: var(--p-text-muted-color);
}

.label-manager-loading {
    flex-direction: row;
    justify-content: center;
}

.label-manager-loading .spinner {
    font-size: 1.5rem;
    animation: spin 1s linear infinite;
}

.label-manager-icon {
    font-size: 2rem;
    color: var(--p-primary-color);
}

.label-manager-empty h3 {
    margin: 0;
    color: var(--p-text-color);
    font-size: 1.25rem;
}

.button-with-icon {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.icon-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--p-text-color);
}

.icon-button.danger {
    color: var(--p-red-500);
}

.label-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.label-row {
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 1fr) auto;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1.25rem;
    border-bottom: 1px solid var(--p-surface-200);
}

.label-row:last-child {
    border-bottom: none;
}

.label-info {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}

.label-info h3 {
    margin: 0;
    font-size: 1.125rem;
    color: var(--p-text-color);
}

.label-info p {
    margin: 0.25rem 0 0;
    color: var(--p-text-muted-color);
    font-size: 0.875rem;
}

.label-swatch {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.08);
}

.label-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    color: var(--p-text-muted-color);
    font-size: 0.85rem;
}

.label-color {
    font-family: monospace;
    font-size: 0.875rem;
    color: var(--p-text-color);
}

.label-actions {
    display: flex;
    gap: 0.25rem;
}

.label-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-field label {
    font-weight: 600;
    color: var(--p-text-color);
}

.color-input {
    width: 3rem;
    height: 3rem;
    padding: 0.25rem;
    border: 1px solid var(--p-surface-300);
    border-radius: 8px;
    background: transparent;
    cursor: pointer;
}

.color-value {
    font-family: monospace;
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}

.dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 0.5rem;
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
