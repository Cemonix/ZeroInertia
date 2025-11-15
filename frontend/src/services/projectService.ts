import type { Project, ProjectReorderItem } from "@/models/project";
import type { PaginatedResponse, PaginationParams } from "@/models/pagination";
import { buildPaginationQuery, isPaginatedResponse, wrapAsSinglePage } from "@/models/pagination";
import apiClient from "./apiClient";


const API_URL = "/api/v1/projects";

type ProjectCreatePayload = Pick<Project, "title" | "parent_id" | "order_index">;
type ProjectUpdatableFields = Pick<Project, "title" | "parent_id" | "order_index">;

export const projectService = {
    async getProjects(pagination?: PaginationParams): Promise<PaginatedResponse<Project>> {
        const response = await apiClient.get(API_URL, { params: buildPaginationQuery(pagination) });
        const data = response.data as unknown;
        if (isPaginatedResponse<Project>(data)) return data;
        return wrapAsSinglePage((data as Project[]) ?? []);
    },

    async getProjectById(projectId: string): Promise<Project | null> {
        const response = await apiClient.get(`${API_URL}/${projectId}`);
        return response.data;
    },

    async createProject(project: ProjectCreatePayload): Promise<Project> {
        const response = await apiClient.post(API_URL, project);
        return response.data;
    },

    async updateProject(
        projectId: string,
        updates: Partial<ProjectUpdatableFields>,
    ): Promise<Project> {
        const response = await apiClient.patch(`${API_URL}/${projectId}`, updates);
        return response.data;
    },

    async deleteProject(projectId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${projectId}`);
    },

    async reorderProjects(reorderedProjects: ProjectReorderItem[]): Promise<void> {
        await apiClient.patch(`${API_URL}/reorder`, reorderedProjects);
    }
}
