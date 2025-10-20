import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Section, SectionReorderItem } from '@/models/section';
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

    async function deleteSection(sectionId: string) {
        loading.value = true;
        error.value = null;
        try {
            await sectionService.deleteSection(sectionId);
            sections.value = sections.value.filter(section => section.id !== sectionId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to delete section';
            console.error('Error deleting section:', err);
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function reorderSections(reorderedSectionIds: string[]) {
        // Optimistically update the local state
        const reorderedSections = reorderedSectionIds.map(id =>
            sections.value.find(s => s.id === id)
        ).filter(Boolean) as Section[];

        // Update order_index for each section
        reorderedSections.forEach((section, index) => {
            const sectionIndex = sections.value.findIndex(s => s.id === section.id);
            if (sectionIndex !== -1) {
                sections.value[sectionIndex] = { ...section, order_index: index };
            }
        });

        // Prepare the reorder payload
        const reorderPayload: SectionReorderItem[] = reorderedSectionIds.map((id, index) => {
            const section = sections.value.find(s => s.id === id);
            return {
                id,
                project_id: section!.project_id,
                order_index: index,
            };
        });

        try {
            await sectionService.reorderSections(reorderPayload);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to reorder sections';
            console.error('Error reordering sections:', err);
            // Reload sections to restore correct order on failure
            const projectId = reorderedSections[0]?.project_id;
            if (projectId) {
                await loadsSectionsForProject(projectId);
            }
            throw err;
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
        deleteSection,
        reorderSections,
        clearSections,
    };
});
