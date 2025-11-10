<template>
    <Dialog
        v-model:visible="isVisible"
        modal
        :header="'Keyboard & Mouse Shortcuts'"
        :style="{ width: '34rem' }"
        :dismissableMask="true"
    >
        <div class="shortcuts-content">
            <section class="section">
                <h4>Kanban Navigation</h4>
                <ul>
                    <li>
                        <span class="keys">
                            <span class="kbd">Shift</span>
                            <span class="join">+</span>
                            <span class="kbd">Scroll</span>
                        </span>
                        <span class="desc">Scroll horizontally across columns</span>
                    </li>
                    <li>
                        <span class="keys">
                            <span class="kbd">Middle Drag</span>
                        </span>
                        <span class="desc">Click and drag to pan horizontally</span>
                    </li>
                    <li>
                        <span class="keys">
                            <span class="kbd">Alt</span>
                            <span class="join">+</span>
                            <span class="kbd">Left Drag</span>
                        </span>
                        <span class="desc">Pan horizontally (Cmd/Ctrl also works)</span>
                    </li>
                </ul>
            </section>

            <section class="section">
                <h4>Planned</h4>
                <ul>
                    <li>
                        <span class="keys">
                            <span class="kbd">Ctrl</span>
                            <span class="join">/</span>
                        </span>
                        <span class="desc">Open shortcuts help</span>
                        <Tag value="Coming Soon" severity="secondary" />
                    </li>
                    <li>
                        <span class="keys">
                            <span class="kbd">Ctrl</span>
                            <span class="join">+</span>
                            <span class="kbd">N</span>
                        </span>
                        <span class="desc">Quick add task</span>
                        <Tag value="Coming Soon" severity="secondary" />
                    </li>
                    <li>
                        <span class="keys">
                            <span class="kbd">Ctrl</span>
                            <span class="join">+</span>
                            <span class="kbd">K</span>
                        </span>
                        <span class="desc">Command palette</span>
                        <Tag value="Coming Soon" severity="secondary" />
                    </li>
                </ul>
            </section>
        </div>
    </Dialog>
    
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ visible: boolean }>();
const emit = defineEmits<{ (e: 'update:visible', value: boolean): void }>();

const isVisible = computed({
    get: () => props.visible,
    set: (v: boolean) => emit('update:visible', v),
});
</script>

<style scoped>
.shortcuts-content {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.section h4 {
    margin: 0 0 0.5rem 0;
    color: var(--p-text-color);
}

.section ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.section li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    background: var(--p-content-hover-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
}

.keys {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

.join {
    color: var(--p-text-muted-color);
}

.desc {
    color: var(--p-text-muted-color);
    font-size: 0.9375rem;
}

.kbd {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.15rem 0.4rem;
    min-width: 1.5rem;
    height: 1.4rem;
    border-radius: 6px;
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    box-shadow: inset 0 -1px 0 0 var(--p-content-border-color);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 0.85rem;
    color: var(--p-text-color);
}
</style>

