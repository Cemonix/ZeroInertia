import type { Task, TaskCreateInput, TaskUpdateInput, TaskReorderItem } from "@/models/task";
import type { PaginatedResponse, PaginationParams } from "@/models/pagination";
import { buildPaginationQuery } from "@/models/pagination";
import apiClient from "./apiClient";

const API_URL = "/api/v1/tasks";

export const taskService = {
    async getTasks(project_id?: string, pagination?: PaginationParams): Promise<PaginatedResponse<Task>> {
        const params: Record<string, unknown> = {};
        if (project_id) params.project_id = project_id;
        const pageParams = buildPaginationQuery(pagination);
        if (pageParams) Object.assign(params, pageParams);
        const response = await apiClient.get<PaginatedResponse<Task>>(API_URL, {
            params,
        });
        return response.data;
    },

    async getTaskById(taskId: string): Promise<Task | null> {
        const response = await apiClient.get(`${API_URL}/${taskId}`);
        return response.data;
    },

    async getTasksByDateRange(dateFrom: Date, dateTo: Date): Promise<Task[]> {
        const response = await apiClient.get<Task[]>(`${API_URL}/by-date`, {
            params: {
                date_from: dateFrom.toISOString(),
                date_to: dateTo.toISOString(),
            },
        });
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
    },

    async getTaskCountsByProject(): Promise<Record<string, number>> {
        const response = await apiClient.get(`${API_URL}/counts`);
        const data = response.data as { counts?: Record<string, number> };
        return data.counts ?? {};
    }
}
