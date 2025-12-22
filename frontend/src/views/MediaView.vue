<template>
    <WorkspaceLayout>
        <template #sidebar>
            <div class="media-categories">
                <div class="panel-header">
                    <h2 class="panel-title">Categories</h2>
                </div>
                <div class="category-buttons">
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
                <FontAwesomeIcon icon="house" />
                <span class="home-nav-label">Home</span>
            </Button>
            <Button
                class="notes-nav-btn"
                text
                rounded
                @click="goToNotes"
                aria-label="Go to notes"
            >
                <FontAwesomeIcon icon="pen" />
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
                        aria-label="Import CSV"
                        class="import-btn"
                        @click="openImportDialog"
                    >
                        <FontAwesomeIcon icon="file-import" />
                        Import CSV
                    </Button>
                    <Button
                        text
                        aria-label="Export CSV"
                        class="export-btn"
                        @click="handleExport"
                        :disabled="filteredItems.length === 0"
                    >
                        <FontAwesomeIcon icon="file-export" />
                        Export CSV
                    </Button>
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
                        {{ yearlyStats.anime ?? 0 }} anime •
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
        <Dialog
            v-model:visible="importDialogVisible"
            modal
            :header="`Import ${activeCategory} CSV`"
            :style="{ width: '520px' }"
        >
            <div class="import-dialog">
                <p class="import-instructions">
                    Select a CSV file to import {{ activeCategory }} items. The file will be validated before import.
                </p>
                <input
                    ref="fileInput"
                    type="file"
                    accept=".csv"
                    @change="onFileSelected"
                    class="file-input"
                />
                <div v-if="importResult" class="import-result">
                    <div class="result-section">
                        <h4>Import Summary</h4>
                        <p><strong>Total rows:</strong> {{ importResult.total_rows }}</p>
                        <p><strong>Imported:</strong> {{ importResult.imported }}</p>
                        <p><strong>Skipped duplicates:</strong> {{ importResult.skipped_duplicates }}</p>
                    </div>
                    <div v-if="importResult.duplicate_titles.length > 0" class="result-section">
                        <h4>Duplicate Titles (Skipped)</h4>
                        <ul class="duplicate-list">
                            <li v-for="title in importResult.duplicate_titles" :key="title">{{ title }}</li>
                        </ul>
                    </div>
                </div>
                <div class="import-dialog-actions">
                    <Button text label="Close" @click="closeImportDialog" />
                    <Button
                        label="Import"
                        :disabled="!selectedFile || importing"
                        :loading="importing"
                        @click="handleImport"
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
import { MEDIA_STATUSES, MEDIA_TYPES, type CSVImportResult, type MediaType } from "@/models/media";
import { useMediaStore } from "@/stores/media";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
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

const importDialogVisible = ref(false);
const importing = ref(false);
const selectedFile = ref<File | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);
const importResult = ref<CSVImportResult | null>(null);

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

const setCategory = (category: MediaType) => {
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

const openImportDialog = () => {
    selectedFile.value = null;
    importResult.value = null;
    importDialogVisible.value = true;
    if (fileInput.value) {
        fileInput.value.value = "";
    }
};

const closeImportDialog = () => {
    importDialogVisible.value = false;
    selectedFile.value = null;
    importResult.value = null;
    if (fileInput.value) {
        fileInput.value.value = "";
    }
};

const onFileSelected = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
        selectedFile.value = target.files[0];
        importResult.value = null;
    }
};

const handleImport = async () => {
    if (!selectedFile.value) return;

    importing.value = true;
    try {
        const result = await mediaStore.importCSV(selectedFile.value, activeCategory.value);
        importResult.value = result;

        toast.add({
            severity: "success",
            summary: "Import successful",
            detail: `Imported ${result.imported} items, skipped ${result.skipped_duplicates} duplicates`,
            life: 4000,
        });

        selectedFile.value = null;
        if (fileInput.value) {
            fileInput.value.value = "";
        }
    } catch (err) {
        toast.add({
            severity: "error",
            summary: "Import failed",
            detail: err instanceof Error ? err.message : "Failed to import CSV",
            life: 5000,
        });
    } finally {
        importing.value = false;
    }
};

const handleExport = async () => {
    try {
        const { mediaService } = await import("@/services/mediaService");
        let blob: Blob;

        switch (activeCategory.value) {
            case "book":
                blob = await mediaService.exportBooks();
                break;
            case "movie":
                blob = await mediaService.exportMovies();
                break;
            case "game":
                blob = await mediaService.exportGames();
                break;
            case "show":
                blob = await mediaService.exportShows();
                break;
            case "manga":
                blob = await mediaService.exportManga();
                break;
            case "anime":
                blob = await mediaService.exportAnime();
                break;
        }

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${activeCategory.value}s.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        toast.add({
            severity: "success",
            summary: "Export successful",
            detail: `Exported ${filteredItems.value.length} ${activeCategory.value} items`,
            life: 3000,
        });
    } catch (err) {
        toast.add({
            severity: "error",
            summary: "Export failed",
            detail: err instanceof Error ? err.message : "Failed to export CSV",
            life: 5000,
        });
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

.import-btn {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.export-btn {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.import-dialog {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-top: 0.5rem;
}

.import-instructions {
    margin: 0;
    color: var(--p-text-muted-color);
    font-size: 0.95rem;
}

.file-input {
    padding: 0.5rem;
    border: 1px solid var(--p-content-border-color);
    border-radius: 4px;
    cursor: pointer;
}

.import-result {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    background: var(--p-content-background);
    border-radius: 6px;
    border: 1px solid var(--p-content-border-color);
}

.result-section h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.95rem;
    font-weight: 600;
}

.result-section p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
}

.duplicate-list {
    margin: 0.5rem 0 0 0;
    padding-left: 1.5rem;
    max-height: 150px;
    overflow-y: auto;
}

.duplicate-list li {
    font-size: 0.9rem;
    margin: 0.25rem 0;
    color: var(--p-text-muted-color);
}

.import-dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding-top: 0.5rem;
}
</style>
