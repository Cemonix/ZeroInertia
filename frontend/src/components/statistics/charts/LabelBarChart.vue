<template>
    <div class="label-bar-chart">
        <div v-if="loading" class="chart-skeleton">
            <div class="skeleton-bar" v-for="i in 5" :key="i"></div>
        </div>
        <div v-else-if="!data || data.length === 0" class="chart-empty">
            <FontAwesomeIcon :icon="['fas', 'calendar']" />
            <p>No label distribution data</p>
        </div>
        <div v-else ref="chartContainer" class="chart-container"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from "vue";
import * as d3 from "d3";
import type { LabelDistribution } from "@/models/statistics";

interface Props {
    data: LabelDistribution[];
    loading?: boolean;
    height?: number;
    maxLabels?: number;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
    height: 350,
    maxLabels: 10,
});

const chartContainer = ref<HTMLElement | null>(null);
let resizeObserver: ResizeObserver | null = null;

function renderChart() {
    if (!chartContainer.value || !props.data.length) return;

    const container = chartContainer.value;
    d3.select(container).selectAll("*").remove();

    const displayData = props.data.slice(0, props.maxLabels);

    const margin = { top: 20, right: 30, bottom: 40, left: 160 };
    const width = container.clientWidth;
    const height = Math.max(displayData.length * 45, 250);
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const svg = d3
        .select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("role", "img")
        .attr("aria-label", "Label distribution horizontal bar chart");

    const chart = svg
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3
        .scaleLinear()
        .domain([0, d3.max(displayData, (d) => d.completed_count) || 0])
        .range([0, chartWidth])
        .nice();

    const yScale = d3
        .scaleBand()
        .domain(displayData.map((d) => d.label_name))
        .range([0, chartHeight])
        .padding(0.25);

    chart
        .append("g")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(d3.axisBottom(xScale).ticks(5))
        .attr("class", "axis-x")
        .selectAll("text")
        .style("fill", "var(--p-text-color)");

    chart.selectAll(".axis-x path, .axis-x line").style("stroke", "var(--p-content-border-color)");

    chart
        .append("g")
        .call(d3.axisLeft(yScale))
        .attr("class", "axis-y")
        .selectAll("text")
        .style("fill", "var(--p-text-color)")
        .style("font-size", "12px");

    chart.selectAll(".axis-y path, .axis-y line").style("stroke", "var(--p-content-border-color)");

    const tooltip = d3
        .select(container)
        .append("div")
        .attr("class", "chart-tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("background", "var(--p-content-background)")
        .style("border", "1px solid var(--p-content-border-color)")
        .style("border-radius", "4px")
        .style("padding", "8px 12px")
        .style("pointer-events", "none")
        .style("box-shadow", "0 2px 8px rgba(0,0,0,0.1)")
        .style("z-index", "1000");

    const bars = chart
        .selectAll(".bar")
        .data(displayData)
        .enter()
        .append("g")
        .attr("class", "bar-group");

    bars.append("rect")
        .attr("class", "bar")
        .attr("x", 0)
        .attr("y", (d) => yScale(d.label_name) || 0)
        .attr("height", yScale.bandwidth())
        .attr("fill", (d) => d.label_color || "#64748b")
        .attr("rx", 4)
        .style("cursor", "pointer")
        .style("opacity", 0.9)
        .on("mouseover", function (_, d) {
            d3.select(this).style("opacity", 0.7);
            tooltip.transition().duration(200).style("opacity", 1);

            tooltip.html(
                `
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <div style="width: 12px; height: 12px; border-radius: 3px; background: ${d.label_color};"></div>
                        <span style="font-weight: 600;">${d.label_name}</span>
                    </div>
                    <div style="color: var(--p-text-muted-color); font-size: 13px;">
                        ${d.completed_count} task${d.completed_count !== 1 ? "s" : ""}<br/>
                        ${d.percentage.toFixed(1)}% of total
                    </div>
                `
            );
        })
        .on("mousemove", function (event) {
            const containerRect = container.getBoundingClientRect();
            const tooltipX = event.clientX - containerRect.left + 10;
            const tooltipY = event.clientY - containerRect.top - 28;

            tooltip.style("left", tooltipX + "px").style("top", tooltipY + "px");
        })
        .on("mouseout", function () {
            d3.select(this).style("opacity", 0.9);
            tooltip.transition().duration(200).style("opacity", 0);
        });

    bars.selectAll("rect")
        .attr("width", 0)
        .transition()
        .duration(800)
        .ease(d3.easeCubicOut)
        .attr("width", (d) => xScale((d as LabelDistribution).completed_count));

    bars.append("text")
        .attr("class", "bar-label")
        .attr("x", (d) => xScale(d.completed_count) + 5)
        .attr("y", (d) => (yScale(d.label_name) || 0) + yScale.bandwidth() / 2)
        .attr("dy", "0.35em")
        .style("fill", "var(--p-text-color)")
        .style("font-size", "12px")
        .style("font-weight", "500")
        .style("opacity", 0)
        .text((d) => d.completed_count)
        .transition()
        .duration(800)
        .delay(400)
        .style("opacity", 1);
}

onMounted(() => {
    if (chartContainer.value) {
        renderChart();

        resizeObserver = new ResizeObserver(() => {
            renderChart();
        });
        resizeObserver.observe(chartContainer.value);
    }
});

onUnmounted(() => {
    if (resizeObserver && chartContainer.value) {
        resizeObserver.unobserve(chartContainer.value);
    }
});

watch(() => props.data, async () => {
    await nextTick();
    renderChart();
}, { deep: true });

watch(() => props.loading, async () => {
    await nextTick();
    renderChart();
});
</script>

<style scoped>
.label-bar-chart {
    width: 100%;
    min-height: 250px;
}

.chart-container {
    width: 100%;
    position: relative;
}

.chart-skeleton {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 20px;
}

.skeleton-bar {
    height: 35px;
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

.skeleton-bar:nth-child(1) {
    width: 85%;
}
.skeleton-bar:nth-child(2) {
    width: 70%;
}
.skeleton-bar:nth-child(3) {
    width: 60%;
}
.skeleton-bar:nth-child(4) {
    width: 50%;
}
.skeleton-bar:nth-child(5) {
    width: 40%;
}

@keyframes shimmer {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

.chart-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    color: var(--p-text-muted-color);
}

.chart-empty i {
    font-size: 48px;
    margin-bottom: 12px;
    opacity: 0.5;
}

.chart-empty p {
    margin: 0;
    font-size: 14px;
}
</style>
