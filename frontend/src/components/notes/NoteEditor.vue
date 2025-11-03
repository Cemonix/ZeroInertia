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
import { marked } from "marked";
import DOMPurify from "dompurify";
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
    const source = localContent.value || "";
    const rawHtml = marked.parse(source, { breaks: true, async: false }) as string;
    return DOMPurify.sanitize(rawHtml);
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
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--p-content-border-color);
    gap: 1rem;
}

.title-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    flex: 1;
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
    gap: 0.75rem;
}

.view-toggle {
    display: flex;
    align-items: center;
    background: var(--p-content-hover-background);
    border-radius: 999px;
    padding: 0.25rem;
}

.view-toggle :deep(.p-button) {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.875rem;
}

.view-toggle--active {
    background: var(--p-primary-100);
    color: var(--p-primary-color);
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
</style>
