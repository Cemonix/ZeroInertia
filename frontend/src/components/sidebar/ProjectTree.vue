<template>
    <div class="tree-container">
        <Tree class="project-tree"
            v-model:value="treeNodes"
            v-model:expandedKeys="expandedKeys"
            selectionMode="single"
            v-model:selectionKeys="selectedProject"
            draggableNodes
            droppableNodes
            @node-drop="onNodeDrop">
            <template #default="{ node }">
                <div class="node-content">
                    <span class="node-label">{{ node.label }}</span>
                    <div class="node-actions">
                        <span class="node-count" :aria-label="`Tasks in ${node.label}`" v-if="node.key">
                            {{ getTaskCountForProject(String(node.key)) }}
                        </span>

                        <Button
                            text
                            rounded
                            size="small"
                            class="node-action"
                            aria-haspopup="true"
                            :aria-controls="`project_menu_${node.key}`"
                            @click.stop="toggleProjectMenu(node, $event)"
                            aria-label="Project options"
                        >
                            <FontAwesomeIcon icon="ellipsis" />
                        </Button>
                        <Menu
                            :id="`project_menu_${node.key}`"
                            :model="getProjectMenuItems(node)"
                            :popup="true"
                            :ref="(el) => setMenuRef(node.key, el)"
                        />
                    </div>
                </div>
            </template>
        </Tree>
        <Dialog
            v-model:visible="isRenameDialogVisible"
            header="Rename Project"
            modal
            :style="{ width: '420px' }"
            :pt="{ content: { style: { padding: '1.5rem' } } }"
            @hide="onRenameDialogHide"
        >
            <div class="rename-project-form">
                <label for="project-rename-input">Project name</label>
                <InputText
                    id="project-rename-input"
                    v-model="renameProjectTitle"
                    autofocus
                    @keyup.enter="handleRenameProject"
                />
                <div class="rename-project-actions">
                    <Button
                        label="Cancel"
                        text
                        type="button"
                        @click="isRenameDialogVisible = false"
                    />
                    <Button
                        label="Save"
                        type="button"
                        :disabled="!renameProjectTitle.trim() || renameProjectTitle.trim() === originalProjectTitle"
                        @click="handleRenameProject"
                    />
                </div>
            </div>
        </Dialog>
        <Dialog
            v-model:visible="isCreateBelowDialogVisible"
            header="Create Project"
            modal
            :style="{ width: '420px' }"
            :pt="{ content: { style: { padding: '1.5rem' } } }"
            @hide="onCreateBelowDialogHide"
        >
            <div class="rename-project-form">
                <label for="project-create-input">Project name</label>
                <InputText
                    id="project-create-input"
                    v-model="newProjectTitle"
                    autofocus
                    @keyup.enter="handleCreateProjectBelow"
                />
                <div class="rename-project-actions">
                    <Button
                        label="Cancel"
                        text
                        type="button"
                        @click="isCreateBelowDialogVisible = false"
                    />
                    <Button
                        label="Create"
                        type="button"
                        :disabled="!newProjectTitle.trim()"
                        @click="handleCreateProjectBelow"
                    />
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, watchEffect, type Ref, type ComponentPublicInstance } from 'vue';
import Tree from 'primevue/tree';
import type { TreeExpandedKeys, TreeNodeDropEvent } from 'primevue/tree';
import type { TreeNode } from 'primevue/treenode';
import { useProjectStore } from '@/stores/project';
import type { Project, ProjectReorderItem } from '@/models/project';
import { useAuthStore } from '@/stores/auth';
import { useToast } from "primevue";
import Button from 'primevue/button';
import Menu from 'primevue/menu';
import { useConfirm } from 'primevue/useconfirm';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { storeToRefs } from 'pinia';
import type { Task } from '@/models/task';
import { taskService } from '@/services/taskService';
import { useTaskStore } from '@/stores/task';

const toast = useToast();
const confirm = useConfirm();

const EXPANDED_KEYS_STORAGE_KEY = 'projectTree.expandedKeys';

const projectStore = useProjectStore();
const authStore = useAuthStore();
const { selectedProject } = storeToRefs(projectStore);
const taskStore = useTaskStore();
const { tasks: taskStoreTasks } = storeToRefs(taskStore);
const treeNodes: Ref<TreeNode[]> = ref([]);
const expandedKeys: Ref<TreeExpandedKeys> = ref({});
type ProjectMenu = ComponentPublicInstance & {
    toggle: (event: MouseEvent) => void;
    hide: () => void;
};
const menuRefs = new Map<string, ProjectMenu>();
const isRenameDialogVisible = ref(false);
const renameProjectTitle = ref('');
const projectBeingRenamed = ref<TreeNode | null>(null);
const originalProjectTitle = ref('');

// Create project below dialog state
const isCreateBelowDialogVisible = ref(false);
const newProjectTitle = ref('');
const projectToCreateBelow = ref<TreeNode | null>(null);

// Local task counts mapped by project id
const taskCounts = ref<Record<string, number>>({});

function applyPartialCountsFrom(tasks: Task[]) {
    // Only update counts for the projects present in the given tasks list
    const updated: Record<string, number> = { ...taskCounts.value };
    const touched = new Set<string>();
    for (const t of tasks) {
        touched.add(t.project_id);
    }
    for (const pid of touched) {
        updated[pid] = tasks.filter(t => t.project_id === pid && !t.completed && !t.archived).length;
    }
    taskCounts.value = updated;
}

function getTaskCountForProject(projectId: string): number {
    return taskCounts.value[projectId] ?? 0;
}

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
            // Fetch counts from backend to avoid heavy client-side aggregation
            try {
                const counts = await taskService.getTaskCountsByProject();
                taskCounts.value = counts;
            } catch (e) {
                // Fail silently for counts to avoid blocking UI
                taskCounts.value = {};
            }
        }
    },
    { immediate: true }
);

// When tasks in the task store change (e.g., on a board), update counts for those projects
watch(
    taskStoreTasks,
    (newTasks) => {
        applyPartialCountsFrom(newTasks as Task[]);
    },
    { deep: true }
);

// Build tree structure from flat projects array
function buildTree(projectList: Project[], parentId: string | null = null): TreeNode[] {
    return projectList
        .filter((project) => project.parent_id === parentId && !project.is_inbox)
        .sort((a, b) => a.order_index - b.order_index)
        .map((project) => {
            const isInbox = project.is_inbox;
            return {
                key: project.id,
                label: project.title,
                data: project,
                draggable: isInbox ? false : undefined,
                droppable: isInbox ? false : undefined,
                children: buildTree(projectList, project.id),
            } as TreeNode;
        });
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

function getProjectMenuItems(node: TreeNode) {
    const projectId = typeof node.key === 'string' ? node.key : String(node.key ?? '');
    const project = projectId ? projectStore.getProjectById(projectId) : undefined;
    const isInbox = project?.is_inbox === true;

    const items = [
        {
            label: 'Create project below',
            command: () => createProjectBelow(node),
        },
        {
            label: 'Rename Project',
            command: () => openRenameDialog(node),
        },
    ];

    if (!isInbox) {
        items.push({
            label: 'Delete Project',
            command: () => confirmProjectDeletion(node),
        });
    }

    return items;
}

function setMenuRef(
    key: TreeNode['key'],
    menu: Element | ComponentPublicInstance | null
) {
    if (key === undefined || key === null) {
        return;
    }
    const normalizedKey = typeof key === 'string' ? key : String(key);
    if (menu && 'toggle' in menu && typeof (menu as ProjectMenu).toggle === 'function') {
        menuRefs.set(normalizedKey, menu as ProjectMenu);
    } else {
        menuRefs.delete(normalizedKey);
    }
}

function toggleProjectMenu(node: TreeNode, event: MouseEvent) {
    if (node.key === undefined || node.key === null) {
        return;
    }
    const normalizedKey = typeof node.key === 'string' ? node.key : String(node.key);
    const menu = menuRefs.get(normalizedKey);
    menu?.toggle(event);
}

function openRenameDialog(node: TreeNode) {
    projectBeingRenamed.value = node;
    renameProjectTitle.value = typeof node.label === 'string' ? node.label : '';
    originalProjectTitle.value = renameProjectTitle.value;
    isRenameDialogVisible.value = true;
}

function onRenameDialogHide() {
    projectBeingRenamed.value = null;
    renameProjectTitle.value = '';
    originalProjectTitle.value = '';
}

async function handleRenameProject() {
    const node = projectBeingRenamed.value;
    if (!node || !node.key) {
        isRenameDialogVisible.value = false;
        return;
    }

    const trimmedTitle = renameProjectTitle.value.trim();
    if (!trimmedTitle || trimmedTitle === originalProjectTitle.value) {
        isRenameDialogVisible.value = false;
        return;
    }

    try {
        await projectStore.updateProject(String(node.key), { title: trimmedTitle });
        toast.add({
            severity: "success",
            summary: "Project renamed",
            detail: `Project is now "${trimmedTitle}".`,
            life: 4000,
        });
    } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to rename project";
        toast.add({ severity: "error", summary: "Error", detail: message });
    } finally {
        isRenameDialogVisible.value = false;
    }
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

function createProjectBelow(node: TreeNode) {
    projectToCreateBelow.value = node;
    newProjectTitle.value = '';
    isCreateBelowDialogVisible.value = true;
}

function onCreateBelowDialogHide() {
    projectToCreateBelow.value = null;
    newProjectTitle.value = '';
}

async function handleCreateProjectBelow() {
    const node = projectToCreateBelow.value;
    if (!node || !node.key) {
        isCreateBelowDialogVisible.value = false;
        return;
    }

    const trimmedTitle = newProjectTitle.value.trim();
    if (!trimmedTitle) {
        isCreateBelowDialogVisible.value = false;
        return;
    }

    const projectId = typeof node.key === 'string' ? node.key : String(node.key ?? '');
    const project = projectId ? projectStore.getProjectById(projectId) : undefined;

    if (!project) {
        isCreateBelowDialogVisible.value = false;
        return;
    }

    try {
        // Get all siblings (projects with the same parent)
        const siblings = projectStore.projects
            .filter((p) => p.parent_id === project.parent_id && p.id !== project.id)
            .sort((a, b) => a.order_index - b.order_index);

        // Calculate new order indices: shift projects after current one
        const updates: ProjectReorderItem[] = [];

        siblings.forEach((p) => {
            if (p.order_index > project.order_index) {
                updates.push({
                    id: p.id,
                    parent_id: p.parent_id,
                    order_index: p.order_index + 1,
                });
            }
        });

        // If we have projects to shift, update them first
        if (updates.length > 0) {
            await projectStore.handleTreeReorder(updates);
        }

        // Now create the new project at the position right after the current project
        await projectStore.createProject({
            title: trimmedTitle,
            parent_id: project.parent_id,
            order_index: project.order_index + 1,
        });

        toast.add({
            severity: "success",
            summary: "Project created",
            detail: `"${trimmedTitle}" created below.`,
            life: 3000,
        });
    } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to create project";
        toast.add({ severity: "error", summary: "Error", detail: message });
    } finally {
        isCreateBelowDialogVisible.value = false;
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

.node-actions {
    display: flex;
    align-items: center;
    position: relative;
    min-width: 2rem;
    justify-content: flex-end;
}

.node-content:hover .node-action,
.node-content:focus-within .node-action {
    opacity: 1;
}

.node-count {
    font-size: 0.85rem;
    color: var(--p-text-muted-color);
    text-align: right;
    transition: opacity 0.2s ease;
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    z-index: 1;
}

.node-content:hover .node-count,
.node-content:focus-within .node-count {
    opacity: 0;
}

.node-action {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    z-index: 2;
}

.node-content:hover .node-action,
.node-content:focus-within .node-action {
    pointer-events: auto;
}

.rename-project-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.rename-project-form label {
    font-weight: 600;
    color: var(--p-text-color);
}

.rename-project-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}
</style>
