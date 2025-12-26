<template>
    <div class="trends-section">
        <h2 class="section-title">Completion Trends</h2>

        <div class="trend-indicator" v-if="trends">
            <div class="trend-card" :class="`trend-${trends.trend_direction}`">
                <div class="trend-icon">
                    <FontAwesomeIcon :icon="trendIcon" />
                </div>
                <div class="trend-content">
                    <div class="trend-label">Trend Direction</div>
                    <div class="trend-value">{{ trendText }}</div>
                    <div class="trend-subtitle">{{ Math.abs(trends.average_change_percent).toFixed(1) }}% avg period-to-period</div>
                </div>
            </div>
        </div>

        <div class="chart-wrapper">
            <h3 class="chart-title">Tasks Completed Over Time</h3>
            <TrendsLineChart
                :data="trends?.periods || []"
                :loading="loading"
                :trendDirection="trends?.trend_direction || 'stable'"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { TrendsResponse } from "@/models/statistics";
import TrendsLineChart from "./charts/TrendsLineChart.vue";

interface Props {
    trends: TrendsResponse | null;
    loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
});

const trendIcon = computed(() => {
    if (!props.trends) return "minus";
    switch (props.trends.trend_direction) {
        case "up":
            return "arrow-up";
        case "down":
            return "arrow-down";
        default:
            return "minus";
    }
});

const trendText = computed(() => {
    if (!props.trends) return "Stable";
    switch (props.trends.trend_direction) {
        case "up":
            return "Trending Up";
        case "down":
            return "Trending Down";
        default:
            return "Stable";
    }
});
</script>

<style scoped>
.trends-section {
    margin-bottom: 32px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0 0 20px 0;
}

.trend-indicator {
    margin-bottom: 24px;
}

.trend-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    border-radius: 12px;
    border: 2px solid;
    max-width: 400px;
}

.trend-up {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
    border-color: #10b981;
}

.trend-down {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    border-color: #ef4444;
}

.trend-stable {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.05) 100%);
    border-color: #3b82f6;
}

.trend-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.trend-up .trend-icon {
    background: #10b981;
}

.trend-down .trend-icon {
    background: #ef4444;
}

.trend-stable .trend-icon {
    background: #3b82f6;
}

.trend-icon svg {
    font-size: 20px;
    color: white;
    font-weight: bold;
}

.trend-content {
    flex: 1;
}

.trend-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.trend-up .trend-label {
    color: #059669;
}

.trend-down .trend-label {
    color: #dc2626;
}

.trend-stable .trend-label {
    color: #1d4ed8;
}

.trend-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--p-text-color);
    margin-bottom: 2px;
}

.trend-subtitle {
    font-size: 13px;
    color: var(--p-text-muted-color);
}

.chart-wrapper {
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 12px;
    padding: 24px;
}

.chart-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0 0 20px 0;
}
</style>
