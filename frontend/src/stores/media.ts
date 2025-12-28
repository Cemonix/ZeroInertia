import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type {
    CSVImportResult,
    Genre,
    MediaFormValues,
    MediaItem,
    MediaStatus,
    MediaType,
    YearlyStats,
} from "@/models/media";
import { mediaService } from "@/services/mediaService";
import { useToast } from "primevue/usetoast";

export const useMediaStore = defineStore("media", () => {
    const toast = useToast();

    const items = ref<MediaItem[]>([]);
    const loading = ref(false);
    const loadingMore = ref(false);
    const error = ref<string | null>(null);

    const formVisible = ref(false);
    const editingItem = ref<MediaItem | null>(null);
    const isTemplateMode = ref(false);

    const selectedStatuses = ref<MediaStatus[]>([]);
    const search = ref("");
    const activeCategory = ref<MediaType>("book");

    const selectedGenres = ref<string[]>([]);
    const selectedPlatforms = ref<string[]>([]);
    const genres = ref<Genre[]>([]);

    const page = ref(1);
    const pageSize = ref(50);

    const yearlyStats = ref<YearlyStats | null>(null);

    const hasActiveFilters = computed(() => {
        return (
            selectedStatuses.value.length > 0 ||
            selectedGenres.value.length > 0 ||
            selectedPlatforms.value.length > 0 ||
            search.value.trim().length > 0
        );
    });

    const filteredByCategory = computed(() => {
        let list = items.value.filter(
            (item) => item.media_type === activeCategory.value,
        );

        if (selectedStatuses.value.length > 0) {
            list = list.filter((item) =>
                selectedStatuses.value.includes(item.status),
            );
        }

        if (selectedGenres.value.length > 0) {
            list = list.filter(
                (item) =>
                    item.genres.length > 0 &&
                    item.genres.some((genre) =>
                        selectedGenres.value.includes(genre.id),
                    ),
            );
        }

        if (selectedPlatforms.value.length > 0) {
            list = list.filter(
                (item) =>
                    item.media_type === "game" &&
                    item.platform !== null &&
                    selectedPlatforms.value.includes(item.platform),
            );
        }

        const term = search.value.trim().toLowerCase();
        if (term) {
            list = list.filter((item) => {
                const fields: Array<string | null | undefined> = [
                    item.title,
                    "creator" in item ? item.creator : null,
                    "author" in item ? item.author : null,
                    item.genres.length > 0
                        ? item.genres.map((genre) => genre.name).join(" ")
                        : null,
                    "platform" in item ? item.platform : null,
                    item.notes,
                ];
                return fields.some(
                    (field) =>
                        field !== null &&
                        field !== undefined &&
                        field.toLowerCase().includes(term),
                );
            });
        }

        list = list.sort((a, b) => {
            if (a.created_at < b.created_at) return 1;
            if (a.created_at > b.created_at) return -1;
            return 0;
        });

        return list;
    });

    const filteredItems = computed(() => {
        return filteredByCategory.value.slice(0, page.value * pageSize.value);
    });

    const total = computed(() => filteredByCategory.value.length);
    const hasNext = computed(
        () => filteredItems.value.length < filteredByCategory.value.length,
    );

    const availableGenres = computed(() =>
        [...genres.value].sort((a, b) => a.name.localeCompare(b.name)),
    );

    const availablePlatforms = computed(() => {
        const values = new Set<string>();
        for (const item of items.value) {
            if (item.media_type === "game" && item.platform) {
                values.add(item.platform);
            }
        }
        return Array.from(values).sort((a, b) => a.localeCompare(b));
    });

    const mergeGenres = (newGenres: Genre[]): void => {
        if (newGenres.length === 0) {
            return;
        }
        const map = new Map<string, Genre>();
        for (const genre of [...genres.value, ...newGenres]) {
            map.set(genre.id, genre);
        }
        genres.value = Array.from(map.values()).sort((a, b) =>
            a.name.localeCompare(b.name),
        );
    };

    async function load(): Promise<void> {
        loading.value = true;
        error.value = null;
        try {
            const params =
                selectedStatuses.value.length === 1
                    ? { status: selectedStatuses.value[0] }
                    : undefined;

            const [mediaLists, genreList] = await Promise.all([
                Promise.all([
                    mediaService.listBooks(params),
                    mediaService.listGames(params),
                    mediaService.listAnime(params),
                    mediaService.listManga(params),
                    mediaService.listMovies(params),
                    mediaService.listShows(params),
                ]),
                mediaService.listGenres(),
            ]);
            const [books, games, anime, manga, movies, shows] = mediaLists;
            items.value = [...books, ...games, ...anime, ...manga, ...movies, ...shows];
            page.value = 1;
            genres.value = [];
            mergeGenres([...genreList, ...items.value.flatMap((item) => item.genres)]);

            try {
                yearlyStats.value = await mediaService.getYearlyStats();
            } catch {
                yearlyStats.value = null;
            }
        } catch (err) {
            error.value =
                err instanceof Error
                    ? err.message
                    : "Failed to load media items";
        } finally {
            loading.value = false;
        }
    }

    async function ensureGenresByNames(names: string[]): Promise<string[]> {
        const normalized = Array.from(
            new Set(
                names
                    .map((name) => name.trim())
                    .filter((name) => name.length > 0),
            ),
        );
        if (normalized.length === 0) {
            return [];
        }
        const byLowerName = new Map(
            genres.value.map((genre) => [genre.name.toLowerCase(), genre] as const),
        );
        const created: Genre[] = [];
        for (const name of normalized) {
            const key = name.toLowerCase();
            if (byLowerName.has(key)) continue;
            const genre = await mediaService.createGenre({ name });
            created.push(genre);
            byLowerName.set(key, genre);
        }
        if (created.length) {
            mergeGenres(created);
        }
        return normalized
            .map((name) => byLowerName.get(name.toLowerCase()))
            .filter((genre): genre is Genre => Boolean(genre))
            .map((genre) => genre.id);
    }

    async function loadMore(): Promise<void> {
        if (!hasNext.value) return;
        loadingMore.value = true;
        try {
            page.value += 1;
        } finally {
            loadingMore.value = false;
        }
    }

    function setActiveCategory(category: MediaType): void {
        activeCategory.value = category;
        page.value = 1;
    }

    function clearFilters(): void {
        selectedStatuses.value = [];
        selectedGenres.value = [];
        selectedPlatforms.value = [];
        search.value = "";
        page.value = 1;
    }

    function openCreateForm(): void {
        editingItem.value = null;
        isTemplateMode.value = false;
        formVisible.value = true;
    }

    function openEditForm(item: MediaItem): void {
        editingItem.value = item;
        isTemplateMode.value = false;
        formVisible.value = true;
    }

    function openCreateFormFromTemplate(item: MediaItem): void {
        editingItem.value = item;
        isTemplateMode.value = true;
        formVisible.value = true;
    }

    function closeForm(): void {
        formVisible.value = false;
        editingItem.value = null;
        isTemplateMode.value = false;
    }

    async function save(values: MediaFormValues): Promise<void> {
        try {
            let saved: MediaItem;
            if (editingItem.value && !isTemplateMode.value) {
                saved = await mediaService.updateMedia(
                    editingItem.value.id,
                    editingItem.value.media_type,
                    values,
                );
                const index = items.value.findIndex(
                    (i) => i.id === editingItem.value?.id,
                );
                if (index !== -1) {
                    items.value[index] = saved;
                }
                toast.add({
                    severity: "success",
                    summary: "Media updated",
                    detail: saved.title,
                    life: 3000,
                });
            } else {
                saved = await mediaService.createMedia(values);
                items.value = [saved, ...items.value];
                toast.add({
                    severity: "success",
                    summary: "Media added",
                    detail: saved.title,
                    life: 3000,
                });
            }

            mergeGenres(saved.genres);
            closeForm();
        } catch (err) {
            const message =
                err instanceof Error
                    ? err.message
                    : "Failed to save media item";
            error.value = message;
            toast.add({
                severity: "error",
                summary: "Error",
                detail: message,
                life: 4000,
            });
            throw err;
        }
    }

    async function remove(id: string, type: MediaType): Promise<void> {
        try {
            await mediaService.deleteMedia(id, type);
            items.value = items.value.filter((item) => item.id !== id);
            toast.add({
                severity: "success",
                summary: "Media deleted",
                life: 2500,
            });
        } catch (err) {
            const message =
                err instanceof Error
                    ? err.message
                    : "Failed to delete media item";
            error.value = message;
            toast.add({
                severity: "error",
                summary: "Error",
                detail: message,
                life: 4000,
            });
            throw err;
        }
    }

    async function importCSV(file: File, type: MediaType): Promise<CSVImportResult> {
        try {
            let result: CSVImportResult;
            switch (type) {
                case "book":
                    result = await mediaService.importBooks(file);
                    break;
                case "movie":
                    result = await mediaService.importMovies(file);
                    break;
                case "game":
                    result = await mediaService.importGames(file);
                    break;
                case "show":
                    result = await mediaService.importShows(file);
                    break;
                case "manga":
                    result = await mediaService.importManga(file);
                    break;
                case "anime":
                    result = await mediaService.importAnime(file);
                    break;
            }

            await load();

            return result;
        } catch (err) {
            const message =
                err instanceof Error
                    ? err.message
                    : "Failed to import CSV";
            error.value = message;
            throw err;
        }
    }

    return {
        items,
        loading,
        loadingMore,
        error,
        formVisible,
        editingItem,
        selectedStatuses,
        selectedGenres,
        selectedPlatforms,
        genres,
        search,
        activeCategory,
        hasActiveFilters,
        filteredItems,
        total,
        hasNext,
        yearlyStats,
        availableGenres,
        availablePlatforms,
        load,
        ensureGenresByNames,
        loadMore,
        clearFilters,
        setActiveCategory,
        openCreateForm,
        openEditForm,
        openCreateFormFromTemplate,
        closeForm,
        save,
        remove,
        importCSV,
    };
});
