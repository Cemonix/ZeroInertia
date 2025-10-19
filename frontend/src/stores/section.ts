import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Section } from '@/models/section';
import { sectionService } from '@/services/sectionService';

export const useSectionStore = defineStore('section', () => {
    const sections = ref<Section[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    // Computed getter for sections sorted by order_index
    const sortedSections = computed(() => {
        return [...sections.value].sort((a, b) => a.order_index - b.order_index);
    });

    async function loadsSectionsForProject(projectId: string) {
        loading.value = true;
        error.value = null;
        try {
            sections.value = await sectionService.getSections(projectId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load sections';
            console.error('Error loading sections:', err);
            sections.value = [];
        } finally {
            loading.value = false;
        }
    }

    async function createSection(sectionData: Partial<Section>) {
        loading.value = true;
        error.value = null;
        try {
            const newSection = await sectionService.createSection(sectionData as Section);
            sections.value.push(newSection);
            return newSection;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to create section';
            console.error('Error creating section:', err);
            throw err;
        } finally {
            loading.value = false;
        }
    }

    function clearSections() {
        sections.value = [];
    }

    return {
        sections,
        sortedSections,
        loading,
        error,
        loadsSectionsForProject,
        createSection,
        clearSections,
    };
});
