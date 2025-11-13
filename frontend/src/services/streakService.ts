import type {
    DailyCompletionData,
    StreakCalendarDay,
    StreakCalendarResponse,
    StreakStats,
} from "@/models/streak";
import apiClient from "./apiClient";

const API_URL = "/api/v1/streaks";

export const streakService = {
    async getStreak(): Promise<StreakStats> {
        const response = await apiClient.get(API_URL);
        return response.data;
    },

    /**
     * Get daily completed task counts for a date range.
     *
     * Backend contract (implemented in statistics API):
     *   GET /api/v1/statistics/daily?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
     *   -> {
     *        start_date,
     *        end_date,
     *        total_completions,
     *        daily_counts: { "YYYY-MM-DD": number }
     *      }
     */
    async getCalendar(params: { start_date: string; end_date: string }): Promise<StreakCalendarResponse> {
        const response = await apiClient.get<DailyCompletionData>("/api/v1/statistics/daily", {
            params,
        });
        const data = response.data;

        const days: StreakCalendarDay[] = Object.entries(data.daily_counts)
            .map(([date, count]) => ({
                date,
                completed_count: count,
            }))
            .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));

        return {
            start_date: data.start_date,
            end_date: data.end_date,
            days,
        };
    },
};
