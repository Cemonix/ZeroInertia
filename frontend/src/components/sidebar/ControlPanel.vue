<template>
    <div class="control-panel">
        <div class="panel-header">
            <h2 class="panel-title">Control Panel</h2>
        </div>
        <div class="panel-content">
            <Button
                v-for="action in panelActions"
                :key="action.id"
                text
                class="panel-button"
                :class="{ 'panel-button--active': action.id === activeView }"
                @click="selectView(action.id)"
            >
                <FontAwesomeIcon :icon="action.icon" />
                {{ action.label }}
            </Button>
        </div>
    </div>
</template>

<script setup lang="ts">
type ControlPanelView = "today" | "inbox" | "labels" | "filters" | "project";

interface PanelAction {
    id: ControlPanelView;
    label: string;
    icon: string;
}

const props = defineProps<{
    activeView: ControlPanelView;
}>();

const emit = defineEmits<{
    (event: "update:activeView", view: ControlPanelView): void;
}>();

const panelActions: PanelAction[] = [
    { id: "today", label: "Today", icon: "fa fa-calendar" },
    { id: "inbox", label: "Inbox", icon: "fa fa-inbox" },
    { id: "labels", label: "Labels", icon: "fa fa-tag" },
    { id: "filters", label: "Filters", icon: "fa fa-filter" },
];

const selectView = (view: ControlPanelView) => {
    if (view !== props.activeView) {
        emit("update:activeView", view);
    }
};
</script>

<style scoped>
.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1rem 0.75rem 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
}

.panel-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0;
}

.panel-content {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 1rem;
    gap: 0.5rem;
}

.panel-button {
    width: 100%;
    justify-content: flex-start;
    font-size: 1rem;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    transition: background-color 0.2s, color 0.2s;
}

.panel-button--active {
    background-color: var(--p-primary-50);
    color: var(--p-primary-color);
}
</style>
