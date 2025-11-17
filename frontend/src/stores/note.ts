import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import type { TreeSelectionKeys } from "primevue/tree";
import type { Note, NoteInput, NoteReorderItem, NoteUpdateInput } from "@/models/note";
import { noteService } from "@/services/noteService";
import type { PaginationParams } from "@/models/pagination";

export const useNoteStore = defineStore("note", () => {
    const notes = ref<Note[]>([]);
    const selectedNoteId = ref<string | null>(null);
    const selectedNoteKeys = ref<TreeSelectionKeys | undefined>(undefined);
    const loading = ref(false);
    const error = ref<string | null>(null);

    const activeNote = computed<Note | null>(() => {
        if (!selectedNoteId.value) return null;
        return notes.value.find((note) => note.id === selectedNoteId.value) ?? null;
    });

    watch(selectedNoteKeys, (value) => {
        const nextId =
            value && Object.keys(value).length > 0
                ? Object.keys(value)[0]
                : null;
        if (selectedNoteId.value !== nextId) {
            selectedNoteId.value = nextId;
        }
    });

    watch(selectedNoteId, (value) => {
        const currentSelectedId =
            selectedNoteKeys.value && Object.keys(selectedNoteKeys.value).length > 0
                ? Object.keys(selectedNoteKeys.value)[0]
                : null;

        if (value && currentSelectedId !== value) {
            selectedNoteKeys.value = { [value]: true };
        } else if (!value && selectedNoteKeys.value) {
            selectedNoteKeys.value = undefined;
        }
    });

    async function loadNotes(pagination: PaginationParams = { page: 1, page_size: 200 }) {
        loading.value = true;
        error.value = null;
        try {
            const existingId = selectedNoteId.value;
            const resp = await noteService.getNotes(pagination);
            notes.value = resp.items;

            if (existingId) {
                const exists = notes.value.some((note) => note.id === existingId);
                if (!exists) {
                    selectedNoteId.value = notes.value.length > 0 ? notes.value[0].id : null;
                }
            } else if (notes.value.length > 0) {
                selectedNoteId.value = notes.value[0].id;
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to load notes";
        } finally {
            loading.value = false;
        }
    }

    async function createNote(input: NoteInput) {
        loading.value = true;
        error.value = null;
        try {
            const newNote = await noteService.createNote({
                title: input.title,
                parent_id: input.parent_id ?? null,
                content: input.content ?? "",
            });
            notes.value = [...notes.value, newNote];
            selectedNoteId.value = newNote.id;
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to create note";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateNote(id: string, payload: NoteUpdateInput) {
        loading.value = true;
        error.value = null;
        try {
            const updated = await noteService.updateNote(id, payload);
            notes.value = notes.value.map((note) => (note.id === id ? updated : note));
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to update note";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteNote(id: string) {
        loading.value = true;
        error.value = null;
        try {
            await noteService.deleteNote(id);
            const toRemove = new Set<string>([id]);

            const collectChildren = (parentId: string) => {
                notes.value
                    .filter((note) => note.parent_id === parentId)
                    .forEach((child) => {
                        toRemove.add(child.id);
                        collectChildren(child.id);
                    });
            };

            collectChildren(id);
            notes.value = notes.value.filter((note) => !toRemove.has(note.id));

            if (selectedNoteId.value && toRemove.has(selectedNoteId.value)) {
                selectedNoteId.value = notes.value.length > 0 ? notes.value[0].id : null;
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to delete note";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function reorderNotes(items: NoteReorderItem[]) {
        loading.value = true;
        error.value = null;
        try {
            await noteService.reorderNotes(items);
            const updated = new Map<string, Note>(
                notes.value.map((note) => [note.id, { ...note }]),
            );
            items.forEach((item) => {
                const current = updated.get(item.id);
                if (current) {
                    current.parent_id = item.parent_id;
                    current.order_index = item.order_index;
                }
            });
            notes.value = Array.from(updated.values());
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Failed to reorder notes";
            throw err;
        } finally {
            loading.value = false;
        }
    }

    function selectNote(noteId: string | null) {
        selectedNoteId.value = noteId;
    }

    return {
        notes,
        selectedNoteId,
        selectedNoteKeys,
        activeNote,
        loading,
        error,
        loadNotes,
        createNote,
        updateNote,
        deleteNote,
        reorderNotes,
        selectNote,
    };
});
