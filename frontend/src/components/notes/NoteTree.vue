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
                            size="small"
                            rounded
                            class="node-action"
                            aria-label="Add child note"
                            @click.stop="createChildNote(node.key)"
                        >
                            <FontAwesomeIcon icon="plus" />
                        </Button>
                        <Button
                            text
                            severity="danger"
                            size="small"
                            rounded
                            class="node-action"
                            aria-label="Delete note"
                            @click.stop="confirmDeletion(node)"
                        >
                            <FontAwesomeIcon icon="trash" />
                        </Button>
                    </div>
                </div>
            </template>
        </Tree>
    </div>
</template>

<script lang="ts" setup>
import { ref, watchEffect, type Ref } from "vue";
import Tree from "primevue/tree";
import Button from "primevue/button";
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
    gap: 0.25rem;
}

.node-action {
    opacity: 0;
    transition: opacity 0.2s ease;
}

.node-content:hover .node-action,
.node-content:focus-within .node-action {
    opacity: 1;
}
</style>
