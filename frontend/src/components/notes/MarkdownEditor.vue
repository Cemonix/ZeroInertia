<template>
    <div ref="editorContainer" class="markdown-editor"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue';
import { EditorState, Compartment } from '@codemirror/state';
import { EditorView, keymap, lineNumbers } from '@codemirror/view';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { markdown } from '@codemirror/lang-markdown';
import { oneDark } from '@codemirror/theme-one-dark';
import { oneLight } from '@/themes/oneLight';
import { useTheme } from '@/composables/useTheme';

interface Props {
    modelValue: string;
}

interface Emits {
    (e: 'update:modelValue', value: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const { isDarkMode } = useTheme();
const editorContainer = ref<HTMLElement | null>(null);
let editorView: EditorView | null = null;
const themeCompartment = new Compartment();

const currentTheme = computed(() => {
    return isDarkMode.value ? oneDark : oneLight;
});

onMounted(() => {
    if (!editorContainer.value) return;

    const startState = EditorState.create({
        doc: props.modelValue,
        extensions: [
            lineNumbers(),
            history(),
            markdown(),
            themeCompartment.of(currentTheme.value),
            keymap.of([...defaultKeymap, ...historyKeymap]),
            EditorView.lineWrapping,
            EditorView.updateListener.of((update) => {
                if (update.docChanged) {
                    emit('update:modelValue', update.state.doc.toString());
                }
            }),
        ],
    });

    editorView = new EditorView({
        state: startState,
        parent: editorContainer.value,
    });
});

watch(currentTheme, (newTheme) => {
    if (!editorView) return;
    editorView.dispatch({
        effects: themeCompartment.reconfigure(newTheme)
    });
});

watch(
    () => props.modelValue,
    (newValue) => {
        if (!editorView) return;
        const currentValue = editorView.state.doc.toString();
        if (newValue !== currentValue) {
            editorView.dispatch({
                changes: {
                    from: 0,
                    to: currentValue.length,
                    insert: newValue,
                },
            });
        }
    }
);

onBeforeUnmount(() => {
    editorView?.destroy();
});
</script>

<style scoped>
.markdown-editor {
    height: 100%;
    overflow: auto;
    font-family: var(--font-family-monospace, "Fira Code", "SFMono-Regular", monospace);
}

.markdown-editor :deep(.cm-editor) {
    height: 100%;
    font-size: 0.95rem;
}

.markdown-editor :deep(.cm-scroller) {
    overflow: auto;
}

.markdown-editor :deep(.cm-content) {
    padding: 0.5rem 0;
}

.markdown-editor :deep(.cm-line) {
    padding: 0 0.5rem;
}
</style>
