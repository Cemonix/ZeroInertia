<template>
    <Dialog modal
        v-model:visible="isVisible"
        header="Create New Section"
        :style="{ width: '400px' }"
        @hide="handleClose"
    >
        <div class="form-field">
            <label for="section-title">Section Name</label>
            <InputText
                id="section-title"
                v-model="sectionTitle"
                placeholder="Enter section name"
                @keyup.enter="handleCreate"
                autofocus
            />
        </div>
        <div class="button-group">
            <Button label="Cancel" text @click="handleClose" />
            <Button label="Create" @click="handleCreate" :disabled="!sectionTitle.trim()" />
        </div>
    </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useSectionStore } from '@/stores/section';
import { useToast } from "primevue";

const sectionStore = useSectionStore();
const toast = useToast();

const props = defineProps<{
    projectId: string;
}>();

const isVisible = defineModel<boolean>('visible');
const sectionTitle = ref('');

const handleCreate = async () => {
    const title = sectionTitle.value.trim();
    if (!title) {
        return;
    }

    try {
        const nextOrderIndex = sectionStore.sections.length;
        await sectionStore.createSection({
            title,
            project_id: props.projectId,
            order_index: nextOrderIndex,
        });
    } catch (error) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to create section" });
    }
    handleClose();
};

const handleClose = () => {
    isVisible.value = false;
    sectionTitle.value = '';
};
</script>

<style scoped>
.form-field {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.button-group {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}
</style>
