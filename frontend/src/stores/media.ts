import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type {
    MediaFormValues,
    MediaItem,
    MediaStatus,
    MediaType,
    YearlyStats,
} from "@/models/media";
import { mediaService } from "@/services/mediaService";
import { useToast } from "primevue/usetoast";

type Category = "all" | MediaType;

export const useMediaStore = defineStore("media", () => {
    const toast = useToast();

    const items = ref<MediaItem[]>([]);
    const loading = ref(false);
    const loadingMore = ref(false);
    const error = ref<string | null>(null);

    const formVisible = ref(false);
    const editingItem = ref<MediaItem | null>(null);

    const selectedStatuses = ref<MediaStatus[]>([]);
    const search = ref("");
    const activeCategory = ref<Category>("all");

    const selectedGenres = ref<string[]>([]);
    const selectedPlatforms = ref<string[]>([]);

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

    const filteredAllItems = computed(() => {
        let list = [...items.value];

        if (activeCategory.value !== "all") {
            list = list.filter(
                (item) => item.media_type === activeCategory.value,
            );
        }

        if (selectedStatuses.value.length > 0) {
            list = list.filter((item) =>
                selectedStatuses.value.includes(item.status),
            );
        }

        if (selectedGenres.value.length > 0) {
            list = list.filter(
                (item) =>
                    item.genre !== null &&
                    selectedGenres.value.includes(item.genre),
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
                    item.genre,
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

        return list.sort((a, b) => {
            if (a.created_at < b.created_at) return 1;
            if (a.created_at > b.created_at) return -1;
            return 0;
        });
    });

    const filteredItems = computed(() => {
        return filteredAllItems.value.slice(0, page.value * pageSize.value);
    });

    const total = computed(() => filteredAllItems.value.length);
    const hasNext = computed(
        () => filteredItems.value.length < filteredAllItems.value.length,
    );

    const availableGenres = computed(() => {
        const values = new Set<string>();
        for (const item of items.value) {
            if (item.genre) {
                values.add(item.genre);
            }
        }
        return Array.from(values).sort((a, b) => a.localeCompare(b));
    });

    const availablePlatforms = computed(() => {
        const values = new Set<string>();
        for (const item of items.value) {
            if (item.media_type === "game" && item.platform) {
                values.add(item.platform);
            }
        }
        return Array.from(values).sort((a, b) => a.localeCompare(b));
    });

    async function load(): Promise<void> {
        loading.value = true;
        error.value = null;
        try {
            const params =
                selectedStatuses.value.length === 1
                    ? { status: selectedStatuses.value[0] }
                    : undefined;

            const [books, games, movies, shows] = await Promise.all([
                mediaService.listBooks(params),
                mediaService.listGames(params),
                mediaService.listMovies(params),
                mediaService.listShows(params),
            ]);
            items.value = [...books, ...games, ...movies, ...shows];
            page.value = 1;

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

    async function loadMore(): Promise<void> {
        if (!hasNext.value) return;
        loadingMore.value = true;
        try {
            page.value += 1;
        } finally {
            loadingMore.value = false;
        }
    }

    function setActiveCategory(category: Category): void {
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
        formVisible.value = true;
    }

    function openEditForm(item: MediaItem): void {
        editingItem.value = item;
        formVisible.value = true;
    }

    function closeForm(): void {
        formVisible.value = false;
        editingItem.value = null;
    }

    async function save(values: MediaFormValues): Promise<void> {
        try {
            let saved: MediaItem;
            if (editingItem.value) {
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
        loadMore,
        clearFilters,
        setActiveCategory,
        openCreateForm,
        openEditForm,
        closeForm,
        save,
        remove,
    };
});
