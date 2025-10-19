import type { StreakStats } from "@/models/streak";
import apiClient from "./apiClient";

const API_URL = "/api/v1/streaks";

export const streakService = {
    async getStreak(): Promise<StreakStats> {
        const response = await apiClient.get(API_URL);
        return response.data;
    }
};
