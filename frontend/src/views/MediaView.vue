<template>
    <WorkspaceLayout>
        <template #sidebar>
            <div class="media-categories">
                <div class="panel-header">
                    <h2 class="panel-title">Categories</h2>
                </div>
                <div class="category-buttons">
                    <Button
                        :outlined="activeCategory !== 'all'"
                        @click="setCategory('all')"
                        class="category-btn"
                    >
                        All Media
                    </Button>
                    <Button
                        v-for="type in MEDIA_TYPES"
                        :key="type.value"
                        :outlined="activeCategory !== type.value"
                        @click="setCategory(type.value)"
                        class="category-btn"
                    >
                        {{ type.label }}
                    </Button>
                </div>
            </div>
            <div class="media-filters">
                <div class="panel-header">
                    <h2 class="panel-title">Media Filters</h2>
                </div>
                <div class="panel-content">
                    <div class="field">
                        <label>Status</label>
                        <MultiSelect
                            v-model="selectedStatuses"
                            :options="MEDIA_STATUSES"
                            optionLabel="label"
                            optionValue="value"
                            display="chip"
                            placeholder="All statuses"
                        />
                    </div>
                    <div class="field">
                        <label>Genre</label>
                        <MultiSelect
                            v-model="selectedGenres"
                            :options="availableGenres"
                            optionLabel="name"
                            optionValue="id"
                            display="chip"
                            placeholder="All genres"
                            :disabled="availableGenres.length === 0"
                        />
                    </div>
                    <div class="field">
                        <label>Platform</label>
                        <MultiSelect
                            v-model="selectedPlatforms"
                            :options="availablePlatforms"
                            display="chip"
                            placeholder="All platforms"
                            :disabled="availablePlatforms.length === 0"
                        />
                    </div>
                    <div class="field">
                        <label>Search</label>
                        <InputText
                            v-model.trim="search"
                            placeholder="Title, creator, or notes"
                        />
                    </div>
                    <div class="actions">
                        <Button @click="applyFilters" :disabled="loading"
                            >Apply</Button
                        >
                        <Button
                            text
                            @click="clearFilters"
                            :disabled="!hasActiveFilters"
                            >Clear</Button
                        >
                    </div>
                </div>
            </div>
        </template>
        <template #navbar-left>
            <Button
                class="home-nav-btn"
                text
                rounded
                @click="goHome"
                aria-label="Return to home"
            >
                <font-awesome-icon icon="house" />
                <span class="home-nav-label">Home</span>
            </Button>
            <Button
                class="notes-nav-btn"
                text
                rounded
                @click="goToNotes"
                aria-label="Go to notes"
            >
                <font-awesome-icon icon="pen" />
                <span class="notes-nav-label">Notes</span>
            </Button>
        </template>
        <div class="media-view">
            <div class="toolbar">
                <div class="toolbar-left">
                    <Button @click="openCreate" aria-label="Add media" class="add-media-btn"
                        >Add Media</Button
                    >
                    <Button
                        text
                        aria-label="Add genre"
                        class="add-genre-btn"
                        @click="openGenreDialog"
                    >
                        Add Genre
                    </Button>
                </div>
                <div class="toolbar-right">
                    <span v-if="yearlyStats" class="stats-badge">
                        {{ yearlyStats.year }}:
                        {{ yearlyStats.books }} books •
                        {{ yearlyStats.games }} games •
                        {{ yearlyStats.manga }} manga •
                        {{ yearlyStats.movies }} movies •
                        {{ yearlyStats.shows }} shows
                    </span>
                    <span class="muted" v-if="hasActiveFilters"
                        >Filters active</span
                    >
                </div>
            </div>
            <div v-if="!loading && filteredItems.length === 0" class="empty-state-centered">
                <h3 class="empty-state-title">No Media To Display</h3>
                <p class="empty-state-subtitle">
                    Add your first item to get started.
                </p>
            </div>
            <template v-else>
                <div v-if="activeCategory !== 'all'">
                    <MediaTable
                        :key="activeCategory"
                        :items="filteredItems"
                        :loading="loading"
                        :type="activeCategory"
                        @edit="openEdit"
                        @delete="onDelete"
                    />
                    <div v-if="filteredItems.length > 0" class="pagination-bar">
                        <span class="count" v-if="total > 0">{{ filteredItems.length }} / {{ total }}</span>
                        <Button
                            v-if="hasNext"
                            :loading="loadingMore"
                            :disabled="loadingMore"
                            @click="loadMore"
                            size="small"
                        >
                            Load more
                        </Button>
                    </div>
                </div>
                <div v-else class="media-all-layout">
                    <div
                        v-for="type in MEDIA_TYPES"
                        :key="type.value"
                        class="media-all-section"
                    >
                        <div class="media-all-header">
                            <span class="media-all-title">{{ type.label }}</span>
                            <span class="media-all-count">
                                {{
                                    filteredItems.filter(
                                        (i) => i.media_type === type.value
                                    ).length
                                }}
                                items
                            </span>
                        </div>
                        <div class="media-all-list">
                            <div
                                v-for="item in filteredItems.filter(
                                    (i) => i.media_type === type.value
                                )"
                                :key="item.id"
                                class="media-card"
                            >
                                <div class="media-card-header">
                                    <span class="media-card-title">
                                        {{ item.title }}
                                    </span>
                                    <Tag
                                        :value="formatStatus(item.status)"
                                        :severity="statusSeverity(item.status)"
                                        class="status-tag"
                                    />
                                </div>
                                <div class="media-card-meta">
                                    <span
                                        v-if="
                                            item.media_type === 'book' &&
                                            item.creator
                                        "
                                        class="media-card-detail"
                                    >
                                        {{ item.creator }}
                                    </span>
                                    <span
                                        v-else-if="
                                            item.media_type === 'manga' &&
                                            'author' in item &&
                                            item.author
                                        "
                                        class="media-card-detail"
                                    >
                                        {{ item.author }}
                                    </span>
                                    <span
                                        v-else-if="
                                            item.media_type === 'game' &&
                                            item.platform
                                        "
                                        class="media-card-detail"
                                    >
                                        {{ item.platform }}
                                    </span>
                                    <span
                                        v-else-if="formatGenres(item)"
                                        class="media-card-detail"
                                    >
                                        {{ formatGenres(item) }}
                                    </span>
                                </div>
                                <div class="media-card-dates">
                                    <span
                                        v-if="item.started_at"
                                        class="media-card-date"
                                    >
                                        Started {{ item.started_at }}
                                    </span>
                                    <span
                                        v-if="item.completed_at"
                                        class="media-card-date"
                                    >
                                        • Completed {{ item.completed_at }}
                                    </span>
                                </div>
                                <div class="media-card-actions">
                                    <Button
                                        size="small"
                                        text
                                        @click="openEdit(item)"
                                    >
                                        Edit
                                    </Button>
                                    <Button
                                        size="small"
                                        text
                                        severity="danger"
                                        @click="onDelete(item)"
                                    >
                                        Delete
                                    </Button>
                                </div>
                            </div>
                            <div
                                v-if="
                                    filteredItems.filter(
                                        (i) => i.media_type === type.value
                                    ).length === 0
                                "
                                class="media-all-empty"
                            >
                                No {{ type.label.toLowerCase() }} yet.
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
        <MediaForm
            v-model:visible="formVisible"
            :item="editingItem"
            @saved="reload"
        />
        <Dialog
            v-model:visible="genreDialogVisible"
            modal
            header="Add Genre"
            :style="{ width: '420px' }"
        >
            <div class="genre-dialog">
                <InputText
                    v-model="newGenreName"
                    placeholder="Genre name"
                    autofocus
                    @keyup.enter="saveGenre"
                />
                <div class="genre-dialog-actions">
                    <Button text label="Cancel" @click="closeGenreDialog" />
                    <Button
                        label="Add"
                        :disabled="!canSaveGenre"
                        :loading="addingGenre"
                        @click="saveGenre"
                    />
                </div>
            </div>
        </Dialog>
    </WorkspaceLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import WorkspaceLayout from "@/layouts/WorkspaceLayout.vue";
import MediaTable from "@/components/media/MediaTable.vue";
import MediaForm from "@/components/media/MediaForm.vue";
import MultiSelect from "primevue/multiselect";
import InputText from "primevue/inputtext";
import Tag from "primevue/tag";
import { MEDIA_STATUSES, MEDIA_TYPES, type MediaItem, type MediaType } from "@/models/media";
import { useMediaStore } from "@/stores/media";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import type { MediaStatus } from "@/models/media";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue";
import Dialog from "primevue/dialog";

const authStore = useAuthStore();
const mediaStore = useMediaStore();
const router = useRouter();
const confirm = useConfirm();
const toast = useToast();
const genreDialogVisible = ref(false);
const newGenreName = ref("");
const addingGenre = ref(false);
const canSaveGenre = computed(
    () => newGenreName.value.trim().length > 0 && !addingGenre.value,
);

const {
    filteredItems,
    loading,
    loadingMore,
    formVisible,
    editingItem,
    selectedStatuses,
    selectedGenres,
    selectedPlatforms,
    search,
    hasActiveFilters,
    activeCategory,
    hasNext,
    total,
    yearlyStats,
    availableGenres,
    availablePlatforms,
} = storeToRefs(mediaStore);

const goHome = () => {
    if (router.currentRoute.value.path !== "/home") router.push("/home");
};
const goToNotes = () => {
    if (router.currentRoute.value.path !== "/notes") router.push("/notes");
};

const reload = async () => {
    await mediaStore.load();
};

const loadMore = async () => {
    await mediaStore.loadMore();
};

const applyFilters = async () => {
    await reload();
};
const clearFilters = () => {
    mediaStore.clearFilters();
};

const setCategory = (category: "all" | MediaType) => {
    mediaStore.setActiveCategory(category);
    void reload();
};

const openCreate = () => mediaStore.openCreateForm();
const openEdit = (item: any) => mediaStore.openEditForm(item);
const openGenreDialog = () => {
    newGenreName.value = "";
    genreDialogVisible.value = true;
};
const closeGenreDialog = () => {
    genreDialogVisible.value = false;
    newGenreName.value = "";
};
const saveGenre = async () => {
    const name = newGenreName.value.trim();
    if (!name || addingGenre.value) return;
    addingGenre.value = true;
    try {
        await mediaStore.ensureGenresByNames([name]);
        toast.add({
            severity: "success",
            summary: "Genre added",
            detail: name,
            life: 2500,
        });
        closeGenreDialog();
    } catch (err) {
        toast.add({
            severity: "error",
            summary: "Error",
            detail:
                err instanceof Error
                    ? err.message
                    : "Failed to add genre",
            life: 3000,
        });
    } finally {
        addingGenre.value = false;
    }
};
const onDelete = (item: any) => {
    const label = item.title || "this media item";

    confirm.require({
        message: `Delete "${label}"? This cannot be undone.`,
        header: "Confirm Deletion",
        acceptClass: "p-button-danger",
        acceptLabel: "Delete",
        rejectLabel: "Cancel",
        accept: async () => {
            try {
                if (editingItem.value && editingItem.value.id === item.id) {
                    mediaStore.closeForm();
                }
                await mediaStore.remove(item.id, item.media_type);
            } catch {
                toast.add({
                    severity: "error",
                    summary: "Error",
                    detail: "Failed to delete media item",
                    life: 3000,
                });
            }
        },
    });
};

const formatGenres = (item: MediaItem): string | null => {
    if (!item.genres || item.genres.length === 0) {
        return null;
    }
    return item.genres.map((genre) => genre.name).join(", ");
};

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

onMounted(async () => {
    if (authStore.isAuthenticated) {
        await reload();
    }
});

watch(
    () => authStore.isAuthenticated,
    async (isAuth) => {
        if (isAuth) await reload();
    }
);
</script>

<style scoped>
.media-categories {
    display: flex;
    flex-direction: column;
}
.category-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.75rem;
}
.category-btn {
    width: 100%;
    justify-content: flex-start;
}
.media-filters {
    display: flex;
    flex-direction: column;
}
.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1rem 0.75rem 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
}
.panel-title {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0;
}
.panel-content {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
}
.field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}
.range-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: var(--p-text-muted-color);
}
.toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    gap: 1rem;
}

.toolbar-left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.add-media-btn {
    flex-shrink: 0;
}

.add-genre-btn {
    flex-shrink: 0;
}

.toolbar-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.stats-badge {
    font-size: 0.85rem;
    color: var(--p-text-muted-color);
}

@media (max-width: 768px) {
    .toolbar {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }

    .add-media-btn {
        width: 100%;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: 600;
    }

    .toolbar-left {
        flex-direction: column;
        align-items: stretch;
    }

    .add-genre-btn {
        width: 100%;
        justify-content: center;
    }

    .toolbar-right {
        justify-content: center;
        gap: 0.75rem;
    }

    .stats-badge {
        font-size: 0.8rem;
        text-align: center;
        width: 100%;
    }
}

.muted {
    color: var(--p-text-muted-color);
    font-size: 0.9rem;
}
.notes-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
}
.notes-nav-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}
/* Match notes button style for Home button */
.home-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
}
.home-nav-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}

/* Centered empty state */
.empty-state-centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    min-height: 240px;
    text-align: center;
    color: var(--p-text-muted-color);
}
.empty-state-title {
    margin: 0;
    font-weight: 700;
    color: var(--p-text-color);
}
.empty-state-subtitle {
    margin: 0;
}

.pagination-bar {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.5rem;
}
.pagination-bar .count {
    color: var(--p-text-muted-color);
    font-size: 0.9rem;
}

.media-all-layout {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-top: 0.75rem;
}

.media-all-section {
    background: var(--p-content-background);
    border-radius: 12px;
    border: 1px solid var(--p-content-border-color);
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.media-all-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
}

.media-all-title {
    font-weight: 600;
}

.media-all-count {
    font-size: 0.85rem;
    color: var(--p-text-muted-color);
}

.media-all-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.media-card {
    border-radius: 10px;
    border: 1px solid var(--p-content-border-color);
    padding: 0.6rem 0.7rem;
    background: var(--p-content-background);
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}

.media-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}

.media-card-title {
    font-weight: 500;
}

.media-card-meta {
    font-size: 0.85rem;
    color: var(--p-text-muted-color);
}

.media-card-dates {
    font-size: 0.8rem;
    color: var(--p-text-muted-color);
}

.media-card-actions {
    display: flex;
    gap: 0.4rem;
    margin-top: 0.25rem;
}

.media-all-empty {
    font-size: 0.85rem;
    color: var(--p-text-muted-color);
    font-style: italic;
}

.genre-dialog {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding-top: 0.25rem;
}

.genre-dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}
</style>
