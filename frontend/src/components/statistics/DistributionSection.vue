<template>
    <div class="distribution-section">
        <h2 class="section-title">Task Distribution</h2>

        <div class="distribution-grid">
            <div class="distribution-card">
                <h3 class="card-subtitle">By Priority</h3>
                <div class="chart-container">
                    <PriorityPieChart :data="distribution?.by_priority || []" :loading="loading" :size="280" />
                </div>
            </div>

            <div class="distribution-card">
                <h3 class="card-subtitle">Top Labels</h3>
                <div class="chart-container">
                    <LabelBarChart :data="distribution?.by_labels || []" :loading="loading" :maxLabels="8" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { DistributionResponse } from "@/models/statistics";
import PriorityPieChart from "./charts/PriorityPieChart.vue";
import LabelBarChart from "./charts/LabelBarChart.vue";

interface Props {
    distribution: DistributionResponse | null;
    loading?: boolean;
}

withDefaults(defineProps<Props>(), {
    loading: false,
});
</script>

<style scoped>
.distribution-section {
    margin-bottom: 32px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0 0 20px 0;
}

.distribution-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

.distribution-card {
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 12px;
    padding: 24px;
}

.card-subtitle {
    font-size: 16px;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0 0 20px 0;
}

.chart-container {
    min-height: 300px;
}

@media (max-width: 968px) {
    .distribution-grid {
        grid-template-columns: 1fr;
    }
}
</style>
