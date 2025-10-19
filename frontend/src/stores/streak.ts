import { defineStore } from 'pinia';
import { ref } from 'vue';
import { streakService } from '@/services/streakService';
import type { StreakStats } from '@/models/streak';

export const useStreakStore = defineStore('streak', () => {
    const currentStreak = ref(0);
    const longestStreak = ref(0);
    const lastActivityDate = ref<string | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);

    async function loadStreak() {
        loading.value = true;
        error.value = null;
        try {
            const stats: StreakStats = await streakService.getStreak();
            currentStreak.value = stats.current_streak;
            longestStreak.value = stats.longest_streak;
            lastActivityDate.value = stats.last_activity_date;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load streak';
            console.error('Error loading streak:', err);
        } finally {
            loading.value = false;
        }
    }

    return {
        currentStreak,
        longestStreak,
        lastActivityDate,
        loading,
        error,
        loadStreak,
    };
});
