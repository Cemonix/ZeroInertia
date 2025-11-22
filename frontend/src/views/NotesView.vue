<template>
    <WorkspaceLayout>
        <template #sidebar>
            <NoteExplorerPanel
                :show-backlinks="showBacklinks"
                @toggle-backlinks="toggleBacklinks"
            />
        </template>
        <template #navbar-left>
            <Button
                class="home-nav-btn"
                text
                rounded
                @click="goHome"
                aria-label="Return to home"
            >
                <FontAwesomeIcon icon="house" />
                <span class="home-nav-label">Home</span>
            </Button>
            <Button
                class="media-nav-btn"
                text
                rounded
                @click="goToMedia"
                aria-label="Go to media"
            >
                <FontAwesomeIcon icon="table-columns" />
                <span class="media-nav-label">Media</span>
            </Button>
        </template>
        <div
            class="notes-content"
            :class="{ 'backlinks-open': showBacklinks && isMobileViewport }"
        >
            <NoteEditor class="editor-panel" />
            <BacklinksPanel
                v-if="showBacklinks"
                class="backlinks-sidebar"
                :note-id="selectedNoteId"
                @select-note="handleNoteSelect"
            />
        </div>
    </WorkspaceLayout>
</template>

<script lang="ts" setup>
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useNoteStore } from "@/stores/note";
import { useUiStore } from "@/stores/ui";
import { storeToRefs } from "pinia";
import NoteExplorerPanel from "@/components/notes/NoteExplorerPanel.vue";
import NoteEditor from "@/components/notes/NoteEditor.vue";
import BacklinksPanel from "@/components/notes/BacklinksPanel.vue";
import WorkspaceLayout from "@/layouts/WorkspaceLayout.vue";

const authStore = useAuthStore();
const noteStore = useNoteStore();
const uiStore = useUiStore();
const router = useRouter();

const { selectedNoteId } = storeToRefs(noteStore);
const showBacklinks = ref(true);
const isMobileViewport = ref(false);

const loadBacklinksPreference = (): boolean => {
    const stored = localStorage.getItem('notes.showBacklinks');
    return stored !== null ? stored === 'true' : true;
};

const saveBacklinksPreference = (value: boolean) => {
    localStorage.setItem('notes.showBacklinks', value.toString());
};

const goHome = () => {
    if (router.currentRoute.value.path !== "/home") {
        router.push("/home");
    }
};

const goToMedia = () => {
    if (router.currentRoute.value.path !== "/media") {
        router.push("/media");
    }
};

const loadNotes = async () => {
    if (!authStore.isAuthenticated) return;
    await noteStore.loadNotes();
};

const handleNoteSelect = (noteId: string) => {
    noteStore.selectNote(noteId);
};

const toggleBacklinks = () => {
    showBacklinks.value = !showBacklinks.value;
    saveBacklinksPreference(showBacklinks.value);
};

const syncViewport = () => {
    const isMobile = typeof window !== "undefined" && window.innerWidth < 1024;
    const wasntMobile = !isMobileViewport.value;

    if (isMobile !== isMobileViewport.value) {
        isMobileViewport.value = isMobile;

        if (isMobile) {
            showBacklinks.value = false;
        } else if (wasntMobile) {
            showBacklinks.value = loadBacklinksPreference();
        }
    }
};

onMounted(() => {
    showBacklinks.value = loadBacklinksPreference();
    syncViewport();
    window.addEventListener("resize", syncViewport);
    void loadNotes();
});

onUnmounted(() => {
    window.removeEventListener("resize", syncViewport);
});

// Close sidebar on mobile when a note is selected (or created)
watch(selectedNoteId, (newNoteId) => {
    if (!newNoteId) return;
    const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
    if (isMobile) uiStore.setSidebarCollapsed(true);
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

.media-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
    transition: all 0.2s ease;
}

.media-nav-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}

@media (max-width: 768px) {
    .home-nav-label,
    .media-nav-label {
        display: none;
    }
}

.notes-content {
    display: flex;
    gap: 1rem;
    height: 100%;
    overflow: hidden;
    padding: 1rem;
    box-sizing: border-box;
    --backlinks-width: clamp(260px, 70vw, 340px);
}

.editor-panel {
    flex: 1;
    min-width: 0;
}

.backlinks-sidebar {
    width: 300px;
    flex-shrink: 0;
    transition: all 0.3s ease;
    background: var(--p-content-background);
}

@media (max-width: 1024px) {
    .notes-content {
        position: relative;
    }

    .notes-content.backlinks-open {
        padding-right: calc(var(--backlinks-width) + 0.75rem);
    }

    .backlinks-sidebar {
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        width: var(--backlinks-width);
        box-shadow: -8px 0 24px rgba(0, 0, 0, 0.12);
        border-left: 1px solid var(--p-content-border-color);
        background: var(--p-content-background);
        z-index: 5;
    }

    .editor-panel {
        width: 100%;
    }
}

@media (max-width: 768px) {
    .notes-content {
        padding: 0.75rem;
    }

    .notes-content.backlinks-open {
        padding-right: 0;
    }

    .backlinks-sidebar {
        width: 100vw;
        left: 0;
        right: 0;
        box-shadow: none;
        border-left: none;
        border-top: 1px solid var(--p-content-border-color);
    }
}
</style>
