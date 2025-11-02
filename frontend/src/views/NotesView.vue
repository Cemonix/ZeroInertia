<template>
    <WorkspaceLayout>
        <template #sidebar>
            <NoteExplorerPanel />
        </template>
        <template #navbar-left>
            <Button
                class="home-nav-btn"
                text
                rounded
                @click="goHome"
                aria-label="Return to home"
            >
                <font-awesome-icon icon="house" />
                <span class="home-nav-label">Home</span>
            </Button>
        </template>
        <NoteEditor />
    </WorkspaceLayout>
</template>

<script lang="ts" setup>
import { onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useNoteStore } from "@/stores/note";
import NoteExplorerPanel from "@/components/notes/NoteExplorerPanel.vue";
import NoteEditor from "@/components/notes/NoteEditor.vue";
import WorkspaceLayout from "@/layouts/WorkspaceLayout.vue";

const authStore = useAuthStore();
const noteStore = useNoteStore();
const router = useRouter();

const goHome = () => {
    if (router.currentRoute.value.path !== "/home") {
        router.push("/home");
    }
};

const loadNotes = async () => {
    if (!authStore.isAuthenticated) return;
    await noteStore.loadNotes();
};

onMounted(() => {
    void loadNotes();
});

watch(
    () => authStore.isAuthenticated,
    (isAuthenticated) => {
        if (isAuthenticated) {
            void loadNotes();
        }
    },
);
</script>

<style scoped>
.home-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
    transition: all 0.2s ease;
}

.home-nav-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}
</style>
