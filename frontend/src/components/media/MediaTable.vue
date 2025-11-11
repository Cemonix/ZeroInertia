<template>
    <div class="media-table">
        <DataTable
            :value="items"
            :loading="loading"
            dataKey="id"
            responsiveLayout="scroll"
            size="small"
        >
            <Column field="title" header="Title" sortable />

            <!-- Show Type column only when viewing all media -->
            <Column v-if="!type" field="media_type" header="Type" sortable>
                <template #body="{ data }">
                    <Tag :value="formatType(data.media_type)" />
                </template>
            </Column>

            <Column field="status" header="Status" sortable>
                <template #body="{ data }">
                    <Tag
                        :value="formatStatus(data.status)"
                        :severity="statusSeverity(data.status)"
                    />
                </template>
            </Column>

            <Column field="rating" header="Rating" sortable>
                <template #body="{ data }">
                    <span v-if="data.rating !== null">{{ data.rating }}</span>
                    <span v-else class="text-muted">—</span>
                </template>
            </Column>

            <Column field="started_at" header="Started" sortable />
            <Column field="completed_at" header="Completed" sortable />

            <!-- Type-specific columns for books -->
            <Column
                v-if="type === 'book'"
                field="author"
                header="Author"
                sortable
            />
            <Column
                v-if="type === 'book'"
                field="pages"
                header="Pages"
                sortable
            />
            <Column v-if="type === 'book'" field="isbn" header="ISBN" />
            <Column
                v-if="type === 'book'"
                field="publisher"
                header="Publisher"
            />

            <!-- Type-specific columns for movies -->
            <Column
                v-if="type === 'movie'"
                field="director"
                header="Director"
                sortable
            />
            <Column
                v-if="type === 'movie'"
                field="duration_minutes"
                header="Duration (min)"
                sortable
            />
            <Column
                v-if="type === 'movie'"
                field="release_year"
                header="Year"
                sortable
            />
            <Column v-if="type === 'movie'" field="genre" header="Genre" />

            <!-- Type-specific columns for games -->
            <Column
                v-if="type === 'game'"
                field="platform"
                header="Platform"
                sortable
            />
            <Column
                v-if="type === 'game'"
                field="developer"
                header="Developer"
            />
            <Column
                v-if="type === 'game'"
                field="playtime_hours"
                header="Playtime (h)"
                sortable
            />
            <Column v-if="type === 'game'" field="genre" header="Genre" />
            <Column v-if="type === 'game'" field="is_100_percent" header="100%">
                <template #body="{ data }">
                    <span>{{ data.is_100_percent ? "Yes" : "No" }}</span>
                </template>
            </Column>

            <!-- Type-specific columns for shows -->
            <Column
                v-if="type === 'show'"
                field="season_number"
                header="Season"
                sortable
            />
            <Column
                v-if="type === 'show'"
                field="episodes"
                header="Episodes"
                sortable
            />
            <Column v-if="type === 'show'" field="creator" header="Creator" />
            <Column
                v-if="type === 'show'"
                field="release_year"
                header="Year"
                sortable
            />
            <Column v-if="type === 'show'" field="genre" header="Genre" />

            <!-- Generic details column when viewing all media -->
            <Column v-if="!type" header="Details">
                <template #body="{ data }">
                    <span v-if="data.media_type === 'book'">{{ data.author }}</span>
                    <span v-else-if="data.media_type === 'movie'">{{ data.director }}</span>
                    <span v-else-if="data.media_type === 'game'">{{ data.platform }}</span>
                    <span v-else-if="data.media_type === 'show'">Season {{ data.season_number }}</span>
                    <span v-else>—</span>
                </template>
            </Column>

            <Column header="Actions" :exportable="false" style="width: 160px">
                <template #body="{ data }">
                    <div class="row-actions">
                        <Button size="small" text @click="$emit('edit', data)"
                            >Edit</Button
                        >
                        <Button
                            size="small"
                            text
                            severity="danger"
                            @click="confirmDelete(data)"
                            >Delete</Button
                        >
                    </div>
                </template>
            </Column>
        </DataTable>
    </div>
    <ConfirmDialog />
    <Toast />
</template>

<script setup lang="ts">
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import type { MediaItem, MediaStatus, MediaType } from '@/models/media';

const emit = defineEmits<{
    (e: 'edit', item: MediaItem): void;
    (e: 'delete', item: MediaItem): void;
}>();

defineProps<{
    items: MediaItem[];
    loading?: boolean;
    type?: MediaType;
}>();

const confirm = useConfirm();
const toast = useToast();

function formatType(type: MediaType): string {
    switch (type) {
        case 'book': return 'Book';
        case 'movie': return 'Movie';
        case 'game': return 'Game';
        case 'show': return 'Show';
    }
}

function formatStatus(status: MediaStatus): string {
    switch (status) {
        case 'planned': return 'Planned';
        case 'in_progress': return 'In Progress';
        case 'completed': return 'Completed';
        case 'dropped': return 'Dropped';
    }
}

function statusSeverity(status: MediaStatus) {
    switch (status) {
        case 'planned': return 'info';
        case 'in_progress': return 'warning';
        case 'completed': return 'success';
        case 'dropped': return 'danger';
    }
}

function confirmDelete(item: MediaItem) {
    confirm.require({
        message: `Delete \"${item.title}\"? This cannot be undone.`,
        header: 'Delete Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Delete',
        acceptClass: 'p-button-danger',
        rejectLabel: 'Cancel',
        accept: () => {
            // bubble up to parent for actual deletion
            emit('delete', item);
            toast.add({ severity: 'info', summary: 'Deleted', detail: 'Item removed', life: 2000 });
        },
    });
}
</script>

<style scoped>
.media-table {
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 12px;
    padding: 0.25rem;
}
.row-actions {
    display: flex;
    gap: 0.25rem;
}
.text-muted {
    color: var(--p-text-muted-color);
}
</style>
