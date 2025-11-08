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

const toast = useToast();

// Set up foreground notification listener when app mounts
onMounted(async () => {
    try {
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
});
</script>