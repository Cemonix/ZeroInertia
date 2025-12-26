<template>
    <div class="priority-pie-chart">
        <div v-if="loading" class="chart-skeleton">
            <div class="skeleton-circle"></div>
        </div>
        <div v-else-if="!data || data.length === 0" class="chart-empty">
            <FontAwesomeIcon :icon="['fas', 'chart-pie']" />
            <p>No priority distribution data</p>
        </div>
        <div v-else ref="chartContainer" class="chart-container"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from "vue";
import * as d3 from "d3";
import type { PriorityDistribution } from "@/models/statistics";

interface Props {
    data: PriorityDistribution[];
    loading?: boolean;
    size?: number;
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
    size: 300,
});

const chartContainer = ref<HTMLElement | null>(null);
let resizeObserver: ResizeObserver | null = null;

const priorityColors: Record<string, string> = {
    High: "#ef4444",
    Medium: "#f59e0b",
    Low: "#3b82f6",
    None: "#9ca3af",
};

function renderChart() {
    if (!chartContainer.value || !props.data.length) return;

    const container = chartContainer.value;
    d3.select(container).selectAll("*").remove();

    const width = Math.min(container.clientWidth, props.size);
    const height = width;
    const radius = Math.min(width, height) / 2 - 20;
    const innerRadius = radius * 0.6;

    const svg = d3
        .select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("role", "img")
        .attr("aria-label", "Priority distribution donut chart");

    const chart = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);

    const color = d3.scaleOrdinal<string>().range(props.data.map((d) => priorityColors[d.priority_name] || "#64748b"));

    const pie = d3
        .pie<PriorityDistribution>()
        .value((d) => d.completed_count)
        .sort(null);

    const arc = d3.arc<d3.PieArcDatum<PriorityDistribution>>().innerRadius(innerRadius).outerRadius(radius);

    const arcHover = d3
        .arc<d3.PieArcDatum<PriorityDistribution>>()
        .innerRadius(innerRadius)
        .outerRadius(radius + 10);

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

    const arcs = chart
        .selectAll(".arc")
        .data(pie(props.data))
        .enter()
        .append("g")
        .attr("class", "arc");

    arcs.append("path")
        .attr("fill", (d) => color(d.data.priority_name))
        .attr("stroke", "var(--p-content-background)")
        .attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("mouseover", function (event, d) {
            d3.select(this).transition().duration(200).attr("d", arcHover as any);

            tooltip.transition().duration(200).style("opacity", 1);

            tooltip.html(
                `
                    <div style="font-weight: 600; margin-bottom: 4px; color: ${color(d.data.priority_name)};">
                        ${d.data.priority_name} Priority
                    </div>
                    <div style="color: var(--p-text-muted-color); font-size: 13px;">
                        ${d.data.completed_count} task${d.data.completed_count !== 1 ? "s" : ""}<br/>
                        ${d.data.percentage.toFixed(1)}% of total
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
            d3.select(this).transition().duration(200).attr("d", arc as any);
            tooltip.transition().duration(200).style("opacity", 0);
        })
        .transition()
        .duration(800)
        .attrTween("d", function (d: any) {
            const interpolate = d3.interpolate({ startAngle: 0, endAngle: 0 }, d);
            return function (t: number) {
                return arc(interpolate(t) as any) || "";
            };
        });

    const totalTasks = d3.sum(props.data, (d) => d.completed_count);

    chart
        .append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "-0.2em")
        .style("font-size", "32px")
        .style("font-weight", "700")
        .style("fill", "var(--p-text-color)")
        .text(totalTasks)
        .style("opacity", 0)
        .transition()
        .duration(800)
        .delay(400)
        .style("opacity", 1);

    chart
        .append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "1.2em")
        .style("font-size", "13px")
        .style("fill", "var(--p-text-muted-color)")
        .text("Total Tasks")
        .style("opacity", 0)
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
.priority-pie-chart {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.chart-container {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
}

.chart-skeleton {
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.skeleton-circle {
    width: 250px;
    height: 250px;
    border-radius: 50%;
    background: linear-gradient(
        135deg,
        var(--p-content-background) 25%,
        var(--p-content-hover-background) 50%,
        var(--p-content-background) 75%
    );
    background-size: 200% 200%;
    animation: shimmer 1.5s infinite;
    position: relative;
}

.skeleton-circle::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: var(--p-content-background);
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
