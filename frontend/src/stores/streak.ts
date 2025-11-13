import { defineStore } from "pinia";
import { ref } from "vue";
import { streakService } from "@/services/streakService";
import type { StreakStats, StreakCalendarDay } from "@/models/streak";

export const useStreakStore = defineStore("streak", () => {
    const currentStreak = ref(0);
    const longestStreak = ref(0);
    const lastActivityDate = ref<string | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const hasLoadedStreak = ref(false);

    const calendarDays = ref<StreakCalendarDay[]>([]);
    const calendarStartDate = ref<string | null>(null);
    const calendarEndDate = ref<string | null>(null);
    const calendarLoading = ref(false);

    async function loadStreak() {
        loading.value = true;
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
            loading.value = false;
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
            error.value = err instanceof Error ? err.message : "Failed to load streak calendar";
        } finally {
            calendarLoading.value = false;
        }
    }

    return {
        currentStreak,
        longestStreak,
        lastActivityDate,
        loading,
        error,
        hasLoadedStreak,
        calendarDays,
        calendarStartDate,
        calendarEndDate,
        calendarLoading,
        loadStreak,
        loadCalendar,
    };
});
