<template>
    <div class="streak-board">
        <header class="streak-board-header">
            <div>
                <h1 class="title">Streaks</h1>
                <p class="subtitle">Visualize your consistency and completed tasks over time.</p>
            </div>
            <div class="streak-metrics">
                <div class="metric">
                    <span class="metric-label">Current streak</span>
                    <span class="metric-value">
                        {{ streakStore.currentStreak }}
                        <span class="metric-suffix">days</span>
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Longest streak</span>
                    <span class="metric-value">
                        {{ streakStore.longestStreak }}
                        <span class="metric-suffix">days</span>
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last activity</span>
                    <span class="metric-value">
                        {{ lastActivityText }}
                    </span>
                </div>
            </div>
        </header>

        <StreakCalendar
            :days="calendarDays"
            :loading="calendarLoading"
            :start-date="calendarStartDate"
            :end-date="calendarEndDate"
        />

        <p v-if="error" class="error-text">
            {{ error }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useStreakStore } from "@/stores/streak";
import { useAuthStore } from "@/stores/auth";
import StreakCalendar from "./StreakCalendar.vue";

const streakStore = useStreakStore();
const authStore = useAuthStore();

const calendarDays = computed(() => streakStore.calendarDays);
const calendarLoading = computed(() => streakStore.calendarLoading);
const calendarStartDate = computed(() => streakStore.calendarStartDate || undefined);
const calendarEndDate = computed(() => streakStore.calendarEndDate || undefined);
const error = computed(() => streakStore.error);

const lastActivityText = computed(() => {
    if (!streakStore.lastActivityDate) return "No activity yet";
    const date = new Date(streakStore.lastActivityDate);
    return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
    });
});

const ensureStreakSummaryLoaded = async () => {
    if (!authStore.isAuthenticated) return;
    if (!streakStore.hasLoadedStreak && !streakStore.loading) {
        await streakStore.loadStreak();
    }
};

const ensureCalendarLoaded = async () => {
    if (!authStore.isAuthenticated) return;
    if (streakStore.calendarLoading || streakStore.calendarDays.length > 0) {
        return;
    }

    const today = new Date();
    const currentYear = today.getFullYear();

    // Show full calendar year from Jan 1 to Dec 31
    // Format dates directly to avoid timezone issues with toISOString()
    const start = `${currentYear}-01-01`;
    const end = `${currentYear}-12-31`;

    await streakStore.loadCalendar(start, end);
};

const loadData = async () => {
    await ensureStreakSummaryLoaded();
    await ensureCalendarLoaded();
};

onMounted(() => {
    void loadData();
});

watch(
    () => authStore.isAuthenticated,
    (isAuth) => {
        if (isAuth) {
            void loadData();
        }
    },
);
</script>

<style scoped>
.streak-board {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.streak-board-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1.5rem;
}

.title {
    margin: 0;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--p-text-color);
}

.subtitle {
    margin: 0.25rem 0 0;
    font-size: 0.95rem;
    color: var(--p-text-muted-color);
}

.streak-metrics {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.metric {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    min-width: 8rem;
}

.metric-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--p-text-muted-color);
}

.metric-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--p-text-color);
}

.metric-suffix {
    font-size: 0.85rem;
    font-weight: 400;
    margin-left: 0.15rem;
    color: var(--p-text-muted-color);
}

.error-text {
    margin: 0;
    font-size: 0.9rem;
    color: var(--p-red-500);
}

@media (max-width: 768px) {
    .streak-board-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
