import type { Priority } from "@/models/priority";
import apiClient from "./apiClient";

const API_URL = "/api/v1/priorities";

export const priorityService = {
    async getPriorities(): Promise<Priority[]> {
        const response = await apiClient.get(API_URL);
        return response.data;
    }
}
