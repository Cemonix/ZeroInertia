import type { Project, ProjectReorderItem } from "@/models/project";
import apiClient from "./apiClient";


const API_URL = "/api/v1/projects";

export const projectService = {
    async getProjects(): Promise<Project[]> {
        const response = await apiClient.get(API_URL);
        return response.data;
    },

    async getProjectById(projectId: string): Promise<Project | null> {
        const response = await apiClient.get(`${API_URL}/${projectId}`);
        return response.data;
    },

    async createProject(project: Project): Promise<Project> {
        const response = await apiClient.post(API_URL, project);
        return response.data;
    },

    async updateProject(projectId: string, updates: Partial<Omit<Project, 'id' | 'created_at'>>): Promise<Project> {
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