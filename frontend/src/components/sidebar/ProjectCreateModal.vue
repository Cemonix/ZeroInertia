<template>
    <Dialog class="project-modal-dialog" 
        :visible="visible" 
        @update:visible="visible = $event"
        modal 
        header="Create Project"
        :style="{ width: '400px' }">
        <div class="form-field">
            <label for="project-title">Project Title</label>
            <InputText id="project-title" 
                v-model="projectTitle" 
                @keyup.enter="createProject" 
                autofocus
            />
        </div>
        <div class="button-group">
            <Button label="Cancel" text @click="visible = false" />
            <Button
                label="Create"
                @click="createProject"
                :disabled="projectTitle.trim() === ''"
            />
        </div>
    </Dialog>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Dialog from 'primevue/dialog';
import { useProjectStore } from '@/stores/project';
import { useToast } from "primevue";

const toast = useToast();

const projectStore = useProjectStore();
const projectTitle = ref('');

const visible = defineModel('visible', { type: Boolean, default: false });

async function createProject() {
    const title = projectTitle.value.trim();
    if (!title) {
        return;
    }

    try {
        await projectStore.createProject({ title });
        projectTitle.value = '';
        visible.value = false;
    } catch (error) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to create project" });
    }
}
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
