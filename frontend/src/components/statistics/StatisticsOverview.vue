<template>
    <div class="statistics-overview">
        <h2 class="section-title">Overview</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-icon" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)">
                    <FontAwesomeIcon icon="check-circle" />
                </div>
                <div class="metric-content">
                    <div class="metric-label">Total Completed</div>
                    <div class="metric-value">
                        <span v-if="loading" class="metric-skeleton"></span>
                        <span v-else>{{ summary?.total_completed || 0 }}</span>
                    </div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%)">
                    <FontAwesomeIcon icon="calendar-day" />
                </div>
                <div class="metric-content">
                    <div class="metric-label">{{ periodLabel }}</div>
                    <div class="metric-value">
                        <span v-if="loading" class="metric-skeleton"></span>
                        <span v-else>{{ periodCount }}</span>
                    </div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-icon" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%)">
                    <FontAwesomeIcon icon="chart-line" />
                </div>
                <div class="metric-content">
                    <div class="metric-label">Average Per Day</div>
                    <div class="metric-value">
                        <span v-if="loading" class="metric-skeleton"></span>
                        <span v-else>{{ summary?.average_per_day.toFixed(1) || "0.0" }}</span>
                    </div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-icon" style="background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)">
                    <FontAwesomeIcon icon="trophy" />
                </div>
                <div class="metric-content">
                    <div class="metric-label">Best Day</div>
                    <div class="metric-value">
                        <span v-if="loading" class="metric-skeleton"></span>
                        <span v-else>{{ summary?.best_day_count || 0 }}</span>
                    </div>
                    <div class="metric-subtitle" v-if="!loading && summary?.best_day_date">
                        {{ formatBestDay(summary.best_day_date) }}
                    </div>
                </div>
            </div>
        </div>

        <div class="weekly-chart-section" v-if="weeklyData">
            <h3 class="weekly-chart-title">This Week's Activity</h3>
            <div class="weekly-chart-wrapper">
                <WeeklyCompletionChart
                    :dailyData="weeklyData.daily_counts"
                    :loading="weeklyLoading"
                />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { CompletionStatistics, DailyCompletionData, TimePeriod } from "@/models/statistics";
import { format, parseISO } from "date-fns";
import WeeklyCompletionChart from "./charts/WeeklyCompletionChart.vue";

interface Props {
    summary: CompletionStatistics | null;
    loading?: boolean;
    selectedPeriod: TimePeriod;
    weeklyData?: DailyCompletionData | null;
    weeklyLoading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
    weeklyLoading: false,
});

const periodLabel = computed(() => {
    switch (props.selectedPeriod) {
        case "week":
            return "This Week";
        case "month":
            return "This Month";
        case "custom":
            return "Selected Period";
        default:
            return "All Time";
    }
});

const periodCount = computed(() => {
    if (!props.summary) return 0;
    switch (props.selectedPeriod) {
        case "week":
            return props.summary.completed_this_week;
        case "month":
            return props.summary.completed_this_month;
        default:
            return props.summary.total_completed;
    }
});

function formatBestDay(dateStr: string): string {
    try {
        return format(parseISO(dateStr), "MMM d, yyyy");
    } catch {
        return dateStr;
    }
}
</script>

<style scoped>
.statistics-overview {
    margin-bottom: 32px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0 0 20px 0;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
}

.metric-card {
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
}

.metric-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.metric-icon svg {
    font-size: 24px;
    color: white;
}

.metric-content {
    flex: 1;
    min-width: 0;
}

.metric-label {
    font-size: 13px;
    color: var(--p-text-muted-color);
    margin-bottom: 4px;
    font-weight: 500;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--p-text-color);
    line-height: 1.2;
}

.metric-skeleton {
    display: inline-block;
    width: 60px;
    height: 28px;
    background: linear-gradient(
        90deg,
        var(--p-content-background) 25%,
        var(--p-content-hover-background) 50%,
        var(--p-content-background) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
}

.metric-subtitle {
    font-size: 12px;
    color: var(--p-text-muted-color);
    margin-top: 4px;
}

@keyframes shimmer {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

.weekly-chart-section {
    margin-top: 32px;
}

.weekly-chart-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0 0 16px 0;
}

.weekly-chart-wrapper {
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 12px;
    padding: 24px;
}

@media (max-width: 768px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}
</style>
