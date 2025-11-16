import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useChecklistStore } from '@/stores/checklist';
import { resetMockChecklists, getMockChecklists } from '../mocks/handlers';

describe('Checklist Store Integration', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        resetMockChecklists();
    });

    it('should load checklists for a task', async () => {
        const store = useChecklistStore();
        const [mockChecklist] = getMockChecklists();

        await store.loadChecklistsForTask(mockChecklist.task_id);

        expect(store.checklists.length).toBeGreaterThan(0);

        const byTask = store.getChecklistsByTask(mockChecklist.task_id);
        expect(byTask.length).toBeGreaterThan(0);
        expect(byTask[0].task_id).toBe(mockChecklist.task_id);
    });

    it('should load checklist details with items', async () => {
        const store = useChecklistStore();
        const [mockChecklist] = getMockChecklists();

        await store.loadChecklistsForTask(mockChecklist.task_id);

        const loaded = await store.loadChecklistDetails(mockChecklist.id);

        expect(loaded).toBeDefined();
        expect(loaded.id).toBe(mockChecklist.id);
        expect(loaded.items).toBeDefined();
        expect(loaded.items && loaded.items.length).toBeGreaterThan(0);

        const fromStore = store.getChecklistById(mockChecklist.id);
        expect(fromStore).not.toBeNull();
        expect(fromStore?.items && fromStore.items.length).toBeGreaterThan(0);
    });

    it('should create and delete a checklist', async () => {
        const store = useChecklistStore();

        const newChecklist = await store.createChecklist({
            task_id: 'task-1',
            title: 'New Checklist',
        });

        expect(newChecklist.id).toBeDefined();
        expect(store.checklists.find(c => c.id === newChecklist.id)).toBeTruthy();

        await store.deleteChecklist(newChecklist.id);

        expect(store.checklists.find(c => c.id === newChecklist.id)).toBeFalsy();
    });

    it('should update a checklist title', async () => {
        const store = useChecklistStore();
        const [mockChecklist] = getMockChecklists();

        await store.loadChecklistsForTask(mockChecklist.task_id);

        const updated = await store.updateChecklist(mockChecklist.id, {
            title: 'Updated Checklist Title',
        });

        expect(updated.title).toBe('Updated Checklist Title');
        const fromStore = store.getChecklistById(mockChecklist.id);
        expect(fromStore?.title).toBe('Updated Checklist Title');
    });

    it('should compute checklist progress correctly', async () => {
        const store = useChecklistStore();
        const [mockChecklist] = getMockChecklists();

        await store.loadChecklistsForTask(mockChecklist.task_id);
        await store.loadChecklistDetails(mockChecklist.id);

        const progress = store.getChecklistProgress(mockChecklist.id);

        expect(progress.total).toBeGreaterThan(0);
        expect(progress.completed).toBeGreaterThanOrEqual(0);
        expect(progress.percentage).toBeGreaterThanOrEqual(0);
        expect(progress.percentage).toBeLessThanOrEqual(100);
    });

    it('should create, update and delete checklist items', async () => {
        const store = useChecklistStore();
        const [mockChecklist] = getMockChecklists();

        await store.loadChecklistDetails(mockChecklist.id);

        const created = await store.createChecklistItem(mockChecklist.id, {
            text: 'New Item',
        });

        expect(created.id).toBeDefined();

        const updated = await store.updateChecklistItem(
            mockChecklist.id,
            created.id,
            { completed: true }
        );

        expect(updated.completed).toBe(true);

        await store.deleteChecklistItem(mockChecklist.id, created.id);

        const fromStore = store.getChecklistById(mockChecklist.id);
        const exists = fromStore?.items?.some((item) => item.id === created.id);
        expect(exists).toBeFalsy();
    });

    it('should reorder checklists for a task', async () => {
        const store = useChecklistStore();
        const [mockChecklist] = getMockChecklists();

        await store.loadChecklistsForTask(mockChecklist.task_id);

        const secondChecklist = await store.createChecklist({
            task_id: mockChecklist.task_id,
            title: 'Second Checklist',
        });

        const reorderedIds = [secondChecklist.id, mockChecklist.id];
        await store.reorderChecklists(mockChecklist.task_id, reorderedIds);

        const byTask = store.getChecklistsByTask(mockChecklist.task_id);
        expect(byTask[0].id).toBe(secondChecklist.id);
        expect(byTask[1].id).toBe(mockChecklist.id);
    });

    it('should reorder checklist items', async () => {
        const store = useChecklistStore();
        const [mockChecklist] = getMockChecklists();

        const checklist = await store.loadChecklistDetails(mockChecklist.id);
        const items = checklist.items || [];

        expect(items.length).toBeGreaterThanOrEqual(2);

        const reorderedIds = [items[1].id, items[0].id];
        await store.reorderChecklistItems(mockChecklist.id, reorderedIds);

        const fromStore = store.getChecklistById(mockChecklist.id);
        expect(fromStore?.items?.[0].id).toBe(items[1].id);
        expect(fromStore?.items?.[1].id).toBe(items[0].id);
    });
});

