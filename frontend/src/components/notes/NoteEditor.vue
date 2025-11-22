<template>
    <section class="note-editor" v-if="activeNote">
        <header class="editor-header">
            <div class="title-group">
                <InputText
                    v-model="localTitle"
                    placeholder="Untitled note"
                    class="title-input"
                />
                <span class="timestamp">
                    Last updated {{ formatTimestamp(activeNote.updated_at) }}
                </span>
            </div>
            <div class="header-actions">
                <div class="view-toggle">
                    <Button
                        v-for="option in viewOptions"
                        :key="option"
                        :label="option.toUpperCase()"
                        text
                        :class="{ 'view-toggle--active': viewMode === option }"
                        @click="viewMode = option"
                    />
                </div>
                <Button
                    class="save-button"
                    label="Save"
                    :disabled="!isDirty"
                    @click="saveChanges"
                />
            </div>
        </header>
        <div class="editor-body" :class="`editor-body--${viewMode}`">
            <div
                v-if="viewMode !== 'preview'"
                class="editor-pane editor-pane--input"
            >
                <Textarea
                    v-model="localContent"
                    class="content-area"
                    placeholder="Start writing in Markdown..."
                    rows="12"
                />
            </div>
            <div
                v-if="viewMode !== 'edit'"
                class="editor-pane editor-pane--preview"
            >
                <div
                    class="markdown-preview"
                    v-html="renderedMarkdown"
                    @click="handlePreviewClick"
                />
            </div>
        </div>
    </section>
    <section v-else class="note-placeholder">
        <h2>Select or create a note</h2>
        <p>Pick a note from the hierarchy to start editing, or create a new one.</p>
    </section>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from "vue";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import { useToast } from "primevue";
import { parseMarkdown } from "@/core/markdown";
import { useNoteStore } from "@/stores/note";

type ViewMode = "edit" | "preview" | "split";

const noteStore = useNoteStore();
const toast = useToast();

const activeNote = computed(() => noteStore.activeNote);
const viewMode = ref<ViewMode>("split");
const viewOptions: ViewMode[] = ["edit", "split", "preview"];
const localTitle = ref("");
const localContent = ref("");

watch(
    activeNote,
    (note) => {
        localTitle.value = note?.title ?? "";
        localContent.value = note?.content ?? "";
    },
    { immediate: true }
);

const isDirty = computed(() => {
    if (!activeNote.value) return false;
    return (
        activeNote.value.title !== localTitle.value ||
        activeNote.value.content !== localContent.value
    );
});

const renderedMarkdown = computed(() => {
    return parseMarkdown(localContent.value || "");
});

const saveChanges = async () => {
    if (!activeNote.value || !isDirty.value) {
        return;
    }
    try {
        await noteStore.updateNote(activeNote.value.id, {
            title: localTitle.value,
            content: localContent.value,
        });
        toast.add({
            severity: "success",
            summary: "Note saved",
            life: 2000,
        });
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Unable to save note",
            detail: error instanceof Error ? error.message : "Unknown error",
            life: 3000,
        });
    }
};

const formatTimestamp = (isoString: string) => {
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) {
        return "recently";
    }
    return date.toLocaleString();
};

const handlePreviewClick = (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    if (target.classList.contains("wikilink")) {
        const noteTitle = target.getAttribute("data-note-title");
        if (noteTitle) {
            const linkedNote = noteStore.notes.find(
                (note) => note.title.toLowerCase() === noteTitle.toLowerCase()
            );
            if (linkedNote) {
                noteStore.selectNote(linkedNote.id);
            } else {
                toast.add({
                    severity: "warn",
                    summary: "Note not found",
                    detail: `No note with title "${noteTitle}" exists`,
                    life: 3000,
                });
            }
        }
    }
};
</script>

<style scoped>
.note-editor {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--p-content-background);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.editor-header {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--p-content-border-color);
    gap: 0.75rem;
}

.title-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    flex: 1 1 auto;
    min-width: 0;
}

.title-input {
    font-size: 1.5rem;
    font-weight: 600;
}

.timestamp {
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem 0.75rem;
    flex: 1 1 auto;
    flex-wrap: wrap;
    justify-content: flex-start;
    min-width: 0;
    width: 100%;
}

.view-toggle {
    display: flex;
    align-items: center;
    background: var(--p-content-hover-background);
    border-radius: 999px;
    padding: 0.25rem;
    gap: 0.25rem;
    flex: 0 1 auto;
    flex-wrap: nowrap;
    min-width: max-content;
    overflow-x: auto;
    max-width: 100%;
    margin-right: 0.5rem;
}

.view-toggle::-webkit-scrollbar {
    display: none;
}

.view-toggle :deep(.p-button) {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.875rem;
    min-width: 80px;
}

.view-toggle--active {
    background: var(--p-primary-100);
    color: var(--p-primary-color);
}

.save-button {
    margin-left: auto;
    flex-shrink: 0;
}

.editor-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.editor-body--edit .editor-pane--input {
    flex: 1;
}

.editor-body--preview .editor-pane--preview {
    flex: 1;
}

.editor-body--split .editor-pane {
    flex: 1;
}

.editor-pane {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    overflow: hidden;
    min-height: 0;
}

.editor-pane--input {
    border-right: 1px solid var(--p-content-border-color);
}

.content-area {
    width: 100%;
    flex: 1;
    font-family: var(--font-family-monospace, "Fira Code", "SFMono-Regular", monospace);
    resize: none;
    height: 100%;
    min-height: 0;
    overflow-y: auto;
    background-color: var(--p-input-background);
}

.markdown-preview {
    flex: 1;
    overflow-y: auto;
    padding-right: 0.5rem;
    line-height: 1.6;
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3),
.markdown-preview :deep(h4) {
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
}

.markdown-preview :deep(p) {
    margin-bottom: 1rem;
}

.markdown-preview :deep(code) {
    background: var(--p-content-hover-background);
    padding: 0.15rem 0.35rem;
    border-radius: 4px;
    font-family: var(--font-family-monospace, "Fira Code", "SFMono-Regular", monospace);
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
    margin-bottom: 1rem;
    padding-left: 2rem;
}

.markdown-preview :deep(ul) {
    list-style-type: disc;
}

.markdown-preview :deep(ol) {
    list-style-type: decimal;
}

.markdown-preview :deep(li) {
    margin-bottom: 0.5rem;
}

.markdown-preview :deep(li > ul),
.markdown-preview :deep(li > ol) {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

.markdown-preview :deep(pre) {
    background: var(--p-content-hover-background);
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    margin-bottom: 1rem;
}

.markdown-preview :deep(pre code) {
    background: transparent;
    padding: 0;
}

.markdown-preview :deep(.wikilink) {
    color: var(--p-primary-color);
    font-weight: 500;
    cursor: pointer;
    border-bottom: 1px dashed var(--p-primary-color);
    transition: all 0.2s ease;
}

.markdown-preview :deep(.wikilink:hover) {
    background-color: var(--p-primary-100);
    border-bottom-style: solid;
}

.note-placeholder {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: var(--p-text-muted-color);
    border: 2px dashed var(--p-content-border-color);
    border-radius: 12px;
    padding: 2rem;
    background: var(--p-content-background);
    gap: 0.75rem;
}

.note-placeholder h2 {
    margin: 0;
    color: var(--p-text-color);
}

@media (max-width: 768px) {
    .editor-header {
        padding: 0.75rem 1rem;
    }

    .title-input {
        font-size: 1.3rem;
    }
}

@media (max-width: 480px) {
    .editor-header {
        padding: 0.625rem 0.75rem;
        gap: 0.625rem;
    }

    .title-input {
        font-size: 1.125rem;
    }

    /* Force edit mode on very small screens - split view is too cramped */
    .editor-body--split {
        flex-direction: column;
    }

    .editor-body--split .editor-pane {
        flex: 1;
        min-height: 300px;
    }

    .editor-pane {
        padding: 0.5rem;
    }

    .editor-pane--input {
        border-right: none;
        border-bottom: 1px solid var(--p-content-border-color);
    }

    .view-toggle :deep(.p-button) {
        padding: 0.3rem 0.4rem;
        font-size: 0.75rem;
    }

    .header-actions {
        gap: 0.4rem;
    }

    .markdown-preview {
        font-size: 0.9375rem;
    }

    .note-placeholder {
        padding: 1.5rem 1rem;
    }

    .note-placeholder h2 {
        font-size: 1.25rem;
    }

    .note-placeholder p {
        font-size: 0.875rem;
        text-align: center;
    }
}
</style>
