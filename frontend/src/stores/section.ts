import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Section } from '@/models/section';
import { sectionService } from '@/services/sectionService';

export const useSectionStore = defineStore('section', () => {
    const sections = ref<Section[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    async function fetchSectionsByProject(projectId: string) {
        loading.value = true;
        error.value = null;
        try {
            sections.value = await sectionService.getSections(projectId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to fetch sections';
            console.error('Error fetching sections:', err);
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

    return {
        sections,
        loading,
        error,
        fetchSectionsByProject,
        createSection,
    };
});
