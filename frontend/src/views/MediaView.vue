<template>
    <WorkspaceLayout>
        <template #sidebar>
            <div class="media-categories">
                <div class="panel-header">
                    <h2 class="panel-title">Categories</h2>
                </div>
                <div class="category-buttons">
                    <Button
                        :outlined="activeCategory !== 'all'"
                        @click="setCategory('all')"
                        class="category-btn"
                    >
                        All Media
                    </Button>
                    <Button
                        v-for="type in MEDIA_TYPES"
                        :key="type.value"
                        :outlined="activeCategory !== type.value"
                        @click="setCategory(type.value)"
                        class="category-btn"
                    >
                        {{ type.label }}
                    </Button>
                </div>
            </div>
            <div class="media-filters">
                <div class="panel-header">
                    <h2 class="panel-title">Media Filters</h2>
                </div>
                <div class="panel-content">
                    <div class="field">
                        <label>Status</label>
                        <MultiSelect
                            v-model="selectedStatuses"
                            :options="MEDIA_STATUSES"
                            optionLabel="label"
                            optionValue="value"
                            display="chip"
                            placeholder="All statuses"
                        />
                    </div>
                    <div class="field">
                        <label>Search</label>
                        <InputText v-model.trim="search" placeholder="Title or notes" />
                    </div>
                    <div class="field">
                        <label>Rating range</label>
                        <Slider v-model="ratingRange" range :min="0" :max="100" />
                        <div class="range-labels">
                            <span>{{ ratingRange[0] }}</span>
                            <span>{{ ratingRange[1] }}</span>
                        </div>
                    </div>
                    <div class="actions">
                        <Button @click="applyFilters" :disabled="loading">Apply</Button>
                        <Button text @click="clearFilters" :disabled="!hasActiveFilters">Clear</Button>
                    </div>
                </div>
            </div>
        </template>
        <template #navbar-left>
            <Button class="home-nav-btn" text rounded @click="goHome" aria-label="Return to home">
                <font-awesome-icon icon="house" />
                <span class="home-nav-label">Home</span>
            </Button>
            <Button class="notes-nav-btn" text rounded @click="goToNotes" aria-label="Go to notes">
                <font-awesome-icon icon="pen" />
                <span class="notes-nav-label">Notes</span>
            </Button>
        </template>
        <div class="media-view">
            <div class="toolbar">
                <Button @click="openCreate" aria-label="Add media">Add Media</Button>
                <span class="muted" v-if="hasActiveFilters">Filters active</span>
            </div>
            <div v-if="!loading && filteredItems.length === 0" class="empty-state-centered">
                <h3 class="empty-state-title">No Media To Display</h3>
                <p class="empty-state-subtitle">Add your first item to get started.</p>
            </div>
            <MediaTable
                v-else
                :key="activeCategory"
                :items="filteredItems"
                :loading="loading"
                :type="activeCategory === 'all' ? undefined : activeCategory"
                @edit="openEdit"
                @delete="onDelete"
            />
        </div>
        <MediaForm v-model:visible="formVisible" :item="editingItem" @saved="reload" />
    </WorkspaceLayout>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import WorkspaceLayout from '@/layouts/WorkspaceLayout.vue';
import MediaTable from '@/components/media/MediaTable.vue';
import MediaForm from '@/components/media/MediaForm.vue';
import Slider from 'primevue/slider';
import MultiSelect from 'primevue/multiselect';
import InputText from 'primevue/inputtext';
import { MEDIA_STATUSES, MEDIA_TYPES, type MediaType } from '@/models/media';
import { useMediaStore } from '@/stores/media';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';

const authStore = useAuthStore();
const mediaStore = useMediaStore();
const router = useRouter();

const { filteredItems, loading, formVisible, editingItem, selectedStatuses, ratingMin, ratingMax, search, hasActiveFilters, activeCategory } = storeToRefs(mediaStore);

const ratingRange = ref<[number, number]>([ratingMin.value, ratingMax.value]);
watch([ratingMin, ratingMax], () => { ratingRange.value = [ratingMin.value, ratingMax.value]; });
watch(ratingRange, ([min, max]) => { ratingMin.value = min; ratingMax.value = max; });

const goHome = () => { if (router.currentRoute.value.path !== '/home') router.push('/home'); };
const goToNotes = () => { if (router.currentRoute.value.path !== '/notes') router.push('/notes'); };

const reload = async () => { await mediaStore.load(); };

const applyFilters = async () => { await reload(); };
const clearFilters = async () => { mediaStore.clearFilters(); await reload(); };

const setCategory = (category: 'all' | MediaType) => {
    mediaStore.setActiveCategory(category);
};

const openCreate = () => mediaStore.openCreateForm();
const openEdit = (item: any) => mediaStore.openEditForm(item);
const onDelete = async (item: any) => {
    // Close the form BEFORE deleting if this item is being edited
    if (editingItem.value && editingItem.value.id === item.id) {
        mediaStore.closeForm();
    }
    await mediaStore.remove(item.id, item.media_type);
};

onMounted(async () => {
    if (authStore.isAuthenticated) {
        await reload();
    }
});

watch(() => authStore.isAuthenticated, async (isAuth) => {
    if (isAuth) await reload();
});
</script>

<style scoped>
.media-categories {
    display: flex;
    flex-direction: column;
}
.category-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.75rem;
}
.category-btn {
    width: 100%;
    justify-content: flex-start;
}
.media-filters {
    display: flex;
    flex-direction: column;
}
.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1rem 0.75rem 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
}
.panel-title { font-size: 1.125rem; font-weight: 600; margin: 0; }
.panel-content { display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.5rem; }
.actions { display: flex; gap: 0.5rem; align-items: center; }
.range-labels { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--p-text-muted-color); }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.muted { color: var(--p-text-muted-color); font-size: 0.9rem; }
.notes-nav-btn { display: inline-flex; align-items: center; gap: 0.4rem; color: var(--p-text-color); }
.notes-nav-btn:hover { background-color: var(--p-content-hover-background); color: var(--p-primary-color); }

/* Centered empty state */
.empty-state-centered {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    min-height: 240px;
    text-align: center;
    color: var(--p-text-muted-color);
}
.empty-state-title {
    margin: 0;
    font-weight: 700;
    color: var(--p-text-color);
}
.empty-state-subtitle { margin: 0; }
</style>
