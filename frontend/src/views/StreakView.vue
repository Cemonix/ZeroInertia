<template>
    <WorkspaceLayout>
        <template #sidebar>
            <div class="streak-sidebar">
                <div class="sidebar-header">
                    <h2 class="sidebar-title">Streak insights</h2>
                    <p class="sidebar-subtitle">
                        Track how often you complete tasks and keep your motivation high.
                    </p>
                </div>
                <ul class="sidebar-tips">
                    <li>Complete at least one task every day to build your streak.</li>
                    <li>Use due dates and reminders to stay consistent.</li>
                    <li>Review your calendar to spot productive days and patterns.</li>
                </ul>
            </div>
        </template>

        <template #navbar-left>
            <Button
                class="nav-btn"
                text
                rounded
                @click="goHome"
                aria-label="Go to home"
            >
                <font-awesome-icon icon="house" />
                <span class="nav-label">Home</span>
            </Button>
            <Button
                class="nav-btn"
                text
                rounded
                @click="goToNotes"
                aria-label="Go to notes"
            >
                <font-awesome-icon icon="pen" />
                <span class="nav-label">Notes</span>
            </Button>
            <Button
                class="nav-btn"
                text
                rounded
                @click="goToMedia"
                aria-label="Go to media"
            >
                <font-awesome-icon icon="table-columns" />
                <span class="nav-label">Media</span>
            </Button>
        </template>

        <StreakBoard />
    </WorkspaceLayout>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import WorkspaceLayout from "@/layouts/WorkspaceLayout.vue";
import StreakBoard from "@/components/streak/StreakBoard.vue";

const router = useRouter();

const goHome = () => {
    if (router.currentRoute.value.path !== "/home") {
        router.push("/home");
    }
};

const goToNotes = () => {
    if (router.currentRoute.value.path !== "/notes") {
        router.push("/notes");
    }
};

const goToMedia = () => {
    if (router.currentRoute.value.path !== "/media") {
        router.push("/media");
    }
};
</script>

<style scoped>
.streak-sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
}

.sidebar-header {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}

.sidebar-title {
    margin: 0;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--p-text-color);
}

.sidebar-subtitle {
    margin: 0;
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}

.sidebar-tips {
    margin: 0;
    padding-left: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    font-size: 0.85rem;
    color: var(--p-text-muted-color);
}

.nav-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--p-text-color);
    transition: all 0.2s ease;
}

.nav-btn:hover {
    background-color: var(--p-content-hover-background);
    color: var(--p-primary-color);
}
</style>

