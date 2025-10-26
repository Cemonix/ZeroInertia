import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Priority } from '@/models/priority';
import { priorityService } from '@/services/priorityService';
import { useToast } from 'primevue/usetoast';

export const usePriorityStore = defineStore('priority', () => {
    const toast = useToast();

    const priorities = ref<Priority[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const getPriorityById = computed(() => {
        return (priorityId: string) => priorities.value.find(p => p.id === priorityId) || null;
    });

    async function loadPriorities() {
        loading.value = true;
        error.value = null;
        try {
            priorities.value = await priorityService.getPriorities();
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load priorities';
            toast.add({ severity: "error", summary: "Error", detail: "Failed to load priorities" });
            priorities.value = [];
        } finally {
            loading.value = false;
        }
    }

    return {
        priorities,
        loading,
        error,
        getPriorityById,
        loadPriorities,
    };
});
