<template>
    <div class="task-form">
        <div class="form-field">
            <label for="title">Title</label>
            <InputText
                id="title"
                v-model="localTitle"
                @keyup.enter="$emit('save')"
                placeholder="Task name (use @ for dates, e.g., 'Meeting @tomorrow 3pm')"
                autofocus
            />
            <div v-if="detectedDateText" class="date-detection-hint">
                <FontAwesomeIcon icon="calendar" />
                <span>Due date set: <strong>{{ detectedDateText }}</strong></span>
                <button
                    type="button"
                    class="clear-detection-btn"
                    @click="$emit('clearDetectedDate')"
                    title="Clear due date"
                >
                    <FontAwesomeIcon icon="times" />
                </button>
            </div>
        </div>

        <!-- Project and Section Selection -->
        <div class="project-section-picker">
            <div class="picker-field">
                <label for="project-select">Project</label>
                <Select
                    id="project-select"
                    v-model="localProjectId"
                    :options="projectOptions"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select Project"
                    showClear
                    :filter="projectOptions.length > 5"
                    :disabled="loading"
                >
                    <template #value="slotProps">
                        <div v-if="slotProps.value">
                            <span>{{ selectedProjectLabel }}</span>
                        </div>
                        <span v-else>Select Project</span>
                    </template>
                </Select>
            </div>

            <div class="picker-field">
                <label for="section-select">Section</label>
                <Select
                    id="section-select"
                    v-model="localSectionId"
                    :options="sectionOptions"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select Section"
                    showClear
                    :disabled="!localProjectId || loading || sectionOptions.length === 0"
                >
                    <template #empty>
                        <div class="empty-message">
                            {{ localProjectId ? 'No sections in this project' : 'Select a project first' }}
                        </div>
                    </template>
                </Select>
            </div>
        </div>

        <div class="form-field">
            <label for="description">Description</label>
            <Textarea
                id="description"
                v-model="localDescription"
                rows="4"
                placeholder="Add more details..."
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Select from 'primevue/select';
import { useProjectStore } from '@/stores/project';
import { useSectionStore } from '@/stores/section';

interface Props {
    title: string;
    description: string | null;
    projectId: string | null;
    sectionId: string | null;
    detectedDateText?: string;
    loading?: boolean;
}

interface Emits {
    (e: 'update:title', value: string): void;
    (e: 'update:description', value: string | null): void;
    (e: 'update:projectId', value: string | null): void;
    (e: 'update:sectionId', value: string | null): void;
    (e: 'clearDetectedDate'): void;
    (e: 'save'): void;
}

const props = withDefaults(defineProps<Props>(), {
    detectedDateText: '',
    loading: false,
});

const emit = defineEmits<Emits>();

const projectStore = useProjectStore();
const sectionStore = useSectionStore();

const localTitle = computed({
    get: () => props.title,
    set: (value: string) => emit('update:title', value),
});

const localDescription = computed({
    get: () => props.description,
    set: (value: string | null) => emit('update:description', value),
});

const localProjectId = computed({
    get: () => props.projectId,
    set: (value: string | null) => emit('update:projectId', value),
});

const localSectionId = computed({
    get: () => props.sectionId,
    set: (value: string | null) => emit('update:sectionId', value),
});

// Project options for the dropdown (exclude inbox project)
const projectOptions = computed(() => {
    return projectStore.projects
        .filter(p => !p.is_inbox)
        .map(p => ({
            label: p.title,
            value: p.id,
        }));
});

// Section options - filtered by selected project
const sectionOptions = computed(() => {
    if (!localProjectId.value) return [];

    const sections = sectionStore.getSectionsByProject(localProjectId.value);
    return sections.map(s => ({
        label: s.title,
        value: s.id,
    }));
});

// Computed properties for displaying selected values
const selectedProjectLabel = computed(() => {
    if (!localProjectId.value) return '';
    const project = projectStore.getProjectById(localProjectId.value);
    return project?.title || '';
});

// When project changes, clear section if it doesn't belong to the new project
watch(localProjectId, (newProjectId) => {
    if (!newProjectId) {
        // Project cleared, clear section too
        localSectionId.value = null;
        return;
    }

    // Check if current section belongs to the new project
    if (localSectionId.value) {
        const section = sectionStore.sections.find(s => s.id === localSectionId.value);
        if (section && section.project_id !== newProjectId) {
            // Section doesn't belong to new project, clear it
            localSectionId.value = null;
        }
    }
});
</script>

<style scoped>
.task-form {
    display: flex;
    flex-direction: column;
}

.form-field {
    display: flex;
    flex-direction: column;
    margin-bottom: 1.5rem;
}

.form-field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.project-section-picker {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.picker-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.picker-field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.empty-message {
    padding: 0.5rem;
    text-align: center;
    color: var(--p-text-muted-color);
    font-size: 0.875rem;
}

/* Ensure Select components fill width */
.picker-field :deep(.p-select) {
    width: 100%;
}

/* Responsive: stack on smaller screens */
@media (max-width: 640px) {
    .project-section-picker {
        grid-template-columns: 1fr;
    }
}

.date-detection-hint {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.375rem;
    padding: 0.5rem 0.625rem;
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 6px;
    font-size: 0.8125rem;
    color: var(--p-text-color);
    animation: slideDown 0.2s ease-out;
}

.date-detection-hint svg {
    color: var(--p-text-muted-color);
    font-size: 0.875rem;
}

.date-detection-hint strong {
    color: var(--p-text-color);
    font-weight: 500;
}

.clear-detection-btn {
    margin-left: auto;
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    color: var(--p-text-muted-color);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.15s ease;
}

.clear-detection-btn:hover {
    background: var(--p-highlight-background);
    color: var(--p-highlight-color);
}

.clear-detection-btn svg {
    font-size: 0.75rem;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
