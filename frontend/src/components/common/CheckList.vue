<template>
    <div class="checklist">
        <!-- Checklist Header -->
        <div class="checklist-header">
            <div class="checklist-title">
                <div class="title">
                    <FontAwesomeIcon icon="check-square" />
                    <span>{{ title }}</span>
                </div>
                <div class="spacer"></div>
                <div class="actions">
                    <Button
                        text
                        aria-label="Delete Checklist"
                        severity="danger"
                        size="small"
                        @click="deleteChecklist()"
                    >
                        <span>Delete Checklist</span>
                        <FontAwesomeIcon icon="trash" />
                    </Button>
                </div>
            </div>
            <div class="checklist-progress">
                <span>{{ completedCount }}/{{ items.length }}</span>
                <div class="progress-bar">
                    <div
                        class="progress-fill"
                        :style="{ width: progressPercentage + '%' }"
                    ></div>
                </div>
            </div>
        </div>

        <!-- Checklist Items -->
        <div class="checklist-items">
            <div
                v-for="(item, _) in items"
                :key="item.id"
                class="checklist-item"
                :class="{ 'is-completed': item.completed }"
            >
                <Checkbox
                    :model-value="item.completed"
                    @update:model-value="toggleItem(item.id)"
                    :binary="true"
                    :input-id="`item-${item.id}`"
                />

                <div class="item-content" @click="!isEditing(item.id) && toggleItem(item.id)">
                    <span v-if="!isEditing(item.id)" class="item-text">{{ item.text }}</span>
                    <InputText
                        v-else
                        :model-value="item.text"
                        @update:model-value="(val) => updateItemText(item.id, val as string)"
                        @blur="saveEdit(item.id)"
                        @keyup.enter="saveEdit(item.id)"
                        @keyup.esc="cancelEdit(item.id)"
                        autofocus
                        class="item-input"
                    />
                </div>

                <div class="item-actions">
                    <Button
                        text
                        size="small"
                        @click="startEdit(item.id)"
                        v-if="!isEditing(item.id)"
                    >
                        <FontAwesomeIcon icon="pen" />
                    </Button>
                    <Button
                        text
                        size="small"
                        severity="danger"
                        @click="deleteItem(item.id)"
                    >
                        <FontAwesomeIcon icon="trash" />
                    </Button>
                </div>
            </div>

            <!-- Add New Item -->
            <div class="checklist-item add-item" v-if="showAddInput">
                <Checkbox disabled :binary="true" />
                <InputText
                    v-model="newItemText"
                    @blur="handleAddBlur"
                    @keyup.enter="addItem"
                    @keyup.esc="cancelAdd"
                    placeholder="Add an item"
                    autofocus
                    class="item-input"
                />
                <div class="item-actions">
                    <Button
                        label="Add"
                        size="small"
                        @click="addItem"
                        :disabled="!newItemText.trim()"
                    />
                    <Button
                        text
                        size="small"
                        @click="cancelAdd"
                    >
                        <FontAwesomeIcon icon="times" />
                    </Button>
                </div>
            </div>

            <Button
                v-else
                text
                size="small"
                @click="showAddInput = true"
                class="add-item-button"
            >
               <FontAwesomeIcon icon="plus" /> Add an item
            </Button>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { useChecklistStore } from '@/stores/checklist';
import { useToast } from "primevue";

const toast = useToast();

interface Props {
    checklistId: string;
}

const props = defineProps<Props>();

const checklistStore = useChecklistStore();

// Local UI state
const showAddInput = ref(false);
const newItemText = ref('');
const editingItems = ref<Record<string, { editing: boolean; originalText: string }>>({});

// Computed properties from store
const checklist = computed(() => checklistStore.getChecklistById(props.checklistId));
const items = computed(() => checklist.value?.items || []);
const title = computed(() => checklist.value?.title || 'Checklist');

const progress = computed(() => checklistStore.getChecklistProgress(props.checklistId));
const completedCount = computed(() => progress.value.completed);
const progressPercentage = computed(() => progress.value.percentage);

async function deleteChecklist() {
    try {
        await checklistStore.deleteChecklist(props.checklistId);
    } catch (err) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to delete checklist" });
    }
}

// Item actions using store
async function toggleItem(itemId: string) {
    try {
        await checklistStore.toggleChecklistItem(props.checklistId, itemId);
    } catch (err) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to toggle item" });
    }
}

function startEdit(itemId: string) {
    const item = items.value.find(i => i.id === itemId);
    if (item) {
        editingItems.value[itemId] = {
            editing: true,
            originalText: item.text
        };
    }
}

function updateItemText(itemId: string, newText: string) {
    if (!editingItems.value[itemId]) return;
    // Store the new text temporarily in editingItems
    editingItems.value[itemId] = {
        ...editingItems.value[itemId],
        newText
    } as any;
}

async function saveEdit(itemId: string) {
    const editState = editingItems.value[itemId];
    if (!editState) return;

    const newText = (editState as any).newText;
    if (!newText) {
        delete editingItems.value[itemId];
        return;
    }

    try {
        await checklistStore.updateChecklistItem(props.checklistId, itemId, {
            text: newText
        });
        delete editingItems.value[itemId];
    } catch (err) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to save edit" });
    }
}

function cancelEdit(itemId: string) {
    delete editingItems.value[itemId];
}

function isEditing(itemId: string): boolean {
    return editingItems.value[itemId]?.editing || false;
}

async function addItem() {
    if (!newItemText.value.trim()) return;

    try {
        await checklistStore.createChecklistItem(props.checklistId, {
            text: newItemText.value.trim()
        });
        newItemText.value = '';
        showAddInput.value = false;
    } catch (err) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to add item" });
    }
}

function handleAddBlur() {
    // Small delay to allow button click to register
    setTimeout(() => {
        if (showAddInput.value && !newItemText.value.trim()) {
            cancelAdd();
        }
    }, 200);
}

function cancelAdd() {
    newItemText.value = '';
    showAddInput.value = false;
}

async function deleteItem(itemId: string) {
    try {
        await checklistStore.deleteChecklistItem(props.checklistId, itemId);
    } catch (err) {
        toast.add({ severity: "error", summary: "Error", detail: "Failed to delete item" });
    }
}
</script>

<style scoped>
.checklist {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.checklist-header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.checklist-title {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    font-size: 1rem;
}

.checklist-title .title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.checklist-header .spacer {
    flex: 1;
}

.checklist-header .actions {
    display: flex;
    gap: 0.5rem;
}

.checklist-progress {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.875rem;
    color: var(--p-gray-500);
}

.progress-bar {
    flex: 1;
    height: 8px;
    background: var(--p-surface-200);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--p-primary-color);
    transition: width 0.3s ease;
    border-radius: 4px;
}

.checklist-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.checklist-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    border: 1px solid var(--p-gray-300);
    border-radius: 10px;
    transition: background-color 0.2s;
}

.checklist-item:hover {
    background-color: var(--p-surface-100);
}

.checklist-item.is-completed .item-text {
    text-decoration: line-through;
    color: var(--p-gray-400);
}

.item-content {
    flex: 1;
    cursor: pointer;
    min-width: 0;
}

.item-text {
    word-break: break-word;
}

.item-input {
    width: 100%;
}

.item-actions {
    display: flex;
    gap: 0.25rem;
    opacity: 0;
    transition: opacity 0.2s;
}

.checklist-item:hover .item-actions {
    opacity: 1;
}

.add-item {
    padding: 0.5rem;
}

.add-item .item-actions {
    opacity: 1;
}

.add-item-button {
    width: 100%;
    justify-content: flex-start;
}
</style>
