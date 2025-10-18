import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useToast } from "primevue/usetoast";
import { projectService } from "@/services/projectService";
import type { ProjectReorderItem } from "@/models/project";
import type { Project } from "@/models/project";

export interface ProjectTreeNode {
    key: string;
    label: string;
    id: string;
    children: ProjectTreeNode[];
}

export const useProjectStore = defineStore("project", () => {
    const projects = ref<Project[]>([]);
    const selectedProjectId = ref<string | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const toast = useToast();

    const getProjectById = computed(() => {
        return (id: string) => projects.value.find((p) => p.id === id);
    });

    const selectedProject = computed(() => {
        return selectedProjectId.value ? getProjectById.value(selectedProjectId.value) : null;
    });

    async function fetchProjects() {
        loading.value = true;
        error.value = null;
        try {
            projects.value = await projectService.getProjects();
        } catch (err) {
            error.value =
                err instanceof Error ? err.message : "Failed to fetch projects";
            console.error("Error fetching projects:", err);
        } finally {
            loading.value = false;
        }
    }

    async function createProject(projectData: Partial<Project>) {
        loading.value = true;
        error.value = null;
        try {
            // Create project at the top (order_index: 0)
            const newProject = await projectService.createProject({
                ...projectData,
                order_index: 0,
                parent_id: projectData.parent_id ?? null,
            } as Project);

            // Add to projects array
            projects.value.push(newProject);

            // Shift other root-level projects down
            const rootProjects = projects.value.filter(
                (p) => p.id !== newProject.id && p.parent_id === null
            );

            if (rootProjects.length > 0) {
                const updates = rootProjects.map((p, index) => ({
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

            return newProject;
        } catch (err) {
            error.value =
                err instanceof Error ? err.message : "Failed to create project";
            console.error("Error creating project:", err);
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
            error.value =
                err instanceof Error ? err.message : "Failed to update project";
            console.error("Error updating project:", err);
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
            projects.value = projects.value.filter((p) => p.id !== id);
        } catch (err) {
            error.value =
                err instanceof Error ? err.message : "Failed to delete project";
            console.error("Error deleting project:", err);
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
                console.error("Error reordering projects:", err);

                // Show error toast
                toast.add({
                    severity: 'error',
                    summary: 'Reorder Failed',
                    detail: 'Failed to save project order. Your changes will not be persisted.',
                    life: 5000
                });

                // Refetch to revert optimistic update
                await fetchProjects();
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
        loading,
        error,
        // Getters
        getProjectById,
        selectedProject,
        // Actions
        fetchProjects,
        createProject,
        updateProject,
        deleteProject,
        handleTreeReorder,
        selectProject,
    };
});
