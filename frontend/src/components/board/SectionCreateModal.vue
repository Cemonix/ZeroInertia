<template>
    <Dialog
        v-model:visible="isVisible"
        modal
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
import { ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

const props = defineProps<{
    visible: boolean;
}>();

const emit = defineEmits<{
    'update:visible': [value: boolean];
    'create': [title: string];
}>();

const isVisible = ref(props.visible);
const sectionTitle = ref('');

// Sync with parent's visible prop
watch(() => props.visible, (newValue) => {
    isVisible.value = newValue;
    if (newValue) {
        // Reset title when dialog opens
        sectionTitle.value = '';
    }
});

// Sync back to parent when changed internally
watch(isVisible, (newValue) => {
    emit('update:visible', newValue);
});

const handleClose = () => {
    isVisible.value = false;
    sectionTitle.value = '';
};

const handleCreate = () => {
    if (!sectionTitle.value.trim()) return;

    emit('create', sectionTitle.value.trim());
    handleClose();
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
