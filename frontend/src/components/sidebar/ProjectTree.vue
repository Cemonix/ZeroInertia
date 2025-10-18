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
                <span>{{ node.label }}</span>
            </template>
        </Tree>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, watchEffect, type Ref } from 'vue';
import Tree, { type TreeSelectionKeys, type TreeNodeDropEvent, type TreeExpandedKeys } from 'primevue/tree';
import { useProjectStore, type ProjectTreeNode } from '@/stores/project';
import type { Project, ProjectReorderItem } from '@/models/project';

const EXPANDED_KEYS_STORAGE_KEY = 'projectTree.expandedKeys';

const projectStore = useProjectStore();
const selectedKey: Ref<TreeSelectionKeys | undefined> = ref();
const treeNodes: Ref<ProjectTreeNode[]> = ref([]);
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

// Build tree structure from flat projects array
function buildTree(projectList: Project[], parentId: string | null = null): ProjectTreeNode[] {
    return projectList
        .filter((project) => project.parent_id === parentId)
        .sort((a, b) => a.order_index - b.order_index)
        .map((project) => ({
            key: project.id,
            label: project.title,
            id: project.id,
            children: buildTree(projectList, project.id),
        }));
}

// Flatten tree structure to extract parent_id and order_index
function flattenTree(nodes: ProjectTreeNode[], parentId: string | null = null): ProjectReorderItem[] {
    const result: ProjectReorderItem[] = [];

    nodes.forEach((node, index) => {
        result.push({
            id: node.id,
            parent_id: parentId,
            order_index: index
        });

        if (node.children && node.children.length > 0) {
            result.push(...flattenTree(node.children, node.id));
        }
    });

    return result;
}

function onNodeDrop(_event: TreeNodeDropEvent) {
    const flattenedTree = flattenTree(treeNodes.value);
    projectStore.handleTreeReorder(flattenedTree);
}

onMounted(async () => {
    // Load expanded state from localStorage
    const savedExpandedKeys = localStorage.getItem(EXPANDED_KEYS_STORAGE_KEY);
    if (savedExpandedKeys) {
        try {
            expandedKeys.value = JSON.parse(savedExpandedKeys);
        } catch (e) {
            console.error('Failed to parse saved expanded keys:', e);
        }
    }

    await projectStore.fetchProjects();
});
</script>

<style scoped>
.project-tree {
    background-color: transparent;
}
</style>