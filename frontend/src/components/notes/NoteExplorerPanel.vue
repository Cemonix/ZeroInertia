<template>
    <section class="note-panel">
        <header class="panel-header">
            <h2 class="panel-title">Notes</h2>
            <div class="header-actions">
                <Button
                    text
                    rounded
                    class="header-action"
                    aria-label="Create note"
                    @click="createRootNote"
                >
                    <FontAwesomeIcon icon="plus" />
                </Button>
                <Button
                    text
                    rounded
                    class="header-action"
                    aria-label="More options"
                    aria-haspopup="true"
                    @click="toggleMenu"
                >
                    <FontAwesomeIcon icon="ellipsis" />
                </Button>
            </div>
        </header>
        <Menu
            ref="menuRef"
            :model="menuItems"
            :popup="true"
            :pt="{ root: { style: { zIndex: 1200 } } }"
        >
            <template #item="{ item }">
                <div class="menu-item-content">
                    <FontAwesomeIcon v-if="item.icon" :icon="item.icon" class="menu-item-icon" />
                    <span>{{ item.label }}</span>
                </div>
            </template>
        </Menu>
        <div class="panel-body">
            <NoteTree ref="noteTreeRef" />
        </div>
    </section>
</template>

<script lang="ts" setup>
import { ref, computed, type Ref, type ComponentPublicInstance } from "vue";
import { useToast } from "primevue";
import { useNoteStore } from "@/stores/note";
import NoteTree from "./NoteTree.vue";
import Button from "primevue/button";
import Menu from "primevue/menu";
import type { MenuItem } from "primevue/menuitem";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

const props = defineProps<{
    showBacklinks: boolean;
}>();

const emit = defineEmits<{
    toggleBacklinks: [];
}>();

type MenuRef = ComponentPublicInstance & {
    toggle: (event: Event) => void;
};

type NoteTreeRef = ComponentPublicInstance & {
    expandAll: () => void;
    collapseAll: () => void;
};

const noteStore = useNoteStore();
const toast = useToast();
const menuRef = ref<MenuRef | null>(null);
const noteTreeRef: Ref<NoteTreeRef | null> = ref(null);

const menuItems = computed<MenuItem[]>(() => [
    {
        label: props.showBacklinks ? 'Hide backlinks' : 'Show backlinks',
        icon: props.showBacklinks ? 'eye-slash' : 'eye',
        command: () => emit("toggleBacklinks"),
    },
    {
        separator: true,
    },
    {
        label: 'Expand all',
        icon: 'angles-down',
        command: () => noteTreeRef.value?.expandAll(),
    },
    {
        label: 'Collapse all',
        icon: 'angles-up',
        command: () => noteTreeRef.value?.collapseAll(),
    },
]);

const createRootNote = async () => {
    try {
        await noteStore.createNote({
            title: "Untitled Note",
            parent_id: null,
            content: "",
        });
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Unable to create note",
            detail: error instanceof Error ? error.message : "Unknown error",
        });
    }
};

const toggleMenu = (event: Event) => {
    menuRef.value?.toggle(event);
};
</script>

<style scoped>
.note-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
}

.panel-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin: 0;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.header-action {
    color: var(--p-primary-color);
    transition: color 0.2s ease, background-color 0.2s ease;
}

.header-action:hover {
    background-color: var(--p-primary-50);
    color: var(--p-primary-600);
}

.panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
}

/* Mobile responsive styles */
@media (max-width: 768px) {
    .panel-header {
        padding: 0.75rem;
    }

    .panel-title {
        font-size: 1rem;
    }

    .panel-body {
        padding: 0.5rem 0.25rem;
    }
}

@media (max-width: 480px) {
    .panel-header {
        padding: 0.625rem 0.75rem;
    }

    .panel-title {
        font-size: 0.9375rem;
    }
}

.menu-item-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem;
    width: 100%;
    cursor: pointer;
    user-select: none;
}

.menu-item-icon {
    width: 1rem;
    color: var(--p-text-muted-color);
}
</style>
