import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import type {
    MediaCreateInput,
    MediaItem,
    MediaQueryParams,
    MediaType,
    MediaUpdateInput,
    MediaStatus,
} from '@/models/media';
import { mediaService } from '@/services/mediaService';

export const useMediaStore = defineStore('media', () => {
    const items = ref<MediaItem[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const formVisible = ref(false);
    const editingItem = ref<MediaItem | null>(null);

    // Filters
    const selectedTypes = ref<MediaType[]>([]);
    const selectedStatuses = ref<MediaStatus[]>([]);
    const ratingMin = ref<number>(0);
    const ratingMax = ref<number>(100);
    const search = ref<string>('');

    // Category navigation state
    const activeCategory = ref<'all' | MediaType>('all');

    const queryParams = computed<MediaQueryParams>(() => ({
        // backend accepts only a single type; when a single is selected we pass it for server-side filtering
        types: selectedTypes.value.length === 1 ? selectedTypes.value : undefined,
        status: selectedStatuses.value.length ? selectedStatuses.value : undefined,
        rating_min: ratingMin.value > 0 ? ratingMin.value : undefined,
        rating_max: ratingMax.value < 100 ? ratingMax.value : undefined,
        search: search.value || undefined,
        sort: 'updated_at',
        order: 'desc',
    }));

    const hasActiveFilters = computed(() =>
        !!(
            // do not consider selectedTypes; type is controlled via category
            selectedStatuses.value.length ||
            ratingMin.value > 0 ||
            ratingMax.value < 100 ||
            search.value
        )
    );

    // Server-side filtering: Apply client-side filters only for multiple types/statuses
    // since backend only supports single type/status per request
    const filteredItems = computed<MediaItem[]>(() => {
        let data = items.value.slice();

        // Active category single-type view
        if (activeCategory.value !== 'all') {
            data = data.filter(i => i.media_type === activeCategory.value);
        }

        // Client-side filter for multiple types (backend only supports single type)
        if (selectedTypes.value.length > 1) {
            const set = new Set(selectedTypes.value);
            data = data.filter(i => set.has(i.media_type));
        }

        // Client-side filter for multiple statuses (backend only supports single status)
        if (selectedStatuses.value.length > 1) {
            const set = new Set(selectedStatuses.value);
            data = data.filter(i => set.has(i.status));
        }

        // Note: rating and search filters are now handled server-side
        return data;
    });

    async function load() {
        loading.value = true;
        error.value = null;
        try {
            items.value = await mediaService.list(queryParams.value);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load media';
            items.value = [];
        } finally {
            loading.value = false;
        }
    }

    async function create(payload: MediaCreateInput) {
        loading.value = true;
        error.value = null;
        try {
            const created = await mediaService.create(payload);
            items.value = [created, ...items.value];
            return created;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to create media';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function update(id: string, type: MediaType, payload: MediaUpdateInput) {
        loading.value = true;
        error.value = null;
        try {
            const updated = await mediaService.update(id, type, payload);
            items.value = items.value.map((i) => (i.id === id ? updated : i));
            return updated;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to update media';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function remove(id: string, type: MediaType) {
        loading.value = true;
        error.value = null;
        try {
            await mediaService.remove(id, type);
            items.value = items.value.filter((i) => i.id !== id);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to delete media';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    function openCreateForm() {
        editingItem.value = null;
        formVisible.value = true;
    }

    function openEditForm(item: MediaItem) {
        editingItem.value = item;
        formVisible.value = true;
    }

    function closeForm() {
        formVisible.value = false;
        editingItem.value = null;
    }

    function clearFilters() {
        // Keep type selection in sync with category
        selectedTypes.value = activeCategory.value === 'all' ? [] : [activeCategory.value];
        selectedStatuses.value = [];
        ratingMin.value = 0;
        ratingMax.value = 100;
        search.value = '';
    }

    function setActiveCategory(type: 'all' | MediaType) {
        activeCategory.value = type;
        if (type === 'all') {
            selectedTypes.value = [];
        } else {
            selectedTypes.value = [type];
        }
    }

    return {
        // state
        items,
        filteredItems,
        loading,
        error,
        formVisible,
        editingItem,
        // filters
        selectedTypes,
        selectedStatuses,
        ratingMin,
        ratingMax,
        search,
        queryParams,
        hasActiveFilters,
        activeCategory,
        // actions
        load,
        create,
        update,
        remove,
        openCreateForm,
        openEditForm,
        closeForm,
        clearFilters,
        setActiveCategory,
    };
});
