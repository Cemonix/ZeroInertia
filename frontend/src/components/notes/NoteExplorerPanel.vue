<template>
    <section class="note-panel">
        <header class="panel-header">
            <h2 class="panel-title">Notes</h2>
            <Button
                text
                rounded
                class="header-action"
                aria-label="Create note"
                @click="createRootNote"
            >
                <FontAwesomeIcon icon="plus" />
            </Button>
        </header>
        <div class="panel-body">
            <NoteTree />
        </div>
    </section>
</template>

<script lang="ts" setup>
import { useToast } from "primevue";
import { useNoteStore } from "@/stores/note";
import NoteTree from "./NoteTree.vue";
import Button from "primevue/button";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

const noteStore = useNoteStore();
const toast = useToast();

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
    padding: 0.75rem 0.5rem;
}
</style>
