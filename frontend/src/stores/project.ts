import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import { projectService } from "@/services/projectService";
import type { PaginationParams } from "@/models/pagination";
import type { ProjectReorderItem } from "@/models/project";
import type { Project } from "@/models/project";
import { useToast } from "primevue/usetoast";
import type { TreeSelectionKeys } from "primevue/tree";

export const useProjectStore = defineStore("project", () => {
    const toast = useToast();

    const projects = ref<Project[]>([]);
    const selectedProjectId = ref<string | null>(null);
    const selectedProject = ref<TreeSelectionKeys | undefined>(undefined);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const getProjectById = (id: string) => {
        return projects.value.find((p) => p.id === id);
    };

    const inboxProject = computed(() => {
        return projects.value.find((p) => p.is_inbox) ?? null;
    });

    const selectedProjectDetails = computed(() => {
        return selectedProjectId.value ? getProjectById(selectedProjectId.value) : null;
    });

    watch(selectedProject, (newSelection) => {
        const nextId = newSelection && Object.keys(newSelection).length > 0
            ? Object.keys(newSelection)[0]
            : null;
        if (selectedProjectId.value !== nextId) {
            selectedProjectId.value = nextId;
        }
    });

    watch(selectedProjectId, (newId) => {
        const currentSelectedId = selectedProject.value && Object.keys(selectedProject.value).length > 0
            ? Object.keys(selectedProject.value)[0]
            : null;

        if (newId && currentSelectedId !== newId) {
            selectedProject.value = { [newId]: true };
        } else if (!newId && selectedProject.value) {
            selectedProject.value = undefined;
        }
    });

    async function loadProjects(pagination: PaginationParams = { page: 1, page_size: 500 }) {
        loading.value = true;
        error.value = null;
        try {
            const resp = await projectService.getProjects(pagination);
            projects.value = resp.items;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load projects";
        } finally {
            loading.value = false;
        }
    }

    async function createProject(projectData: Partial<Project>) {
        loading.value = true;
        error.value = null;
        try {
            // Use provided order_index, or default to 0 (top)
            const orderIndex = projectData.order_index ?? 0;
            const parentId = projectData.parent_id ?? null;

            // Create project at the specified position
            const newProject = await projectService.createProject({
                title: projectData.title as string,
                order_index: orderIndex,
                parent_id: parentId,
            });

            // Only shift siblings if creating at the top (order_index 0)
            // For custom positions, the caller should handle shifting
            if (orderIndex === 0) {
                // Shift other projects with same parent down
                const siblings = projects.value
                    .filter((p) => p.parent_id === parentId)
                    .sort((a, b) => a.order_index - b.order_index);

                if (siblings.length > 0) {
                    const updates = siblings.map((p, index) => ({
                        id: p.id,
                        parent_id: p.parent_id,
                        order_index: index + 1,
                    }));

                    // Update local state
                    updates.forEach((update) => {
                        const project = projects.value.find((p) => p.id === update.id);
                        if (project) {
                            project.order_index = update.order_index;
                        }
                    });

                    await projectService.reorderProjects(updates);
                }
            }

            // Add new project to the array
            projects.value.push(newProject);

            return newProject;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to create project";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateProject(id: string, projectData: Partial<Project>) {
        loading.value = true;
        error.value = null;
        try {
            const updatedProject = await projectService.updateProject(
                id,
                projectData
            );
            const index = projects.value.findIndex((p) => p.id === id);
            if (index !== -1) {
                projects.value[index] = updatedProject;
            }
            return updatedProject;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to update project";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteProject(id: string) {
        loading.value = true;
        error.value = null;
        try {
            await projectService.deleteProject(id);
            const idsToRemove = new Set<string>();
            const queue: string[] = [id];

            while (queue.length > 0) {
                const currentId = queue.shift() as string;
                idsToRemove.add(currentId);

                projects.value
                    .filter((project) => project.parent_id === currentId)
                    .forEach((child) => queue.push(child.id));
            }

            projects.value = projects.value.filter((project) => !idsToRemove.has(project.id));

            if (selectedProjectId.value && idsToRemove.has(selectedProjectId.value)) {
                selectedProjectId.value = null;
            }
            if (selectedProject.value) {
                const currentId = Object.keys(selectedProject.value)[0];
                if (currentId && idsToRemove.has(currentId)) {
                    selectedProject.value = undefined;
                }
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to delete project";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    let reorderTimeout: ReturnType<typeof setTimeout> | null = null;
    let pendingReorders = new Map<string, ProjectReorderItem>();

    async function handleTreeReorder(flattenedTree: ProjectReorderItem[]) {
        // Update local projects array optimistically
        flattenedTree.forEach((update) => {
            const project = projects.value.find((p) => p.id === update.id);
            if (project) {
                project.parent_id = update.parent_id;
                project.order_index = update.order_index;
            }
        });

        // Add to pending reorders (using project ID as key to avoid duplicates)
        flattenedTree.forEach((item) => {
            pendingReorders.set(item.id, item);
        });

        // Debounce the API call
        if (reorderTimeout) {
            clearTimeout(reorderTimeout);
        }

        reorderTimeout = setTimeout(async () => {
            const reordersToSend = Array.from(pendingReorders.values());
            pendingReorders.clear();

            try {
                await projectService.reorderProjects(reordersToSend);
            } catch (err) {
                error.value = err instanceof Error ? err.message : "Failed to reorder projects";

                // Show error toast
                toast.add({
                    severity: 'error',
                    summary: 'Reorder Failed',
                    detail: 'Failed to save project order. Your changes will not be persisted.',
                    life: 5000
                });

                // Refetch to revert optimistic update
                await loadProjects();
            }
        }, 1500);
    }

    function selectProject(projectId: string | null) {
        selectedProjectId.value = projectId;
    }

    return {
        // State
        projects,
        selectedProjectId,
        selectedProject,
        loading,
        error,
        // Getters
        getProjectById,
        selectedProjectDetails,
        inboxProject,
        // Actions
        loadProjects,
        createProject,
        updateProject,
        deleteProject,
        handleTreeReorder,
        selectProject,
    };
});
