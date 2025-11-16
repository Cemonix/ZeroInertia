import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { CheckList, CheckListItem } from '@/models/checklist';
import {
    checklistService,
    type CheckListCreateInput,
    type CheckListItemCreateInput,
    type CheckListReorderItem
} from '@/services/checklistService';

export const useChecklistStore = defineStore('checklist', () => {
    const checklists = ref<CheckList[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);

    // Computed getters
    const getChecklistsByTask = computed(() => {
        return (taskId: string) =>
            checklists.value
                .filter(checklist => checklist.task_id === taskId)
                .sort((a, b) => a.order_index - b.order_index);
    });

    const getChecklistById = computed(() => {
        return (checklistId: string) =>
            checklists.value.find(checklist => checklist.id === checklistId) || null;
    });

    const getChecklistProgress = computed(() => {
        return (checklistId: string) => {
            const checklist = getChecklistById.value(checklistId);
            if (!checklist || !checklist.items || checklist.items.length === 0) {
                return { completed: 0, total: 0, percentage: 0 };
            }
            const completed = checklist.items.filter(item => item.completed).length;
            const total = checklist.items.length;
            return {
                completed,
                total,
                percentage: Math.round((completed / total) * 100)
            };
        };
    });

    // Checklist actions
    async function loadChecklistsForTask(taskId: string) {
        loading.value = true;
        error.value = null;
        try {
            const taskChecklists = await checklistService.getChecklistsByTask(taskId);
            // Merge checklists for this task with any existing checklists
            const others = checklists.value.filter(c => c.task_id !== taskId);
            checklists.value = [...others, ...taskChecklists];
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load checklists';
            // Keep existing cache on failure to avoid UI flicker
        } finally {
            loading.value = false;
        }
    }

    async function loadChecklistDetails(checklistId: string) {
        loading.value = true;
        error.value = null;
        try {
            const checklist = await checklistService.getChecklistById(checklistId);
            const index = checklists.value.findIndex(c => c.id === checklistId);
            if (index !== -1) {
                checklists.value[index] = checklist;
            } else {
                checklists.value.push(checklist);
            }
            return checklist;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load checklist';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function createChecklist(checklistData: CheckListCreateInput) {
        loading.value = true;
        error.value = null;
        try {
            const newChecklist = await checklistService.createChecklist(checklistData);
            checklists.value.push(newChecklist);
            return newChecklist;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to create checklist';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateChecklist(checklistId: string, updates: Partial<CheckList>) {
        loading.value = true;
        error.value = null;
        try {
            const updatedChecklist = await checklistService.updateChecklist(checklistId, updates);
            const index = checklists.value.findIndex(c => c.id === checklistId);
            if (index !== -1) {
                checklists.value[index] = updatedChecklist;
            }
            return updatedChecklist;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to update checklist';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function deleteChecklist(checklistId: string) {
        loading.value = true;
        error.value = null;
        try {
            await checklistService.deleteChecklist(checklistId);
            checklists.value = checklists.value.filter(c => c.id !== checklistId);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to delete checklist';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function reorderChecklists(taskId: string, reorderedChecklistIds: string[]) {
        // Optimistically update the local state
        const checklistsInTask = reorderedChecklistIds.map(id =>
            checklists.value.find(c => c.id === id)
        ).filter(Boolean) as CheckList[];

        // Update order_index for each checklist
        checklistsInTask.forEach((checklist, index) => {
            const checklistIndex = checklists.value.findIndex(c => c.id === checklist.id);
            if (checklistIndex !== -1) {
                checklists.value[checklistIndex] = { ...checklist, order_index: index };
            }
        });

        const reorderPayload: CheckListReorderItem[] = reorderedChecklistIds.map((id, index) => ({
            id,
            order_index: index,
        }));

        try {
            await checklistService.reorderChecklists(reorderPayload);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to reorder checklists';
            // Reload checklists to restore correct order on failure
            await loadChecklistsForTask(taskId);
            throw err;
        }
    }

    // CheckListItem actions
    async function createChecklistItem(checklistId: string, itemData: CheckListItemCreateInput) {
        loading.value = true;
        error.value = null;
        try {
            const newItem = await checklistService.createChecklistItem(checklistId, itemData);

            // Update the checklist in the store
            const index = checklists.value.findIndex(c => c.id === checklistId);
            if (index !== -1) {
                const checklist = checklists.value[index];
                checklists.value[index] = {
                    ...checklist,
                    items: [...(checklist.items || []), newItem]
                };
            }
            return newItem;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to create checklist item';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function updateChecklistItem(checklistId: string, itemId: string, updates: Partial<CheckListItem>) {
        loading.value = true;
        error.value = null;
        try {
            const updatedItem = await checklistService.updateChecklistItem(checklistId, itemId, updates);

            // Update the item in the store
            const checklistIndex = checklists.value.findIndex(c => c.id === checklistId);
            if (checklistIndex !== -1) {
                const checklist = checklists.value[checklistIndex];
                if (checklist.items) {
                    const itemIndex = checklist.items.findIndex(item => item.id === itemId);
                    if (itemIndex !== -1) {
                        const newItems = [...checklist.items];
                        newItems[itemIndex] = updatedItem;
                        checklists.value[checklistIndex] = {
                            ...checklist,
                            items: newItems
                        };
                    }
                }
            }
            return updatedItem;
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to update checklist item';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function toggleChecklistItem(checklistId: string, itemId: string) {
        const checklist = getChecklistById.value(checklistId);
        const item = checklist?.items?.find(i => i.id === itemId);
        if (!item) return;

        await updateChecklistItem(checklistId, itemId, {
            completed: !item.completed
        });
    }

    async function deleteChecklistItem(checklistId: string, itemId: string) {
        loading.value = true;
        error.value = null;
        try {
            await checklistService.deleteChecklistItem(checklistId, itemId);

            // Remove the item from the store
            const checklistIndex = checklists.value.findIndex(c => c.id === checklistId);
            if (checklistIndex !== -1) {
                const checklist = checklists.value[checklistIndex];
                checklists.value[checklistIndex] = {
                    ...checklist,
                    items: checklist.items?.filter(item => item.id !== itemId) || []
                };
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to delete checklist item';
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function reorderChecklistItems(checklistId: string, reorderedItemIds: string[]) {
        const checklist = getChecklistById.value(checklistId);
        if (!checklist || !checklist.items) return;

        // Optimistically update the local state
        const itemsInChecklist = reorderedItemIds.map(id =>
            checklist.items!.find(item => item.id === id)
        ).filter(Boolean) as CheckListItem[];

        const checklistIndex = checklists.value.findIndex(c => c.id === checklistId);
        if (checklistIndex !== -1) {
            checklists.value[checklistIndex] = {
                ...checklist,
                items: itemsInChecklist.map((item, index) => ({ ...item, order_index: index }))
            };
        }

        const reorderPayload: CheckListReorderItem[] = reorderedItemIds.map((id, index) => ({
            id,
            order_index: index,
        }));

        try {
            await checklistService.reorderChecklistItems(checklistId, reorderPayload);
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to reorder checklist items';
            // Reload checklist to restore correct order on failure
            await loadChecklistDetails(checklistId);
            throw err;
        }
    }

    function clearChecklists() {
        checklists.value = [];
    }

    return {
        checklists,
        loading,
        error,
        getChecklistsByTask,
        getChecklistById,
        getChecklistProgress,
        loadChecklistsForTask,
        loadChecklistDetails,
        createChecklist,
        updateChecklist,
        deleteChecklist,
        reorderChecklists,
        createChecklistItem,
        updateChecklistItem,
        toggleChecklistItem,
        deleteChecklistItem,
        reorderChecklistItems,
        clearChecklists,
    };
});
