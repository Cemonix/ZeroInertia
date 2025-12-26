<template>
    <div class="productivity-patterns-section">
        <h2 class="section-title">Productivity Patterns</h2>

        <div class="highlight-cards" v-if="patterns">
            <div class="highlight-card highlight-primary">
                <div class="highlight-icon">
                    <FontAwesomeIcon icon="sun" />
                </div>
                <div class="highlight-content">
                    <div class="highlight-label">Most Productive Day</div>
                    <div class="highlight-value">{{ patterns.most_productive_day }}</div>
                    <div class="highlight-subtitle" v-if="mostProductiveStats">
                        {{ mostProductiveStats.completed_count }} tasks total
                    </div>
                </div>
            </div>

            <div class="highlight-card highlight-secondary">
                <div class="highlight-icon">
                    <FontAwesomeIcon icon="moon" />
                </div>
                <div class="highlight-content">
                    <div class="highlight-label">Least Productive Day</div>
                    <div class="highlight-value">{{ patterns.least_productive_day }}</div>
                    <div class="highlight-subtitle" v-if="leastProductiveStats">
                        {{ leastProductiveStats.completed_count }} tasks total
                    </div>
                </div>
            </div>
        </div>

        <div class="chart-wrapper">
            <h3 class="chart-title">Tasks Completed by Day of Week</h3>
            <DayOfWeekChart
                :data="patterns?.by_day_of_week || []"
                :loading="loading"
                :highlightBest="true"
                :highlightWorst="true"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ProductivityPatternsResponse } from "@/models/statistics";
import DayOfWeekChart from "./charts/DayOfWeekChart.vue";

interface Props {
    patterns: ProductivityPatternsResponse | null;
    loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
});

const mostProductiveStats = computed(() => {
    if (!props.patterns) return null;
    return props.patterns.by_day_of_week.find((d) => d.day_name === props.patterns!.most_productive_day);
});

const leastProductiveStats = computed(() => {
    if (!props.patterns) return null;
    return props.patterns.by_day_of_week.find((d) => d.day_name === props.patterns!.least_productive_day);
});
</script>

<style scoped>
.productivity-patterns-section {
    margin-bottom: 32px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0 0 20px 0;
}

.highlight-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.highlight-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    border-radius: 12px;
    border: 2px solid;
}

.highlight-primary {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.05) 100%);
    border-color: #3b82f6;
}

.highlight-secondary {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(109, 40, 217, 0.05) 100%);
    border-color: #8b5cf6;
}

.highlight-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.highlight-primary .highlight-icon {
    background: #3b82f6;
}

.highlight-secondary .highlight-icon {
    background: #8b5cf6;
}

.highlight-icon i {
    font-size: 20px;
    color: white;
}

.highlight-content {
    flex: 1;
    min-width: 0;
}

.highlight-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.highlight-primary .highlight-label {
    color: #1d4ed8;
}

.highlight-secondary .highlight-label {
    color: #6d28d9;
}

.highlight-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--p-text-color);
    margin-bottom: 2px;
}

.highlight-subtitle {
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

@media (max-width: 768px) {
    .highlight-cards {
        grid-template-columns: 1fr;
    }
}
</style>
