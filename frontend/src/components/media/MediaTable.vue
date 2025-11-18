<template>
    <div class="media-table-wrapper">
        <table class="media-table">
            <thead>
                <tr>
                    <th class="col-title">Title</th>
                    <th v-if="type === 'all'" class="col-type">Type</th>
                    <th v-if="type === 'all' || type === 'book'" class="col-creator">
                        Creator
                    </th>
                    <th class="col-status">Status</th>
                    <th class="col-genre">Genre</th>
                    <th v-if="type === 'all' || type === 'game'" class="col-platform">
                        Platform
                    </th>
                    <th class="col-date">Started</th>
                    <th class="col-date">Completed</th>
                    <th class="col-actions"></th>
                </tr>
            </thead>
            <tbody>
                <template v-if="loading && items.length === 0">
                    <tr
                        v-for="n in 3"
                        :key="`skeleton-${n}`"
                    >
                        <td class="cell-title">
                            <div class="title-main">
                                <Skeleton
                                    width="70%"
                                    height="1rem"
                                    class="skeleton-line"
                                />
                            </div>
                            <div class="title-notes">
                                <Skeleton
                                    width="50%"
                                    height="0.8rem"
                                    class="skeleton-line secondary"
                                />
                            </div>
                        </td>
                        <td
                            v-if="type === 'all'"
                            class="cell-type"
                        >
                            <Skeleton
                                width="50%"
                                height="0.8rem"
                                class="skeleton-line"
                            />
                        </td>
                        <td
                            v-if="type === 'all' || type === 'book'"
                            class="cell-creator"
                        >
                            <Skeleton
                                width="60%"
                                height="0.8rem"
                                class="skeleton-line"
                            />
                        </td>
                        <td class="cell-status">
                            <Skeleton
                                width="4.5rem"
                                height="1.4rem"
                                class="skeleton-pill"
                            />
                        </td>
                        <td class="cell-genre">
                            <Skeleton
                                width="40%"
                                height="0.8rem"
                                class="skeleton-line"
                            />
                        </td>
                        <td
                            v-if="type === 'all' || type === 'game'"
                            class="cell-platform"
                        >
                            <Skeleton
                                width="50%"
                                height="0.8rem"
                                class="skeleton-line"
                            />
                        </td>
                        <td class="cell-date">
                            <Skeleton
                                width="60%"
                                height="0.8rem"
                                class="skeleton-line"
                            />
                        </td>
                        <td class="cell-date">
                            <Skeleton
                                width="60%"
                                height="0.8rem"
                                class="skeleton-line"
                            />
                        </td>
                        <td class="cell-actions">
                            <Skeleton
                                width="70%"
                                height="1.2rem"
                                class="skeleton-line"
                            />
                        </td>
                    </tr>
                </template>
                <tr v-else-if="items.length === 0">
                    <td :colspan="columnCount" class="empty-cell">
                        No media items in this view.
                    </td>
                </tr>
                <tr
                    v-for="item in items"
                    :key="item.id"
                >
                    <td class="cell-title">
                        <div class="title-main">{{ item.title }}</div>
                        <div v-if="item.notes" class="title-notes">
                            {{ item.notes }}
                        </div>
                    </td>
                    <td
                        v-if="type === 'all'"
                        class="cell-type"
                    >
                        {{ formatMediaType(item.media_type) }}
                    </td>
                    <td
                        v-if="type === 'all' || type === 'book'"
                        class="cell-creator"
                    >
                        <span v-if="item.media_type === 'book'">
                            {{ item.creator }}
                        </span>
                    </td>
                    <td class="cell-status">
                        <Tag
                            :value="formatStatus(item.status)"
                            :severity="statusSeverity(item.status)"
                            class="status-tag"
                        />
                    </td>
                    <td class="cell-genre">
                        <span v-if="item.genre">{{ item.genre }}</span>
                    </td>
                    <td
                        v-if="type === 'all' || type === 'game'"
                        class="cell-platform"
                    >
                        <span v-if="item.media_type === 'game'">
                            {{ item.platform }}
                        </span>
                    </td>
                    <td class="cell-date">
                        <span v-if="item.started_at">
                            {{ formatDate(item.started_at) }}
                        </span>
                    </td>
                    <td class="cell-date">
                        <span v-if="item.completed_at">
                            {{ formatDate(item.completed_at) }}
                        </span>
                    </td>
                    <td class="cell-actions">
                        <Button
                            text
                            size="small"
                            @click="$emit('edit', item)"
                        >
                            Edit
                        </Button>
                        <Button
                            text
                            size="small"
                            severity="danger"
                            @click="$emit('delete', item)"
                        >
                            Delete
                        </Button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import Tag from "primevue/tag";
import Button from "primevue/button";
import Skeleton from "primevue/skeleton";
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
const props = defineProps<Props>();

const columnCount = computed(() => {
    let count = 6; // title, status, genre, started, completed, actions
    if (props.type === "all") {
        count += 2; // type + creator
    } else if (props.type === "book") {
        count += 1; // creator
    }
    if (props.type === "all" || props.type === "game") {
        count += 1; // platform
    }
    return count;
});

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
    overflow-x: auto;
}

.media-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.media-table thead tr {
    background-color: var(--p-content-background);
}

.media-table th,
.media-table td {
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--p-content-border-color);
    text-align: left;
    vertical-align: middle;
}

.col-actions {
    width: 120px;
}

.cell-title .title-main {
    font-weight: 500;
}

.cell-title .title-notes {
    margin-top: 0.15rem;
    color: var(--p-text-muted-color);
    font-size: 0.8rem;
}

.cell-status :deep(.p-tag) {
    font-size: 0.8rem;
}

.status-tag {
    border-radius: 999px;
    padding-inline: 0.6rem;
}

.empty-cell {
    text-align: center;
    color: var(--p-text-muted-color);
    font-style: italic;
}

.cell-actions {
    white-space: nowrap;
}

.skeleton-line {
    border-radius: 999px;
}

.skeleton-line.secondary {
    margin-top: 0.25rem;
}

.skeleton-pill {
    border-radius: 999px;
}

@media (max-width: 768px) {
    .media-table th,
    .media-table td {
        padding: 0.4rem 0.5rem;
    }
}
</style>
