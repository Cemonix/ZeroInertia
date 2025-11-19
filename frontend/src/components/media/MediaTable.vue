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
                v-if="type === 'all'"
                field="media_type"
                header="Type"
                sortable
                style="width: 120px"
            >
                <template #body="slotProps">
                    {{ formatMediaType(slotProps.data.media_type) }}
                </template>
            </Column>
            <Column
                v-if="type === 'all' || type === 'book'"
                field="creator"
                header="Creator"
                sortable
            >
                <template #body="slotProps">
                    <span v-if="slotProps.data.media_type === 'book'">
                        {{ slotProps.data.creator }}
                    </span>
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
            <Column field="genre" header="Genre" sortable style="width: 140px">
                <template #body="slotProps">
                    <span v-if="slotProps.data.genre">{{ slotProps.data.genre }}</span>
                </template>
            </Column>
            <Column
                v-if="type === 'all' || type === 'game'"
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
            <Column field="started_at" header="Started" sortable style="width: 140px">
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
            <Column header="Actions" style="width: 140px">
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

interface Props {
    items: MediaItem[];
    loading: boolean;
    type: "all" | MediaType;
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

const formatMediaType = (type: MediaType): string => {
    switch (type) {
        case "book":
            return "Book";
        case "game":
            return "Game";
        case "movie":
            return "Movie";
        case "show":
            return "Show";
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
