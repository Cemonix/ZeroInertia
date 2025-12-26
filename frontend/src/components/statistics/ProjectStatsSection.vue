<template>
    <div class="project-stats-section">
        <h2 class="section-title">Project Performance</h2>

        <div class="highlight-cards" v-if="projectStats && projectStats.projects.length > 0">
            <div class="highlight-card highlight-success">
                <div class="highlight-icon">
                    <FontAwesomeIcon icon="arrow-up" />
                </div>
                <div class="highlight-content">
                    <div class="highlight-label">Most Productive</div>
                    <div class="highlight-value">{{ mostProductiveProject?.project_title || "N/A" }}</div>
                    <div class="highlight-subtitle" v-if="mostProductiveProject">
                        {{ mostProductiveProject.completed_count }} task{{
                            mostProductiveProject.completed_count !== 1 ? "s" : ""
                        }}
                    </div>
                </div>
            </div>

            <div class="highlight-card highlight-warning">
                <div class="highlight-icon">
                    <FontAwesomeIcon icon="arrow-down" />
                </div>
                <div class="highlight-content">
                    <div class="highlight-label">Least Focused</div>
                    <div class="highlight-value">{{ leastProductiveProject?.project_title || "N/A" }}</div>
                    <div class="highlight-subtitle" v-if="leastProductiveProject">
                        {{ leastProductiveProject.completed_count }} task{{
                            leastProductiveProject.completed_count !== 1 ? "s" : ""
                        }}
                    </div>
                </div>
            </div>
        </div>

        <div class="chart-wrapper">
            <h3 class="chart-title">Tasks Completed by Project</h3>
            <ProjectStatsChart :data="projectStats?.projects || []" :loading="loading" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ProjectStatisticsResponse } from "@/models/statistics";
import ProjectStatsChart from "./charts/ProjectStatsChart.vue";

interface Props {
    projectStats: ProjectStatisticsResponse | null;
    loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
});

const mostProductiveProject = computed(() => {
    if (!props.projectStats || props.projectStats.projects.length === 0) return null;
    return props.projectStats.projects[0];
});

const leastProductiveProject = computed(() => {
    if (!props.projectStats || props.projectStats.projects.length === 0) return null;
    return props.projectStats.projects[props.projectStats.projects.length - 1];
});
</script>

<style scoped>
.project-stats-section {
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

.highlight-success {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
    border-color: #10b981;
}

.highlight-warning {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    border-color: #ef4444;
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

.highlight-success .highlight-icon {
    background: #10b981;
}

.highlight-warning .highlight-icon {
    background: #ef4444;
}

.highlight-icon svg {
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

.highlight-success .highlight-label {
    color: #059669;
}

.highlight-warning .highlight-label {
    color: #dc2626;
}

.highlight-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--p-text-color);
    margin-bottom: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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
