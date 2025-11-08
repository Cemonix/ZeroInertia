import { defineStore } from "pinia";
import { ref } from "vue";

export const useUiStore = defineStore("ui", () => {
    const isSidebarCollapsed = ref(false);

    function setSidebarCollapsed(value: boolean) {
        isSidebarCollapsed.value = value;
    }

    function toggleSidebar() {
        isSidebarCollapsed.value = !isSidebarCollapsed.value;
    }

    return {
        isSidebarCollapsed,
        setSidebarCollapsed,
        toggleSidebar,
    };
});

