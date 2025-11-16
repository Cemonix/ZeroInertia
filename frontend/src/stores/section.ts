import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Section, SectionReorderItem } from '@/models/section';
import { sectionService } from '@/services/sectionService';

export const useSectionStore = defineStore('section', () => {
    const sections = ref<Section[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    // Get sections for a specific project, sorted by order_index
    const getSectionsByProject = computed(() => {
        return (projectId: string) =>
            sections.value
                .filter(section => section.project_id === projectId)
                .sort((a, b) => a.order_index - b.order_index);
    });

    // Keep sortedSections for backwards compatibility (across all projects)
    const sortedSections = computed(() => {
        return [...sections.value].sort((a, b) => a.order_index - b.order_index);
    });

    async function loadSectionsForProject(projectId: string) {
        loading.value = true;
        error.value = null;
        try {
            const projectSections = await sectionService.getSections(projectId);
            const others = sections.value.filter(s => s.project_id !== projectId);
            sections.value = [...others, ...projectSections];
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load sections';
            // Keep existing cache on failure to avoid UI flicker
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
            // Reload sections to restore correct order on failure
            const projectId = reorderedSections[0]?.project_id;
            if (projectId) {
                await loadSectionsForProject(projectId);
            }
            throw err;
        }
    }

    async function updateSection(sectionId: string, updates: Partial<Omit<Section, 'id' | 'created_at'>>) {
        loading.value = true;
        error.value = null;
        try {
            const updatedSection = await sectionService.updateSection(sectionId, updates);
            const index = sections.value.findIndex(section => section.id === sectionId);
            if (index !== -1) {
                sections.value[index] = { ...sections.value[index], ...updatedSection };
            }
            return updatedSection;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to update section';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    function clearProjectSections(projectId: string) {
        sections.value = sections.value.filter(s => s.project_id !== projectId);
    }

    function clearSections() {
        sections.value = [];
    }

    return {
        sections,
        sortedSections,
        getSectionsByProject,
        loading,
        error,
        loadSectionsForProject,
        createSection,
        deleteSection,
        updateSection,
        reorderSections,
        clearProjectSections,
        clearSections,
    };
});
