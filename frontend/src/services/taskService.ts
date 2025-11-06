import type { Task, TaskCreateInput, TaskUpdateInput, TaskReorderItem } from "@/models/task";
import apiClient from "./apiClient";

const API_URL = "/api/v1/tasks";

export const taskService = {
    async getTasks(project_id?: string): Promise<Task[]> {
        const response = await apiClient.get(API_URL, {
            ...(project_id && { params: { project_id } })
        });
        return response.data;
    },

    async getTaskById(taskId: string): Promise<Task | null> {
        const response = await apiClient.get(`${API_URL}/${taskId}`);
        return response.data;
    },

    async createTask(task: TaskCreateInput): Promise<Task> {
        const response = await apiClient.post(API_URL, task);
        return response.data;
    },

    async updateTask(taskId: string, updates: TaskUpdateInput): Promise<Task> {
        const response = await apiClient.patch(`${API_URL}/${taskId}`, updates);
        return response.data;
    },

    async deleteTask(taskId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${taskId}`);
    },

    async reorderTasks(reorderedTasks: TaskReorderItem[]): Promise<void> {
        await apiClient.post(`${API_URL}/reorder`, reorderedTasks);
    },

    async archiveTask(taskId: string): Promise<void> {
        await apiClient.post(`${API_URL}/${taskId}/archive`);
    },

    async snoozeTask(taskId: string): Promise<Task> {
        const response = await apiClient.post(`${API_URL}/${taskId}/snooze`);
        return response.data;
    }
}
