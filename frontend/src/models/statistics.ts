export interface ProjectStatistics {
    project_id: string;
    project_title: string;
    completed_count: number;
    completion_percentage: number;
}

export interface ProjectStatisticsResponse {
    projects: ProjectStatistics[];
    total_completed: number;
    start_date: string;
    end_date: string;
}

export interface DayOfWeekStatistics {
    day_of_week: number;
    day_name: string;
    completed_count: number;
    average_per_week: number;
}

export interface ProductivityPatternsResponse {
    by_day_of_week: DayOfWeekStatistics[];
    most_productive_day: string;
    least_productive_day: string;
}

export interface TrendPeriod {
    period_start: string;
    period_end: string;
    completed_count: number;
}

export interface TrendsResponse {
    periods: TrendPeriod[];
    trend_direction: "up" | "down" | "stable";
    average_change_percent: number;
}

export interface PriorityDistribution {
    priority_id: string | null;
    priority_name: string;
    completed_count: number;
    percentage: number;
}

export interface LabelDistribution {
    label_id: string;
    label_name: string;
    label_color: string;
    completed_count: number;
    percentage: number;
}

export interface DistributionResponse {
    by_priority: PriorityDistribution[];
    by_labels: LabelDistribution[];
    total_completed: number;
}

export interface CompletionStatistics {
    total_completed: number;
    completed_today: number;
    completed_this_week: number;
    completed_this_month: number;
    average_per_day: number;
    best_day_count: number;
    best_day_date: string | null;
}

export type TimePeriod = "week" | "month" | "all" | "custom";

export interface DateRange {
    start: string;
    end: string;
}

export interface DailyCompletionData {
    daily_counts: Record<string, number>;
    start_date: string;
    end_date: string;
    total_completions: number;
}
