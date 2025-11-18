<template>
    <div id="app">
        <ConfirmDialog />
        <Toast />
        <RouterView />
    </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { setupForegroundMessageListener } from '@/services/notificationService';
import { useTaskStore } from '@/stores/task';
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts';
import apiClient from '@/services/apiClient';

const toast = useToast();
const taskStore = useTaskStore();
const { register } = useKeyboardShortcuts();

// Set up foreground notification listener when app mounts
onMounted(async () => {
    try {
        // Prime CSRF token early on first app load
        try {
            await apiClient.get('/csrf');
        } catch (e) {
            // Non-fatal; interceptor will attempt lazy fetch on first unsafe request
            console.debug('CSRF prefetch failed (will retry lazily)', e);
        }

        await setupForegroundMessageListener((payload) => {
            console.log('Received foreground notification:', payload);

            const title = payload.notification?.title || 'Zero Inertia';
            const body = payload.notification?.body || '';

            toast.add({
                severity: 'info',
                summary: title,
                detail: body,
                life: 5000,
            });
        });
    } catch (error) {
        console.error('Failed to setup foreground notification listener:', error);
    }

    // Register global keyboard shortcuts
    register({
        key: 'a',
        ctrl: true,
        meta: true,
        handler: () => {
            if (!taskStore.isTaskModalVisible) {
                taskStore.openTaskModal(null);
            }
        },
        description: 'Quick add task',
    });
});
</script>
