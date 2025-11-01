import type { Label, LabelCreateInput, LabelUpdateInput } from "@/models/label";
import apiClient from "./apiClient";

const API_URL = "/api/v1/labels";

export const labelService = {
    async getLabels(): Promise<Label[]> {
        const response = await apiClient.get(API_URL);
        return response.data;
    },

    async createLabel(payload: LabelCreateInput): Promise<Label> {
        const response = await apiClient.post(API_URL, payload);
        return response.data;
    },

    async updateLabel(labelId: string, updates: LabelUpdateInput): Promise<Label> {
        const response = await apiClient.patch(`${API_URL}/${labelId}`, updates);
        return response.data;
    },

    async deleteLabel(labelId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${labelId}`);
    },
};
