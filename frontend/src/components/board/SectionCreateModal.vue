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

const sectionStore = useSectionStore();

const props = defineProps<{
    projectId: string;
}>();

const isVisible = defineModel<boolean>('visible');
const sectionTitle = ref('');

const handleCreate = async () => {
    if (!sectionTitle.value.trim()) return;

    try {
        const nextOrderIndex = sectionStore.sections.length;
        await sectionStore.createSection({
            title: sectionTitle.value.trim(),
            project_id: props.projectId,
            order_index: nextOrderIndex,
        });
    } catch (error) {
        console.error("Failed to create section:", error);
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
