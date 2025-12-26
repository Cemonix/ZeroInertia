import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { streakService } from "@/services/streakService";
import { statisticsService } from "@/services/statisticsService";
import type { StreakStats, StreakCalendarDay } from "@/models/streak";
import type {
    CompletionStatistics,
    DailyCompletionData,
    ProjectStatisticsResponse,
    ProductivityPatternsResponse,
    TrendsResponse,
    DistributionResponse,
    TimePeriod,
    DateRange,
} from "@/models/statistics";
import { startOfWeek, endOfWeek, startOfMonth, endOfMonth, format } from "date-fns";

export const useStatisticsStore = defineStore("statistics", () => {
    const currentStreak = ref(0);
    const longestStreak = ref(0);
    const lastActivityDate = ref<string | null>(null);
    const streakLoading = ref(false);
    const hasLoadedStreak = ref(false);

    const calendarDays = ref<StreakCalendarDay[]>([]);
    const calendarStartDate = ref<string | null>(null);
    const calendarEndDate = ref<string | null>(null);
    const calendarLoading = ref(false);

    const summary = ref<CompletionStatistics | null>(null);
    const summaryLoading = ref(false);

    const selectedPeriod = ref<TimePeriod>("week");
    const customDateRange = ref<DateRange | null>(null);

    const projectStats = ref<ProjectStatisticsResponse | null>(null);
    const projectStatsLoading = ref(false);

    const patterns = ref<ProductivityPatternsResponse | null>(null);
    const patternsLoading = ref(false);

    const trends = ref<TrendsResponse | null>(null);
    const trendsLoading = ref(false);

    const distribution = ref<DistributionResponse | null>(null);
    const distributionLoading = ref(false);

    const weeklyData = ref<DailyCompletionData | null>(null);
    const weeklyDataLoading = ref(false);

    const error = ref<string | null>(null);

    const currentDateRange = computed<DateRange>(() => {
        if (selectedPeriod.value === "custom" && customDateRange.value) {
            return customDateRange.value;
        }

        const now = new Date();
        if (selectedPeriod.value === "week") {
            return {
                start: format(startOfWeek(now, { weekStartsOn: 1 }), "yyyy-MM-dd"),
                end: format(endOfWeek(now, { weekStartsOn: 1 }), "yyyy-MM-dd"),
            };
        } else if (selectedPeriod.value === "month") {
            return {
                start: format(startOfMonth(now), "yyyy-MM-dd"),
                end: format(endOfMonth(now), "yyyy-MM-dd"),
            };
        } else {
            return {
                start: "2020-01-01",
                end: format(now, "yyyy-MM-dd"),
            };
        }
    });

    async function loadStreak() {
        streakLoading.value = true;
        error.value = null;
        try {
            const stats: StreakStats = await streakService.getStreak();
            currentStreak.value = stats.current_streak;
            longestStreak.value = stats.longest_streak;
            lastActivityDate.value = stats.last_activity_date;
            hasLoadedStreak.value = true;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load streak";
        } finally {
            streakLoading.value = false;
        }
    }

    async function loadCalendar(startDate: string, endDate: string) {
        calendarLoading.value = true;
        error.value = null;
        try {
            const response = await streakService.getCalendar({
                start_date: startDate,
                end_date: endDate,
            });
            calendarDays.value = response.days;
            calendarStartDate.value = startDate;
            calendarEndDate.value = endDate;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load calendar";
        } finally {
            calendarLoading.value = false;
        }
    }

    async function loadSummary() {
        summaryLoading.value = true;
        error.value = null;
        try {
            summary.value = await statisticsService.getSummary();
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load summary";
        } finally {
            summaryLoading.value = false;
        }
    }

    async function loadProjectStats() {
        projectStatsLoading.value = true;
        error.value = null;
        try {
            const range = currentDateRange.value;
            projectStats.value = await statisticsService.getProjectStats(range.start, range.end);
        } catch (err) {
            console.error("Error loading project stats:", err);
            error.value = err instanceof Error ? err.message : "Failed to load project stats";
        } finally {
            projectStatsLoading.value = false;
        }
    }

    async function loadPatterns() {
        patternsLoading.value = true;
        error.value = null;
        try {
            patterns.value = await statisticsService.getPatterns();
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load patterns";
        } finally {
            patternsLoading.value = false;
        }
    }

    async function loadTrends(periodType: "week" | "month" = "week") {
        trendsLoading.value = true;
        error.value = null;
        try {
            trends.value = await statisticsService.getTrends(periodType, 8);
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load trends";
        } finally {
            trendsLoading.value = false;
        }
    }

    async function loadDistribution() {
        distributionLoading.value = true;
        error.value = null;
        try {
            const range = currentDateRange.value;
            distribution.value = await statisticsService.getDistribution(range.start, range.end);
        } catch (err) {
            console.error("Error loading distribution:", err);
            error.value = err instanceof Error ? err.message : "Failed to load distribution";
        } finally {
            distributionLoading.value = false;
        }
    }

    async function loadWeeklyData() {
        weeklyDataLoading.value = true;
        error.value = null;
        try {
            const now = new Date();
            const weekStart = format(startOfWeek(now, { weekStartsOn: 1 }), "yyyy-MM-dd");
            const weekEnd = format(endOfWeek(now, { weekStartsOn: 1 }), "yyyy-MM-dd");
            weeklyData.value = await statisticsService.getDailyCompletions(weekStart, weekEnd);
        } catch (err) {
            console.error("Error loading weekly data:", err);
            error.value = err instanceof Error ? err.message : "Failed to load weekly data";
        } finally {
            weeklyDataLoading.value = false;
        }
    }

    function setPeriod(period: TimePeriod) {
        selectedPeriod.value = period;
    }

    function setCustomDateRange(range: DateRange) {
        customDateRange.value = range;
        selectedPeriod.value = "custom";
    }

    async function loadAllStatistics() {
        await Promise.all([
            loadStreak(),
            loadSummary(),
            loadWeeklyData(),
            loadProjectStats(),
            loadPatterns(),
            loadTrends(),
            loadDistribution(),
        ]);
    }

    return {
        currentStreak,
        longestStreak,
        lastActivityDate,
        streakLoading,
        hasLoadedStreak,
        calendarDays,
        calendarStartDate,
        calendarEndDate,
        calendarLoading,
        summary,
        summaryLoading,
        selectedPeriod,
        customDateRange,
        currentDateRange,
        projectStats,
        projectStatsLoading,
        patterns,
        patternsLoading,
        trends,
        trendsLoading,
        distribution,
        distributionLoading,
        weeklyData,
        weeklyDataLoading,
        error,
        loadStreak,
        loadCalendar,
        loadSummary,
        loadWeeklyData,
        loadProjectStats,
        loadPatterns,
        loadTrends,
        loadDistribution,
        setPeriod,
        setCustomDateRange,
        loadAllStatistics,
    };
});

export const useStreakStore = useStatisticsStore;
