<template>
    <div class="weekly-completion-chart">
        <div v-if="loading" class="chart-skeleton">
            <div class="skeleton-bars">
                <div class="skeleton-bar" v-for="i in 7" :key="i"></div>
            </div>
        </div>
        <div v-else-if="!dailyData || Object.keys(dailyData).length === 0" class="chart-empty">
            <FontAwesomeIcon :icon="['fas', 'calendar-week']" />
            <p>No data for this week</p>
        </div>
        <div v-else ref="chartContainer" class="chart-container"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick, computed } from "vue";
import * as d3 from "d3";
import { startOfWeek, endOfWeek, eachDayOfInterval, format, parseISO } from "date-fns";

interface Props {
    dailyData: Record<string, number>;
    loading?: boolean;
    height?: number;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
    height: 280,
});

const chartContainer = ref<HTMLElement | null>(null);
let resizeObserver: ResizeObserver | null = null;

const weekDays = computed(() => {
    const today = new Date();
    const weekStart = startOfWeek(today, { weekStartsOn: 1 });
    const weekEnd = endOfWeek(today, { weekStartsOn: 1 });

    return eachDayOfInterval({ start: weekStart, end: weekEnd }).map(date => ({
        date,
        dateStr: format(date, 'yyyy-MM-dd'),
        dayName: format(date, 'EEE'),
        count: props.dailyData[format(date, 'yyyy-MM-dd')] || 0
    }));
});

function renderChart() {
    if (!chartContainer.value || weekDays.value.length === 0) return;

    const container = chartContainer.value;
    d3.select(container).selectAll("*").remove();

    const margin = { top: 20, right: 20, bottom: 50, left: 45 };
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
        .attr("aria-label", "Current week task completion bar chart");

    const chart = svg
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const maxCount = d3.max(weekDays.value, (d) => d.count) || 1;

    const xScale = d3
        .scaleBand()
        .domain(weekDays.value.map((d) => d.dayName))
        .range([0, chartWidth])
        .padding(0.3);

    const yScale = d3
        .scaleLinear()
        .domain([0, maxCount])
        .range([chartHeight, 0])
        .nice();

    chart
        .append("g")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(d3.axisBottom(xScale))
        .attr("class", "axis-x")
        .selectAll("text")
        .style("fill", "var(--p-text-color)")
        .style("font-size", "12px")
        .style("font-weight", "500");

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
        .attr("y", -32)
        .attr("x", -chartHeight / 2)
        .attr("text-anchor", "middle")
        .style("fill", "var(--p-text-muted-color)")
        .style("font-size", "11px")
        .text("Tasks");

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

    const today = format(new Date(), 'yyyy-MM-dd');

    const bars = chart
        .selectAll(".bar")
        .data(weekDays.value)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", (d) => xScale(d.dayName) || 0)
        .attr("width", xScale.bandwidth())
        .attr("y", chartHeight)
        .attr("rx", 5)
        .attr("fill", (d) => d.dateStr === today ? "#10b981" : "#3b82f6")
        .style("cursor", "pointer")
        .on("mouseover", function (event, d) {
            d3.select(this).style("opacity", 0.8);
            tooltip.transition().duration(200).style("opacity", 1);

            tooltip.html(
                `
                    <div style="font-weight: 600; margin-bottom: 4px;">${format(d.date, 'EEEE, MMM d')}</div>
                    <div style="color: var(--p-text-muted-color); font-size: 13px;">
                        ${d.count} task${d.count !== 1 ? "s" : ""} completed
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
            d3.select(this).style("opacity", 1);
            tooltip.transition().duration(200).style("opacity", 0);
        });

    bars.transition()
        .duration(800)
        .ease(d3.easeCubicOut)
        .attr("y", (d) => yScale(d.count))
        .attr("height", (d) => chartHeight - yScale(d.count));

    chart
        .selectAll(".bar-label")
        .data(weekDays.value)
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .attr("x", (d) => (xScale(d.dayName) || 0) + xScale.bandwidth() / 2)
        .attr("y", (d) => yScale(d.count) - 6)
        .attr("text-anchor", "middle")
        .style("fill", "var(--p-text-color)")
        .style("font-size", "11px")
        .style("font-weight", "600")
        .style("opacity", 0)
        .text((d) => d.count)
        .transition()
        .duration(800)
        .delay(400)
        .style("opacity", (d) => (d.count > 0 ? 1 : 0));
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

watch(() => props.dailyData, async () => {
    await nextTick();
    renderChart();
}, { deep: true });

watch(() => props.loading, async () => {
    await nextTick();
    renderChart();
});
</script>

<style scoped>
.weekly-completion-chart {
    width: 100%;
}

.chart-container {
    width: 100%;
    position: relative;
}

.chart-skeleton {
    padding: 20px;
}

.skeleton-bars {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    height: 240px;
}

.skeleton-bar {
    flex: 1;
    background: linear-gradient(
        180deg,
        var(--p-content-background) 25%,
        var(--p-content-hover-background) 50%,
        var(--p-content-background) 75%
    );
    background-size: 100% 200%;
    animation: shimmer 1.5s infinite;
    border-radius: 5px;
}

.skeleton-bar:nth-child(1) {
    height: 50%;
}
.skeleton-bar:nth-child(2) {
    height: 70%;
}
.skeleton-bar:nth-child(3) {
    height: 60%;
}
.skeleton-bar:nth-child(4) {
    height: 85%;
}
.skeleton-bar:nth-child(5) {
    height: 75%;
}
.skeleton-bar:nth-child(6) {
    height: 40%;
}
.skeleton-bar:nth-child(7) {
    height: 55%;
}

@keyframes shimmer {
    0% {
        background-position: 0 200%;
    }
    100% {
        background-position: 0 -200%;
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
