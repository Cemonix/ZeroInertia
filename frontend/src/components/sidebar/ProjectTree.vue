<template>
    <div class="tree-container">
        <Tree class="project-tree"
            v-model:value="treeNodes"
            v-model:expandedKeys="expandedKeys"
            selectionMode="single"
            v-model:selectionKeys="selectedKey"
            draggableNodes
            droppableNodes
            @node-drop="onNodeDrop">
            <template #default="{ node }">
                <div class="node-content">
                    <span class="node-label">{{ node.label }}</span>
                    <Button
                        severity="danger"
                        text
                        rounded
                        size="small"
                        class="node-action"
                        @click.stop="confirmProjectDeletion(node)"
                        aria-label="Delete project"
                    >
                        <FontAwesomeIcon icon="trash" />
                    </Button>
                </div>
            </template>
        </Tree>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, watchEffect, type Ref } from 'vue';
import Tree from 'primevue/tree';
import type { TreeSelectionKeys, TreeExpandedKeys, TreeNodeDropEvent } from 'primevue/tree';
import type { TreeNode } from 'primevue/treenode';
import { useProjectStore } from '@/stores/project';
import type { Project, ProjectReorderItem } from '@/models/project';
import { useAuthStore } from '@/stores/auth';
import { useToast } from "primevue";
import Button from 'primevue/button';
import { useConfirm } from 'primevue/useconfirm';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

const toast = useToast();
const confirm = useConfirm();

const EXPANDED_KEYS_STORAGE_KEY = 'projectTree.expandedKeys';

const projectStore = useProjectStore();
const authStore = useAuthStore();
const selectedKey: Ref<TreeSelectionKeys | undefined> = ref();
const treeNodes: Ref<TreeNode[]> = ref([]);
const expandedKeys: Ref<TreeExpandedKeys> = ref({});

watch(selectedKey, (newKey) => {
    if (newKey && Object.keys(newKey).length > 0) {
        const projectId = Object.keys(newKey)[0];
        projectStore.selectProject(projectId);
    } else {
        // No project selected
        projectStore.selectProject(null);
    }
});

// Watch for changes from backend and rebuild tree
watchEffect(() => {
    const currentProjects = projectStore.projects;
    treeNodes.value = buildTree(currentProjects);
});

// Save expanded state to localStorage whenever it changes
watch(expandedKeys, (newExpandedKeys) => {
    localStorage.setItem(EXPANDED_KEYS_STORAGE_KEY, JSON.stringify(newExpandedKeys));
}, { deep: true });

// Load projects when authenticated
watch(
    () => authStore.isAuthenticated,
    async (isAuthenticated) => {
        if (isAuthenticated) {
            await projectStore.loadProjects();
        }
    },
    { immediate: true }
);

// Build tree structure from flat projects array
function buildTree(projectList: Project[], parentId: string | null = null): TreeNode[] {
    return projectList
        .filter((project) => project.parent_id === parentId)
        .sort((a, b) => a.order_index - b.order_index)
        .map((project) => ({
            key: project.id,
            label: project.title,
            children: buildTree(projectList, project.id),
        }));
}

// Flatten tree structure to extract parent_id and order_index
function flattenTree(nodes: TreeNode[], parentId: string | null = null): ProjectReorderItem[] {
    const result: ProjectReorderItem[] = [];

    nodes.forEach((node, index) => {
        result.push({
            id: node.key,
            parent_id: parentId,
            order_index: index
        });

        if (node.children && node.children.length > 0) {
            result.push(...flattenTree(node.children, node.key));
        }
    });

    return result;
}

function onNodeDrop(_event: TreeNodeDropEvent) {
    const flattenedTree = flattenTree(treeNodes.value);
    projectStore.handleTreeReorder(flattenedTree);
}

function confirmProjectDeletion(node: TreeNode) {
    confirm.require({
        message: "Deleting this project will remove all sections, tasks, and data within it. This action cannot be undone.",
        header: "Delete Project?",
        icon: "fa fa-danger",
        acceptLabel: "Delete",
        rejectLabel: "Cancel",
        acceptClass: "p-button-danger",
        rejectClass: "p-button-text",
        accept: () => deleteProject(node),
    });
}

async function deleteProject(node: TreeNode) {
    try {
        await projectStore.deleteProject(node.key);
        toast.add({
            severity: "success",
            summary: "Project deleted",
            detail: `Removed "${node.label}" and all associated items.`,
            life: 4000,
        });
    } catch (error) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to delete project" });
    }
}

onMounted(async () => {
    // Load expanded state from localStorage
    const savedExpandedKeys = localStorage.getItem(EXPANDED_KEYS_STORAGE_KEY);
    if (savedExpandedKeys) {
        try {
            expandedKeys.value = JSON.parse(savedExpandedKeys);
        } catch (e) {
            toast.add({ severity: "error", summary: "Error", detail: "Failed to parse saved expanded keys" });
        }
    }
});
</script>

<style scoped>
.project-tree {
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
}

.node-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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
