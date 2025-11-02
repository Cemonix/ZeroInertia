<template>
    <div class="board-container">
        <div v-if="!projectId" class="empty-state">
            <p>Select a project to view its tasks</p>
        </div>
        <div v-else>
            <div class="board-sections">
                <draggable
                    v-model="draggableSections"
                    item-key="id"
                    @end="handleDragEnd"
                    handle=".section-header"
                    animation="200"
                    ghost-class="section-ghost"
                >
                    <template #item="{element}">
                        <BoardSection
                            :project-id="projectId"
                            :section="element"
                        />
                    </template>
                </draggable>
            </div>
            <Button
                @click="isSectionCreateVisible = true"
                class="add-section-btn"
                icon="pi pi-plus"
                label="Add Section"
                outlined
            />
        </div>
    </div>

    <SectionCreateModal
        v-if="projectId"
        v-model:visible="isSectionCreateVisible"
        :projectId="projectId"
    />

    <TaskModal v-if="projectId" :projectId="projectId" />
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import draggable from "vuedraggable";
import BoardSection from "./BoardSection.vue";
import SectionCreateModal from "./SectionCreateModal.vue";
import TaskModal from "./TaskModal.vue";
import { useSectionStore } from "@/stores/section";
import { useTaskStore } from "@/stores/task";
import { useLabelStore } from "@/stores/label";
import type { Section } from "@/models/section";
import { useToast } from "primevue";

const toast = useToast();

interface Props {
    projectId?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
    projectId: null,
});

const sectionStore = useSectionStore();
const taskStore = useTaskStore();
const labelStore = useLabelStore();

const isSectionCreateVisible = ref(false);

// Create a local ref that draggable can mutate
const draggableSections = ref<Section[]>([]);

// Watch sections from store and sync to local draggable array
watch(() => sectionStore.sortedSections, (newSections) => {
    draggableSections.value = [...newSections];
}, { immediate: true });

async function handleDragEnd() {
    // Use the mutated draggableSections array (which has the new order)
    const sectionIds = draggableSections.value.map((section: Section) => section.id);
    try {
        await sectionStore.reorderSections(sectionIds);
    } catch (error) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to reorder sections" });
    }
}

const loadSections = async () => {
    if (!props.projectId) {
        sectionStore.clearSections();
        return;
    }

    try {
        await Promise.all([
            sectionStore.loadSectionsForProject(props.projectId),
            taskStore.loadTasksForProject(props.projectId),
            // Load labels at board level to prevent duplicate requests from individual cards
            labelStore.labels.length === 0 ? labelStore.loadLabels() : Promise.resolve(),
        ]);
    } catch (error) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to load sections and tasks" });
    }
};

watch(
    () => props.projectId,
    () => { loadSections(); },
    { immediate: true }
);
</script>

<style scoped>
.board-container {
    width: 100%;
    padding: 1.5rem;
    margin: 0 auto;
    background: var(--p-content-background);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid var(--p-content-border-color);
}

.board-header {
    margin-bottom: 1.5rem;
}

.board-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--p-text-color);
    margin: 0;
}

.board-sections {
    display: flex;
    flex-direction: column;
    gap: 0;
}

/* Future: Kanban view support */
.board-sections.kanban-view {
    flex-direction: row;
    gap: 1rem;
    overflow-x: auto;
}

.board-sections.kanban-view > * {
    min-width: 300px;
    max-width: 350px;
}

.empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    color: var(--p-text-muted-color);
    font-size: 1.125rem;
}

.add-section-btn {
    margin-top: 1rem;
    width: 100%;
}

/* Draggable ghost styles for sections */
.section-ghost {
    opacity: 0.5;
    background: var(--p-primary-50);
    border: 2px dashed var(--p-primary-color);
}
</style>
