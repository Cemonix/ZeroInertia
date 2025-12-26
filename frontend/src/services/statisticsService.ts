import type {
    CompletionStatistics,
    DailyCompletionData,
    DistributionResponse,
    ProductivityPatternsResponse,
    ProjectStatisticsResponse,
    TrendsResponse,
} from "@/models/statistics";
import apiClient from "./apiClient";

const API_URL = "/api/v1/statistics";

export const statisticsService = {
    async getSummary(): Promise<CompletionStatistics> {
        const response = await apiClient.get(`${API_URL}/summary`);
        return response.data;
    },

    async getProjectStats(startDate: string, endDate: string): Promise<ProjectStatisticsResponse> {
        const response = await apiClient.get(`${API_URL}/projects`, {
            params: { start_date: startDate, end_date: endDate },
        });
        return response.data;
    },

    async getPatterns(): Promise<ProductivityPatternsResponse> {
        const response = await apiClient.get(`${API_URL}/patterns`);
        return response.data;
    },

    async getTrends(periodType: "week" | "month", numPeriods: number = 8): Promise<TrendsResponse> {
        const response = await apiClient.get(`${API_URL}/trends`, {
            params: { period_type: periodType, num_periods: numPeriods },
        });
        return response.data;
    },

    async getDistribution(startDate: string, endDate: string): Promise<DistributionResponse> {
        const response = await apiClient.get(`${API_URL}/distribution`, {
            params: { start_date: startDate, end_date: endDate },
        });
        return response.data;
    },

    async getDailyCompletions(startDate: string, endDate: string): Promise<DailyCompletionData> {
        const response = await apiClient.get(`${API_URL}/daily`, {
            params: { start_date: startDate, end_date: endDate },
        });
        return response.data;
    },
};
