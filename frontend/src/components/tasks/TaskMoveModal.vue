<template>
    <Dialog
        v-model:visible="visible"
        header="Move Task"
        modal
        :style="{ width: '420px' }"
        :pt="{ content: { style: { padding: '1.5rem' } } }"
        @hide="onHide"
    >
        <div class="form-field">
            <label for="project-select">
                Move "<span class="task-title-preview">{{ task.title }}</span>" to project
            </label>
            <Select
                labelId="project-select"
                v-model="selectedProjectId"
                :options="availableProjects"
                optionLabel="title"
                optionValue="id"
                placeholder="Select project"
                class="w-full"
                :disabled="isLoading || !availableProjects.length"
            />
        </div>
        <p v-if="!availableProjects.length" class="helper-text">
            You don't have any other projects yet. Create a project first to move tasks out of Inbox.
        </p>
        <div class="button-group">
            <Button label="Cancel" text @click="visible = false" />
            <Button
                label="Move"
                @click="handleMove"
                :disabled="!selectedProjectId || isLoading"
            />
        </div>
    </Dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import Dialog from "primevue/dialog";
import Select from "primevue/select";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import type { Task } from "@/models/task";
import { useProjectStore } from "@/stores/project";
import { useTaskStore } from "@/stores/task";
import { sectionService } from "@/services/sectionService";
import { storeToRefs } from "pinia";

const visible = defineModel<boolean>("visible", { default: false });

const props = defineProps<{
    task: Task;
}>();

const toast = useToast();
const projectStore = useProjectStore();
const taskStore = useTaskStore();
const { projects } = storeToRefs(projectStore);

const selectedProjectId = ref<string | null>(null);
const isLoading = ref(false);

const availableProjects = computed(() => {
    // Hide Inbox project from the move target list
    return projects.value.filter(project => !project.is_inbox);
});

watch(
    () => visible.value,
    async (isVisible) => {
        if (isVisible) {
            if (!projects.value.length) {
                try {
                    await projectStore.loadProjects();
                } catch (error) {
                    const detail = error instanceof Error ? error.message : "Failed to load projects";
                    toast.add({
                        severity: "error",
                        summary: "Projects",
                        detail,
                        life: 4000,
                    });
                }
            }

            const first = availableProjects.value[0] ?? null;
            // Default to first non-inbox project that's not the current one, if possible
            if (first && first.id !== props.task.project_id) {
                selectedProjectId.value = first.id;
            } else {
                selectedProjectId.value = first ? first.id : null;
            }
        } else {
            selectedProjectId.value = null;
            isLoading.value = false;
        }
    }
);

const handleMove = async () => {
    if (!selectedProjectId.value) {
        return;
    }
    isLoading.value = true;

    try {
        // Find a default section for the target project (first by order_index)
        const sections = await sectionService.getSections(selectedProjectId.value);
        if (!sections.length) {
            toast.add({
                severity: "error",
                summary: "Move task",
                detail: "Selected project has no sections to move the task into.",
                life: 4000,
            });
            return;
        }

        const targetSection = [...sections].sort((a, b) => a.order_index - b.order_index)[0];

        await taskStore.moveTaskToSection(props.task.id, selectedProjectId.value, targetSection.id);

        toast.add({
            severity: "success",
            summary: "Task moved",
            detail: "Task has been moved to the selected project.",
            life: 3000,
        });

        visible.value = false;
    } catch (error) {
        const detail = error instanceof Error ? error.message : "Failed to move task";
        toast.add({
            severity: "error",
            summary: "Move task",
            detail,
            life: 4000,
        });
    } finally {
        isLoading.value = false;
    }
};

const onHide = () => {
    selectedProjectId.value = null;
    isLoading.value = false;
};
</script>

<style scoped>
.form-field {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.task-title-preview {
    font-weight: 600;
}

.button-group {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}

.helper-text {
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
    margin: 0 0 0.75rem 0;
}

.w-full {
    width: 100%;
}
</style>

