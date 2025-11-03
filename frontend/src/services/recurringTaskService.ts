import type {
    RecurringTask,
    RecurringTaskCreateInput,
    RecurringTaskUpdateInput
} from "@/models/recurringTask";
import apiClient from "./apiClient";

const API_URL = "/api/v1/recurring-tasks";

interface GetRecurringTasksParams {
    project_id?: string;
    include_inactive?: boolean;
}

export const recurringTaskService = {
    async getRecurringTasks(params?: GetRecurringTasksParams): Promise<RecurringTask[]> {
        const queryParams: Record<string, unknown> = {};
        if (params?.project_id) {
            queryParams.project_id = params.project_id;
        }
        if (typeof params?.include_inactive === "boolean") {
            queryParams.include_inactive = params.include_inactive;
        }

        const response = await apiClient.get(API_URL, {
            params: Object.keys(queryParams).length ? queryParams : undefined
        });
        return response.data;
    },

    async getRecurringTask(recurringTaskId: string): Promise<RecurringTask> {
        const response = await apiClient.get(`${API_URL}/${recurringTaskId}`);
        return response.data;
    },

    async createRecurringTask(payload: RecurringTaskCreateInput): Promise<RecurringTask> {
        const response = await apiClient.post(API_URL, payload);
        return response.data;
    },

    async updateRecurringTask(
        recurringTaskId: string,
        updates: RecurringTaskUpdateInput
    ): Promise<RecurringTask> {
        const response = await apiClient.patch(`${API_URL}/${recurringTaskId}`, updates);
        return response.data;
    },

    async deleteRecurringTask(recurringTaskId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${recurringTaskId}`);
    },

    async pauseRecurringTask(recurringTaskId: string): Promise<RecurringTask> {
        const response = await apiClient.post(`${API_URL}/${recurringTaskId}/pause`);
        return response.data;
    },

    async resumeRecurringTask(recurringTaskId: string): Promise<RecurringTask> {
        const response = await apiClient.post(`${API_URL}/${recurringTaskId}/resume`);
        return response.data;
    }
};
