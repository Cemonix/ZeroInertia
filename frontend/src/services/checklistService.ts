import type { CheckList, CheckListItem } from "@/models/checklist";
import apiClient from "./apiClient";

const API_URL = "/api/v1/checklists";

export interface CheckListCreateInput {
    task_id: string;
    title: string;
}

export interface CheckListItemCreateInput {
    text: string;
}

export interface CheckListReorderItem {
    id: string;
    order_index: number;
}

export const checklistService = {
    // Checklist CRUD operations
    async getChecklistsByTask(taskId: string): Promise<CheckList[]> {
        const response = await apiClient.get(`${API_URL}`, {
            params: { task_id: taskId }
        });
        return response.data;
    },

    async getChecklistById(checklistId: string): Promise<CheckList> {
        const response = await apiClient.get(`${API_URL}/${checklistId}`);
        return response.data;
    },

    async createChecklist(checklist: CheckListCreateInput): Promise<CheckList> {
        const response = await apiClient.post(API_URL, checklist);
        return response.data;
    },

    async updateChecklist(checklistId: string, updates: Partial<Omit<CheckList, 'id' | 'created_at'>>): Promise<CheckList> {
        const response = await apiClient.patch(`${API_URL}/${checklistId}`, updates);
        return response.data;
    },

    async deleteChecklist(checklistId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${checklistId}`);
    },

    async reorderChecklists(reorderedChecklists: CheckListReorderItem[]): Promise<void> {
        await apiClient.post(`${API_URL}/reorder`, reorderedChecklists);
    },

    // CheckList Item CRUD operations
    async createChecklistItem(checklistId: string, item: CheckListItemCreateInput): Promise<CheckListItem> {
        const response = await apiClient.post(`${API_URL}/${checklistId}/items`, item);
        return response.data;
    },

    async updateChecklistItem(checklistId: string, itemId: string, updates: Partial<Omit<CheckListItem, 'id' | 'created_at'>>): Promise<CheckListItem> {
        const response = await apiClient.patch(`${API_URL}/${checklistId}/items/${itemId}`, updates);
        return response.data;
    },

    async deleteChecklistItem(checklistId: string, itemId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${checklistId}/items/${itemId}`);
    },

    async reorderChecklistItems(checklistId: string, reorderedItems: CheckListReorderItem[]): Promise<void> {
        await apiClient.post(`${API_URL}/${checklistId}/items/reorder`, reorderedItems);
    },
};
