<template>
    <div class="tree-container">
        <Tree
            class="note-tree"
            v-model:value="treeNodes"
            selectionMode="single"
            v-model:selectionKeys="selectedNoteKeys"
            draggableNodes
            droppableNodes
            @node-drop="handleNodeDrop"
        >
            <template #default="{ node }">
                <div class="node-content">
                    <span class="node-label">{{ node.label }}</span>
                    <div class="node-actions">
                        <Button
                            text
                            rounded
                            size="small"
                            class="node-action"
                            aria-haspopup="true"
                            :aria-controls="`note_menu_${node.key}`"
                            @click.stop="openNoteMenu(node, $event)"
                            aria-label="Note options"
                        >
                            <FontAwesomeIcon icon="ellipsis" />
                        </Button>
                    </div>
                </div>
            </template>
        </Tree>
        <Menu
            ref="noteMenuRef"
            :model="noteMenuItems"
            :popup="true"
            :pt="{ root: { style: { zIndex: 1200 } } }"
        />
    </div>
</template>

<script lang="ts" setup>
import { ref, watchEffect, type Ref, type ComponentPublicInstance } from "vue";
import Tree from "primevue/tree";
import Button from "primevue/button";
import Menu from "primevue/menu";
import type { MenuItem } from "primevue/menuitem";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue";
import { useNoteStore } from "@/stores/note";
import { storeToRefs } from "pinia";
import type { TreeNode } from "primevue/treenode";
import type { TreeNodeDropEvent } from "primevue/tree";
import type { Note } from "@/models/note";

const noteStore = useNoteStore();
const confirm = useConfirm();
const toast = useToast();

const { selectedNoteKeys } = storeToRefs(noteStore);
const treeNodes: Ref<TreeNode[]> = ref([]);

type NoteMenu = ComponentPublicInstance & {
    toggle: (event: Event) => void;
    hide: () => void;
};
const noteMenuRef = ref<NoteMenu | null>(null);
const noteMenuItems = ref<MenuItem[]>([]);

const buildTree = (notes: Note[], parentId: string | null = null): TreeNode[] => {
    return notes
        .filter((note) => note.parent_id === parentId)
        .sort((a, b) => {
            if (a.order_index !== b.order_index) {
                return a.order_index - b.order_index;
            }
            return a.title.localeCompare(b.title);
        })
        .map((note) => ({
            key: note.id,
            label: note.title || "Untitled",
            data: note,
            children: buildTree(notes, note.id),
        }));
};

watchEffect(() => {
    const currentNotes = noteStore.notes;
    treeNodes.value = buildTree(currentNotes);
});

const createChildNote = async (parentId?: TreeNode["key"]) => {
    if (typeof parentId !== "string") {
        return;
    }
    try {
        await noteStore.createNote({
            title: "Untitled Note",
            parent_id: parentId,
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

const confirmDeletion = (node: TreeNode) => {
    if (typeof node.key !== "string") return;
    const noteTitle = typeof node.label === "string" ? node.label : "this note";
    const props = {
        message:
            "Deleting this note will remove all nested notes. This action cannot be undone.",
        header: `Delete "${noteTitle}"?`,
        icon: "fa fa-exclamation-triangle",
        acceptLabel: "Delete",
        rejectLabel: "Cancel",
        acceptClass: "p-button-danger",
        rejectClass: "p-button-text",
        accept: async () => {
            try {
                await noteStore.deleteNote(node.key);
                toast.add({
                    severity: "success",
                    summary: "Note deleted",
                    detail: `Removed "${noteTitle}".`,
                    life: 3000,
                });
            } catch (error) {
                toast.add({
                    severity: "error",
                    summary: "Unable to delete note",
                    detail:
                        error instanceof Error ? error.message : "Unknown error",
                    life: 4000,
                });
            }
        },
    };

    confirm.require(props);
};

function getNoteMenuItems(node: TreeNode): MenuItem[] {
    return [
        {
            label: 'Add note below',
            command: () => createChildNote(node.key),
        },
        {
            label: 'Delete note',
            command: () => confirmDeletion(node),
        },
    ];
}

function openNoteMenu(node: TreeNode, event: Event) {
    if (node.key === undefined || node.key === null) {
        return;
    }
    noteMenuItems.value = getNoteMenuItems(node);
    noteMenuRef.value?.toggle(event);
}

const flattenTree = (nodes: TreeNode[], parentId: string | null = null) => {
    const result: { id: string; parent_id: string | null; order_index: number }[] = [];
    nodes.forEach((node, index) => {
        if (typeof node.key !== "string") {
            return;
        }
        result.push({
            id: node.key,
            parent_id: parentId,
            order_index: index,
        });
        if (node.children && node.children.length > 0) {
            result.push(...flattenTree(node.children, node.key));
        }
    });
    return result;
};

const handleNodeDrop = async (_event: TreeNodeDropEvent) => {
    try {
        const payload = flattenTree(treeNodes.value);
        await noteStore.reorderNotes(payload);
        toast.add({
            severity: "success",
            summary: "Notes reordered",
            life: 2000,
        });
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Unable to reorder notes",
            detail: error instanceof Error ? error.message : "Unknown error",
            life: 3000,
        });
        await noteStore.loadNotes();
    }
};
</script>

<style scoped>
.tree-container {
    height: 100%;
    overflow-y: auto;
}

.note-tree {
    background-color: transparent;
}

:deep(.p-tree-node-label) {
    width: 100%;
}

.node-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    gap: 0.5rem;
}

.node-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.node-actions {
    display: flex;
    align-items: center;
    position: relative;
    min-width: 2rem;
    justify-content: flex-end;
}

.node-action {
    opacity: 0;
    transition: opacity 0.2s ease;
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    z-index: 2;
    touch-action: manipulation;
}

.node-content:hover .node-action,
.node-content:focus-within .node-action {
    opacity: 1;
    pointer-events: auto;
}

@media (hover: none) {
    .node-actions {
        position: static;
        min-width: auto;
    }

    .node-action {
        position: static;
        transform: none;
        opacity: 1;
        pointer-events: auto;
    }
}
</style>
