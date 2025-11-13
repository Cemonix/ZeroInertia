export interface StreakStats {
    current_streak: number;
    longest_streak: number;
    last_activity_date: string | null;
}

export interface DailyCompletionData {
    daily_counts: Record<string, number>;
    start_date: string;
    end_date: string;
    total_completions: number;
}

export interface StreakCalendarDay {
    /**
     * ISO date string (YYYY-MM-DD).
     */
    date: string;
    /**
     * Number of completed tasks on this date.
     */
    completed_count: number;
}

export interface StreakCalendarResponse {
    start_date: string;
    end_date: string;
    days: StreakCalendarDay[];
}
