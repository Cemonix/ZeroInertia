<template>
    <div class="media-quick-actions">
        <Button
            text
            rounded
            size="small"
            class="media-menu-trigger"
            aria-haspopup="true"
            :aria-controls="menuId"
            aria-label="Media options"
            @click.stop="toggleMenu"
        >
            <template #icon>
                <FontAwesomeIcon icon="ellipsis" />
            </template>
        </Button>
        <Menu
            :id="menuId"
            ref="menuRef"
            :model="menuItems"
            :popup="true"
        >
            <template #item="{ item }">
                <div class="menu-item-content">
                    <FontAwesomeIcon v-if="item.icon" :icon="item.icon" class="menu-item-icon" />
                    <span>{{ item.label }}</span>
                </div>
            </template>
        </Menu>
    </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import Button from "primevue/button";
import Menu from "primevue/menu";
import type { MenuItem } from "primevue/menuitem";
import type { MediaItem } from "@/models/media";
import { useMediaStore } from "@/stores/media";

const props = defineProps<{
    item: MediaItem;
}>();

type MediaMenuInstance = {
    toggle: (event: MouseEvent) => void;
    hide: () => void;
};

const mediaStore = useMediaStore();

const menuRef = ref<MediaMenuInstance | null>(null);

const menuId = computed(() => `media_menu_${props.item.id}`);

const toggleMenu = (event: MouseEvent) => {
    menuRef.value?.toggle(event);
};

const closeMenu = () => {
    menuRef.value?.hide();
};

const handleUseAsTemplate = () => {
    closeMenu();
    mediaStore.openCreateFormFromTemplate(props.item);
};

const menuItems = computed<MenuItem[]>(() => [
    {
        label: "Use as template",
        icon: "copy",
        command: () => handleUseAsTemplate(),
    },
]);
</script>

<style scoped>
.media-quick-actions {
    display: flex;
    align-items: center;
    justify-content: center;
}

.menu-item-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem;
    width: 100%;
    cursor: pointer;
    user-select: none;
}

.menu-item-icon {
    width: 1rem;
    color: var(--p-text-muted-color);
}
</style>
