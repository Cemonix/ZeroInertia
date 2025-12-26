<template>
    <Card class="backlinks-panel">
        <template #title>
            <div class="panel-header">
                <FontAwesomeIcon icon="link" />
                <span>Backlinks</span>
            </div>
        </template>
        <template #content>
            <div v-if="loading" class="loading-state">
                <ProgressSpinner
                    style="width: 32px; height: 32px"
                    strokeWidth="4"
                />
                <span>Loading backlinks...</span>
            </div>
            <div v-else-if="error" class="error-state">
                <FontAwesomeIcon icon="triangle-exclamation" />
                <span>{{ error }}</span>
            </div>
            <div v-else-if="backlinks.length === 0" class="empty-state">
                <FontAwesomeIcon icon="link" />
                <p>No notes link to this page yet</p>
                <small>Create links by using [[Note Title]] in other notes</small>
            </div>
            <div v-else class="backlinks-list">
                <div
                    v-for="backlink in backlinks"
                    :key="backlink.note_id"
                    class="backlink-item"
                    @click="handleBacklinkClick(backlink.note_id)"
                >
                    <div class="backlink-content">
                        <FontAwesomeIcon icon="file" />
                        <span class="backlink-title">{{ backlink.note_title }}</span>
                    </div>
                    <span class="backlink-date">{{
                        formatRelativeDate(backlink.created_at)
                    }}</span>
                </div>
            </div>
        </template>
    </Card>
</template>

<script lang="ts" setup>
import { ref, watch } from "vue";
import Card from "primevue/card";
import ProgressSpinner from "primevue/progressspinner";
import { noteService } from "@/services/noteService";
import type { BacklinkInfo } from "@/models/note";
import { formatDistance } from "date-fns";

const props = defineProps<{
    noteId: string | null;
}>();

const emit = defineEmits<{
    selectNote: [noteId: string];
}>();

const backlinks = ref<BacklinkInfo[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

const loadBacklinks = async (noteId: string) => {
    loading.value = true;
    error.value = null;
    try {
        backlinks.value = await noteService.getBacklinks(noteId);
    } catch (err) {
        error.value = err instanceof Error ? err.message : "Failed to load backlinks";
        backlinks.value = [];
    } finally {
        loading.value = false;
    }
};

watch(
    () => props.noteId,
    (newNoteId) => {
        if (newNoteId) {
            loadBacklinks(newNoteId);
        } else {
            backlinks.value = [];
        }
    },
    { immediate: true }
);

const handleBacklinkClick = (noteId: string) => {
    emit("selectNote", noteId);
};

const formatRelativeDate = (isoString: string) => {
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) {
        return "recently";
    }
    return formatDistance(date, new Date(), { addSuffix: true });
};
</script>

<style scoped>
.backlinks-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.backlinks-panel :deep(.p-card-body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.backlinks-panel :deep(.p-card-content) {
    flex: 1;
    overflow-y: auto;
    padding: 0;
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
}

.loading-state,
.error-state,
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
    color: var(--p-text-muted-color);
    gap: 0.75rem;
}

.error-state {
    color: var(--p-error-color);
}

.empty-state i {
    font-size: 2rem;
    opacity: 0.5;
}

.empty-state p {
    margin: 0;
    font-weight: 500;
    color: var(--p-text-color);
}

.empty-state small {
    font-size: 0.875rem;
    opacity: 0.75;
}

.backlinks-list {
    display: flex;
    flex-direction: column;
}

.backlink-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.backlink-item:hover {
    background-color: var(--p-content-hover-background);
}

.backlink-item:last-child {
    border-bottom: none;
}

.backlink-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
}

.backlink-content i {
    color: var(--p-primary-color);
    opacity: 0.7;
}

.backlink-title {
    font-weight: 500;
    color: var(--p-text-color);
}

.backlink-date {
    font-size: 0.75rem;
    color: var(--p-text-muted-color);
    white-space: nowrap;
}

@media (max-width: 768px) {
    .backlink-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .backlink-date {
        font-size: 0.7rem;
    }
}
</style>
