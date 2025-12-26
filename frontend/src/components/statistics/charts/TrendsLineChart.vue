<template>
    <div class="trends-line-chart">
        <div v-if="loading" class="chart-skeleton">
            <div class="skeleton-line"></div>
        </div>
        <div v-else-if="!data || data.length === 0" class="chart-empty">
            <FontAwesomeIcon icon="chart-line" />
            <p>No trend data available</p>
        </div>
        <div v-else ref="chartContainer" class="chart-container"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from "vue";
import * as d3 from "d3";
import type { TrendPeriod } from "@/models/statistics";
import { format, parseISO } from "date-fns";

interface Props {
    data: TrendPeriod[];
    loading?: boolean;
    height?: number;
    trendDirection?: "up" | "down" | "stable";
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
    height: 300,
    trendDirection: "stable",
});

const chartContainer = ref<HTMLElement | null>(null);
let resizeObserver: ResizeObserver | null = null;

function renderChart() {
    if (!chartContainer.value || !props.data.length) return;

    const container = chartContainer.value;
    d3.select(container).selectAll("*").remove();

    const margin = { top: 30, right: 30, bottom: 60, left: 50 };
    const width = container.clientWidth;
    const height = props.height;
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const svg = d3
        .select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("role", "img")
        .attr("aria-label", "Completion trends over time line chart");

    const chart = svg
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const parseDate = (dateStr: string) => parseISO(dateStr);

    const dataWithDates = props.data.map((d) => ({
        ...d,
        date: parseDate(d.period_start),
    }));

    const xScale = d3
        .scaleTime()
        .domain(d3.extent(dataWithDates, (d) => d.date) as [Date, Date])
        .range([0, chartWidth]);

    const maxCount = d3.max(dataWithDates, (d) => d.completed_count) || 0;
    const yScale = d3
        .scaleLinear()
        .domain([0, maxCount])
        .range([chartHeight, 0])
        .nice();

    const xAxis = d3
        .axisBottom(xScale)
        .ticks(Math.min(props.data.length, 6))
        .tickFormat((d) => format(d as Date, "MMM d"));

    chart
        .append("g")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(xAxis)
        .attr("class", "axis-x")
        .selectAll("text")
        .style("fill", "var(--p-text-color)")
        .style("font-size", "11px")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    chart.selectAll(".axis-x path, .axis-x line").style("stroke", "var(--p-content-border-color)");

    chart
        .append("g")
        .call(d3.axisLeft(yScale).ticks(5))
        .attr("class", "axis-y")
        .selectAll("text")
        .style("fill", "var(--p-text-color)");

    chart.selectAll(".axis-y path, .axis-y line").style("stroke", "var(--p-content-border-color)");

    chart
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -35)
        .attr("x", -chartHeight / 2)
        .attr("text-anchor", "middle")
        .style("fill", "var(--p-text-muted-color)")
        .style("font-size", "12px")
        .text("Tasks Completed");

    const lineColor =
        props.trendDirection === "up" ? "#10b981" : props.trendDirection === "down" ? "#ef4444" : "#3b82f6";

    const line = d3
        .line<(typeof dataWithDates)[0]>()
        .x((d) => xScale(d.date))
        .y((d) => yScale(d.completed_count))
        .curve(d3.curveMonotoneX);

    const area = d3
        .area<(typeof dataWithDates)[0]>()
        .x((d) => xScale(d.date))
        .y0(chartHeight)
        .y1((d) => yScale(d.completed_count))
        .curve(d3.curveMonotoneX);

    const gradient = chart
        .append("defs")
        .append("linearGradient")
        .attr("id", "area-gradient")
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "0%")
        .attr("y2", "100%");

    gradient.append("stop").attr("offset", "0%").attr("stop-color", lineColor).attr("stop-opacity", 0.3);

    gradient.append("stop").attr("offset", "100%").attr("stop-color", lineColor).attr("stop-opacity", 0);

    chart
        .append("path")
        .datum(dataWithDates)
        .attr("class", "area")
        .attr("fill", "url(#area-gradient)")
        .attr("d", area);

    const path = chart
        .append("path")
        .datum(dataWithDates)
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke", lineColor)
        .attr("stroke-width", 3)
        .attr("d", line);

    const pathLength = (path.node() as SVGPathElement).getTotalLength();

    path.attr("stroke-dasharray", pathLength + " " + pathLength)
        .attr("stroke-dashoffset", pathLength)
        .transition()
        .duration(1200)
        .ease(d3.easeQuadInOut)
        .attr("stroke-dashoffset", 0);

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

    chart
        .selectAll(".dot")
        .data(dataWithDates)
        .enter()
        .append("circle")
        .attr("class", "dot")
        .attr("cx", (d) => xScale(d.date))
        .attr("cy", (d) => yScale(d.completed_count))
        .attr("r", 0)
        .attr("fill", lineColor)
        .attr("stroke", "var(--p-content-background)")
        .attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("mouseover", function (_event, d) {
            d3.select(this).transition().duration(200).attr("r", 8);

            tooltip.transition().duration(200).style("opacity", 1);

            tooltip.html(
                `
                    <div style="font-weight: 600; margin-bottom: 4px;">
                        ${format(d.date, "MMM d, yyyy")}
                    </div>
                    <div style="color: var(--p-text-muted-color); font-size: 13px;">
                        ${d.completed_count} task${d.completed_count !== 1 ? "s" : ""} completed
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
            d3.select(this).transition().duration(200).attr("r", 5);
            tooltip.transition().duration(200).style("opacity", 0);
        })
        .transition()
        .duration(800)
        .delay((_d, i) => i * 100)
        .attr("r", 5);
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

watch(() => props.trendDirection, async () => {
    await nextTick();
    renderChart();
});
</script>

<style scoped>
.trends-line-chart {
    width: 100%;
}

.chart-container {
    width: 100%;
    position: relative;
}

.chart-skeleton {
    padding: 20px;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.skeleton-line {
    width: 100%;
    height: 200px;
    background: linear-gradient(
        135deg,
        var(--p-content-background) 25%,
        var(--p-content-hover-background) 50%,
        var(--p-content-background) 75%
    );
    background-size: 200% 200%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
    clip-path: polygon(0 80%, 15% 60%, 30% 70%, 45% 40%, 60% 50%, 75% 30%, 90% 45%, 100% 20%, 100% 100%, 0 100%);
}

@keyframes shimmer {
    0% {
        background-position: 200% 200%;
    }
    100% {
        background-position: -200% -200%;
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
