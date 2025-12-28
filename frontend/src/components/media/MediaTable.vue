<template>
    <div class="media-table-wrapper">
        <DataTable
            :value="items"
            :loading="loading"
            stripedRows
            sortMode="multiple"
            removableSort
            tableStyle="min-width: 50rem"
        >
            <Column field="index" header="#" style="width: 50px">
                <template #body="slotProps">
                    {{ items.length - slotProps.index }}
                </template>
            </Column>
            <Column field="title" header="Title" sortable>
                <template #body="slotProps">
                    <div class="title-content">
                        <div class="title-main">{{ slotProps.data.title }}</div>
                        <div v-if="slotProps.data.notes" class="title-notes">
                            {{ slotProps.data.notes }}
                        </div>
                    </div>
                </template>
            </Column>
            <Column
                v-if="type === 'book' || type === 'manga'"
                field="creator"
                header="Creator / Author"
                sortable
            >
                <template #body="slotProps">
                    <span v-if="slotProps.data.media_type === 'book'">
                        {{ slotProps.data.creator }}
                    </span>
                    <span
                        v-else-if="slotProps.data.media_type === 'manga' && slotProps.data.author"
                    >
                        {{ slotProps.data.author }}
                    </span>
                </template>
            </Column>
            <Column
                v-if="type === 'book'"
                field="is_audiobook"
                header="Format"
                sortable
                style="width: 120px"
            >
                <template #body="slotProps">
                    <Tag
                        v-if="slotProps.data.media_type === 'book' && slotProps.data.is_audiobook"
                        value="Audiobook"
                        severity="info"
                        class="status-tag"
                    />
                </template>
            </Column>
            <Column field="status" header="Status" sortable style="width: 140px">
                <template #body="slotProps">
                    <Tag
                        :value="formatStatus(slotProps.data.status)"
                        :severity="statusSeverity(slotProps.data.status)"
                        class="status-tag"
                    />
                </template>
            </Column>
            <Column field="genres" header="Genres" sortable style="width: 180px">
                <template #body="slotProps">
                    <div
                        v-if="slotProps.data.genres?.length"
                        class="genre-chips"
                    >
                        <Tag
                            v-for="genre in slotProps.data.genres"
                            :key="genre.id"
                            :value="genre.name"
                            severity="secondary"
                            class="genre-tag"
                        />
                    </div>
                </template>
            </Column>
            <Column
                v-if="type === 'game'"
                field="platform"
                header="Platform"
                sortable
                style="width: 140px"
            >
                <template #body="slotProps">
                    <span v-if="slotProps.data.media_type === 'game'">
                        {{ slotProps.data.platform }}
                    </span>
                </template>
            </Column>
            <Column
                v-if="type === 'anime'"
                field="episodes"
                header="Episodes"
                sortable
                style="width: 120px"
            >
                <template #body="slotProps">
                    <span v-if="slotProps.data.media_type === 'anime'">
                        {{ slotProps.data.episodes ?? "N/A" }}
                    </span>
                </template>
            </Column>
            <Column
                v-if="type !== 'movie'"
                field="started_at"
                header="Started"
                sortable
                style="width: 140px"
            >
                <template #body="slotProps">
                    <span v-if="slotProps.data.started_at">
                        {{ formatDate(slotProps.data.started_at) }}
                    </span>
                </template>
            </Column>
            <Column field="completed_at" header="Completed" sortable style="width: 140px">
                <template #body="slotProps">
                    <span v-if="slotProps.data.completed_at">
                        {{ formatDate(slotProps.data.completed_at) }}
                    </span>
                </template>
            </Column>
            <Column header="Actions" style="width: 180px">
                <template #body="slotProps">
                    <div class="action-buttons">
                        <Button
                            text
                            size="small"
                            @click="$emit('edit', slotProps.data)"
                        >
                            Edit
                        </Button>
                        <Button
                            text
                            size="small"
                            severity="danger"
                            @click="$emit('delete', slotProps.data)"
                        >
                            Delete
                        </Button>
                        <MediaActions :item="slotProps.data" />
                    </div>
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<script setup lang="ts">
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Tag from "primevue/tag";
import Button from "primevue/button";
import type { MediaItem, MediaStatus, MediaType } from "@/models/media";
import { format, parseISO } from "date-fns";
import MediaActions from "@/components/media/MediaActions.vue";

interface Props {
    items: MediaItem[];
    loading: boolean;
    type: MediaType;
}

interface Emits {
    (e: "edit", item: MediaItem): void;
    (e: "delete", item: MediaItem): void;
}

defineEmits<Emits>();
defineProps<Props>();

const formatStatus = (status: MediaStatus): string => {
    switch (status) {
        case "planned":
            return "Planned";
        case "in_progress":
            return "In Progress";
        case "completed":
            return "Completed";
        case "dropped":
            return "Dropped";
    }
};

const statusSeverity = (status: MediaStatus): string => {
    switch (status) {
        case "planned":
            return "secondary";
        case "in_progress":
            return "warn";
        case "completed":
            return "success";
        case "dropped":
            return "danger";
    }
};

const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return "";
    try {
        return format(parseISO(dateStr), "MMM d, yyyy");
    } catch {
        return dateStr;
    }
};
</script>

<style scoped>
.media-table-wrapper {
    width: 100%;
}

.title-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.title-main {
    font-weight: 500;
}

.title-notes {
    color: var(--p-text-muted-color);
    font-size: 0.85rem;
}

.status-tag {
    border-radius: 999px;
    padding-inline: 0.6rem;
}

.action-buttons {
    display: flex;
    gap: 0.25rem;
}

.genre-chips {
    display: flex;
    gap: 0.25rem;
    flex-wrap: wrap;
}

.genre-tag {
    padding-inline: 0.5rem;
}

:deep(.p-datatable-table) {
    font-size: 0.9rem;
}

:deep(.p-datatable-thead > tr > th) {
    font-weight: 600;
    background-color: var(--p-content-background);
}

:deep(.p-datatable-tbody > tr > td) {
    padding: 0.5rem 0.75rem;
}

@media (max-width: 768px) {
    :deep(.p-datatable-tbody > tr > td) {
        padding: 0.4rem 0.5rem;
    }
}
</style>
