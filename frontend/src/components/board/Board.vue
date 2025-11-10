<template>
    <div class="board-container">
        <div v-if="!projectId" class="empty-state">
            <p>Select a project to view its tasks</p>
        </div>
        <div v-else>
            <!-- View mode toggle -->
            <div class="board-header">
                <SelectButton
                    v-model="viewMode"
                    :options="viewModeOptions"
                    optionLabel="label"
                    optionValue="value"
                    aria-labelledby="view-mode-toggle"
                >
                    <template #option="{ option }">
                        <FontAwesomeIcon :icon="option.icon" />
                        <span class="option-label">{{ option.label }}</span>
                    </template>
                </SelectButton>
            </div>

            <div
                ref="boardSectionsRef"
                class="board-sections"
                :class="{ 'kanban-view': viewMode === 'kanban' }"
            >
                <draggable
                    v-model="draggableSections"
                    item-key="id"
                    @start="handleDragStart"
                    @end="handleDragEnd"
                    handle=".drag-handle"
                    animation="200"
                    ghost-class="section-ghost"
                >
                    <template #item="{element}">
                        <div v-if="element" :key="element.id">
                            <BoardSection
                                class="drag-handle"
                                :project-id="projectId"
                                :section="element"
                            />
                        </div>
                    </template>
                </draggable>
                <div v-if="viewMode === 'kanban'" class="add-section-card">
                    <Button
                        @click="isSectionCreateVisible = true"
                        label="Add Section"
                        text
                        class="add-section-inline-btn"
                    >
                        <template #icon>
                            <FontAwesomeIcon icon="plus" />
                        </template>
                    </Button>
                </div>
            </div>
            <Button
                v-if="viewMode === 'list'"
                @click="isSectionCreateVisible = true"
                class="add-section-btn"
                label="Add Section"
                outlined
            >
                <template #icon>
                    <FontAwesomeIcon icon="plus" />
                </template>
            </Button>
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
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import draggable from "vuedraggable";
import BoardSection from "./BoardSection.vue";
import SectionCreateModal from "./SectionCreateModal.vue";
import TaskModal from "./TaskModal.vue";
import { useSectionStore } from "@/stores/section";
import { useTaskStore } from "@/stores/task";
import { useLabelStore } from "@/stores/label";
import type { Section } from "@/models/section";
import { useToast } from "primevue";
import SelectButton from "primevue/selectbutton";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

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

// View mode state
const VIEW_MODE_STORAGE_KEY = 'board.viewMode';

type ViewMode = 'list' | 'kanban';
const savedViewMode = localStorage.getItem(VIEW_MODE_STORAGE_KEY) as ViewMode | null;

const viewMode = ref<ViewMode>(savedViewMode || 'list');
const viewModeOptions = [
    { label: 'List', value: 'list', icon: 'list' },
    { label: 'Kanban', value: 'kanban', icon: 'table-columns' }
];

// Save view mode preference to localStorage
watch(viewMode, (newMode) => {
    localStorage.setItem(VIEW_MODE_STORAGE_KEY, newMode);
});

// Create a local ref that draggable can mutate
const draggableSections = ref<Section[]>([]);
const isDragging = ref(false);

// Watch sections from store and sync to local draggable array
watch(() => sectionStore.sortedSections, (newSections) => {
    if (!isDragging.value) {
        draggableSections.value = [...newSections];
    }
}, { immediate: true });

function handleDragStart() {
    isDragging.value = true;
}

async function handleDragEnd() {
    const sectionIds = draggableSections.value.map((section: Section) => section.id);
    try {
        await sectionStore.reorderSections(sectionIds);
    } catch (error) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to reorder sections" });
    } finally {
        isDragging.value = false;
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

// Horizontal drag-to-scroll for Kanban view
const boardSectionsRef = ref<HTMLElement | null>(null);
const isPanning = ref(false);
let panStartX = 0;
let panScrollLeft = 0;

function tryStartPan(e: MouseEvent) {
    if (viewMode.value !== 'kanban') return;
    const container = boardSectionsRef.value;
    if (!container) return;
    // Middle mouse button OR Alt + Left click to pan
    const isMiddle = e.button === 1;
    const isAltLeft = e.button === 0 && (e.altKey || e.metaKey || e.ctrlKey);
    if (!isMiddle && !isAltLeft) return;

    isPanning.value = true;
    panStartX = e.clientX;
    panScrollLeft = container.scrollLeft;
    container.classList.add('is-panning');
    container.style.cursor = 'grabbing';
    e.preventDefault();
}

function onPanMove(e: MouseEvent) {
    if (!isPanning.value) return;
    const container = boardSectionsRef.value;
    if (!container) return;
    const dx = e.clientX - panStartX;
    container.scrollLeft = panScrollLeft - dx;
}

function endPan() {
    if (!isPanning.value) return;
    const container = boardSectionsRef.value;
    isPanning.value = false;
    if (container) {
        container.classList.remove('is-panning');
        container.style.cursor = '';
    }
}

function onWheelHorizontal(e: WheelEvent) {
    if (viewMode.value !== 'kanban') return;
    const container = boardSectionsRef.value;
    if (!container) return;
    if (!e.shiftKey) return; // Only convert when Shift is held to avoid interfering with vertical scroll in task lists
    if (container.scrollWidth <= container.clientWidth) return;
    container.scrollLeft += e.deltaY;
    e.preventDefault();
}

onMounted(() => {
    const container = boardSectionsRef.value;
    if (!container) return;
    container.addEventListener('mousedown', tryStartPan);
    window.addEventListener('mousemove', onPanMove);
    window.addEventListener('mouseup', endPan);
    container.addEventListener('mouseleave', endPan);
    container.addEventListener('wheel', onWheelHorizontal, { passive: false });
});

onBeforeUnmount(() => {
    const container = boardSectionsRef.value;
    if (container) {
        container.removeEventListener('mousedown', tryStartPan);
        container.removeEventListener('mouseleave', endPan);
        container.removeEventListener('wheel', onWheelHorizontal as any);
    }
    window.removeEventListener('mousemove', onPanMove);
    window.removeEventListener('mouseup', endPan);
});
</script>

<style scoped>
.board-container {
    width: 100%;
    height: 100%;
    padding: 1.5rem;
    margin: 0 auto;
    background: var(--p-content-background);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid var(--p-content-border-color);
    display: flex;
    flex-direction: column;
    /* allow inner flex children to size/scroll correctly */
    min-height: 0;
    /* include padding and border in explicit height */
    box-sizing: border-box;
}

.board-header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1.5rem;
    flex: 0 0 auto;
}

.option-label {
    margin-left: 0.5rem;
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
    transition: all 0.3s ease;
    flex: 1;
    min-height: 0;
}

/* Kanban view support */
.board-sections.kanban-view {
    flex-direction: row;
    gap: 1rem;
    overflow-x: auto;
    overflow-y: hidden;
    align-items: stretch;
}

.board-sections.kanban-view.is-panning {
    cursor: grabbing;
}

/* Make draggable wrapper inherit flex layout in kanban view */
.board-sections.kanban-view > :first-child {
    display: flex;
    flex-direction: row;
    gap: 1rem;
    height: 100%;
    align-items: flex-start;
}

.board-sections.kanban-view :deep(.board-section) {
    min-width: 340px;
    max-width: 400px;
    flex-shrink: 0;
    max-height: calc(100vh - 225px);
    display: flex;
    flex-direction: column;
}

.board-sections.kanban-view :deep(.task-list) {
    overflow-y: auto;
    flex: 1;
    min-height: 0;
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

/* Inline add-section tile for Kanban view */
.add-section-card {
    min-width: 300px;
    max-width: 360px;
    flex-shrink: 0;
    height: 100%;
    background: var(--p-content-hover-background);
    border: 1px dashed var(--p-content-border-color);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem;
}

.add-section-inline-btn {
    width: 100%;
    justify-content: center;
    color: var(--p-text-color);
}

/* Draggable ghost styles for sections */
.section-ghost {
    opacity: 0.5;
    background: var(--p-primary-50);
    border: 2px dashed var(--p-primary-color);
}
</style>
