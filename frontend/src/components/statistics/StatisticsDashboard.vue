<template>
    <div class="statistics-dashboard">
        <div class="dashboard-header">
            <h1 class="dashboard-title">Statistics & Insights</h1>
            <TimePeriodSelector
                :model-value="statisticsStore.selectedPeriod"
                @update:model-value="handlePeriodChange"
                @custom-range-applied="handleCustomRangeChange"
            />
        </div>

        <div class="dashboard-content">
            <StatisticsOverview
                :summary="statisticsStore.summary"
                :loading="statisticsStore.summaryLoading"
                :selected-period="statisticsStore.selectedPeriod"
                :weeklyData="statisticsStore.weeklyData"
                :weeklyLoading="statisticsStore.weeklyDataLoading"
            />

            <ProjectStatsSection
                :project-stats="statisticsStore.projectStats"
                :loading="statisticsStore.projectStatsLoading"
            />

            <ProductivityPatternsSection
                :patterns="statisticsStore.patterns"
                :loading="statisticsStore.patternsLoading"
            />

            <TrendsSection
                :trends="statisticsStore.trends"
                :loading="statisticsStore.trendsLoading"
                :period-type="trendPeriodType"
            />

            <DistributionSection
                :distribution="statisticsStore.distribution"
                :loading="statisticsStore.distributionLoading"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, watch, computed } from "vue";
import { useStatisticsStore } from "@/stores/statistics";
import type { TimePeriod, DateRange } from "@/models/statistics";
import StatisticsOverview from "./StatisticsOverview.vue";
import ProjectStatsSection from "./ProjectStatsSection.vue";
import ProductivityPatternsSection from "./ProductivityPatternsSection.vue";
import TrendsSection from "./TrendsSection.vue";
import DistributionSection from "./DistributionSection.vue";
import TimePeriodSelector from "./TimePeriodSelector.vue";

const statisticsStore = useStatisticsStore();

const trendPeriodType = computed<"week" | "month">(() => {
    return statisticsStore.selectedPeriod === "month" ? "month" : "week";
});

async function loadData() {
    await statisticsStore.loadAllStatistics();
}

function handlePeriodChange(period: TimePeriod) {
    statisticsStore.setPeriod(period);
}

function handleCustomRangeChange(range: DateRange) {
    statisticsStore.setCustomDateRange(range);
}

watch(
    () => statisticsStore.selectedPeriod,
    async () => {
        await Promise.all([
            statisticsStore.loadProjectStats(),
            statisticsStore.loadDistribution(),
            statisticsStore.loadTrends(trendPeriodType.value),
        ]);
    }
);

watch(
    () => statisticsStore.customDateRange,
    async (newRange) => {
        if (newRange && statisticsStore.selectedPeriod === "custom") {
            await Promise.all([
                statisticsStore.loadProjectStats(),
                statisticsStore.loadDistribution(),
            ]);
        }
    }
);

onMounted(() => {
    loadData();
});
</script>

<style scoped>
.statistics-dashboard {
    display: flex;
    flex-direction: column;
    background: var(--p-surface-ground);
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 32px;
    background: var(--p-content-background);
    border-bottom: 1px solid var(--p-content-border-color);
    flex-shrink: 0;
}

.dashboard-title {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
    color: var(--p-text-color);
}

.dashboard-content {
    flex: 1;
    padding: 32px;
}

.dashboard-content > * + * {
    margin-top: 32px;
}

@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
        padding: 16px 20px;
    }

    .dashboard-title {
        font-size: 24px;
    }

    .dashboard-content {
        padding: 20px;
    }

    .dashboard-content > * + * {
        margin-top: 24px;
    }
}
</style>
