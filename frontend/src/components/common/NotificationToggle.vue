<template>
    <Dialog
        v-model:visible="isDialogVisible"
        modal
        :header="'Notification Settings'"
        :style="{ width: '30rem' }"
        :dismissableMask="true"
    >
        <div class="notification-settings">
            <div v-if="!isSupported" class="not-supported-message">
                <i class="fa fa-exclamation-triangle"></i>
                <p>Push notifications are not supported in your browser.</p>
            </div>
            <template v-else>
                <div class="permission-status">
                    <span class="status-label">Status:</span>
                    <Tag
                        :severity="permissionSeverity"
                        :value="permissionText"
                    />
                </div>

                <p class="description">
                    Get notified about upcoming tasks before they're due.
                </p>

                <div class="actions">
                    <Button
                        v-if="permission !== 'granted' || !hasSubscriptions"
                        @click="handleEnableNotifications"
                        :disabled="permission === 'denied' || isLoading"
                        :loading="isLoading"
                        severity="primary"
                        label="Enable Notifications"
                        icon="fa fa-bell"
                    />
                    <Button
                        v-else
                        @click="handleDisableNotifications"
                        :disabled="isLoading"
                        :loading="isLoading"
                        severity="danger"
                        label="Disable Notifications"
                        icon="fa fa-bell-slash"
                    />
                </div>

                <div v-if="permission === 'granted' && hasSubscriptions" class="test-section">
                    <p class="test-description">Test your notification setup:</p>
                    <Button
                        @click="handleTestNotification"
                        :disabled="isLoading"
                        :loading="isLoading"
                        severity="secondary"
                        outlined
                        label="Send Test Notification"
                        icon="fa fa-bell"
                    />
                </div>

                <div v-if="permission === 'denied'" class="denied-help">
                    <p>
                        <strong>Notifications blocked.</strong>
                        To enable them, you need to allow notifications in your browser settings.
                    </p>
                </div>
            </template>
        </div>
    </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import apiClient from '@/services/apiClient';
import {
    subscribeToNotifications,
    unsubscribeFromNotifications,
    getNotificationPermission,
    isNotificationSupported,
    getUserSubscriptions,
} from '@/services/notificationService';

const props = defineProps<{
    visible: boolean;
}>();

const emit = defineEmits<{
    (event: 'update:visible', value: boolean): void;
}>();

const toast = useToast();
const permission = ref<NotificationPermission>('default');
const isSupported = ref(true);
const isLoading = ref(false);
const hasSubscriptions = ref(false);

const isDialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value),
});

const permissionSeverity = computed(() => {
    if (permission.value === 'denied') return 'danger';
    if (permission.value === 'granted' && hasSubscriptions.value) return 'success';
    return 'warn';
});

const permissionText = computed(() => {
    if (permission.value === 'denied') return 'Blocked';
    if (permission.value === 'granted' && hasSubscriptions.value) return 'Enabled';
    return 'Disabled';
});

const updatePermissionStatus = () => {
    permission.value = getNotificationPermission();
};

const refreshSubscriptionStatus = async () => {
    try {
        const subs = await getUserSubscriptions();
        hasSubscriptions.value = subs.length > 0;
    } catch (e) {
        // If we cannot fetch, assume not subscribed to avoid showing a misleading Enabled state
        console.warn('Unable to fetch subscriptions:', e);
        hasSubscriptions.value = false;
    }
};

const handleEnableNotifications = async () => {
    if (isLoading.value) return;

    isLoading.value = true;
    try {
        await subscribeToNotifications();
        updatePermissionStatus();
        await refreshSubscriptionStatus();

        if (permission.value === 'granted') {
            toast.add({
                severity: 'success',
                summary: 'Notifications Enabled',
                detail: 'You will now receive task reminders',
                life: 3000,
            });
        } else if (permission.value === 'denied') {
            toast.add({
                severity: 'error',
                summary: 'Permission Denied',
                detail: 'Please allow notifications in your browser settings',
                life: 5000,
            });
        }
    } catch (error: any) {
        console.error('Error enabling notifications:', error);

        const isBraveError = error?.message?.includes('Brave') ||
                            error?.message?.includes('Google services for push');

        toast.add({
            severity: 'error',
            summary: isBraveError ? 'Browser Settings Required' : 'Failed to Enable Notifications',
            detail: error?.message || 'Failed to enable notifications. Please try again.',
            life: isBraveError ? 0 : 5000, // Sticky toast for Brave users
        });
    } finally {
        isLoading.value = false;
    }
};

const handleDisableNotifications = async () => {
    if (isLoading.value) return;

    isLoading.value = true;
    try {
        await unsubscribeFromNotifications();
        updatePermissionStatus();
        hasSubscriptions.value = false;
        toast.add({
            severity: 'info',
            summary: 'Notifications Disabled',
            detail: 'You will no longer receive task reminders',
            life: 3000,
        });
    } catch (error) {
        console.error('Error disabling notifications:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to disable notifications. Please try again.',
            life: 5000,
        });
    } finally {
        isLoading.value = false;
    }
};

const handleTestNotification = async () => {
    if (isLoading.value) return;

    isLoading.value = true;
    try {
        await apiClient.post('/api/v1/notifications/test', {
            title: 'Test Notification',
            body: 'This is a test notification from Zero Inertia!'
        });

        toast.add({
            severity: 'success',
            summary: 'Test Sent',
            detail: 'Check your notifications!',
            life: 3000,
        });
    } catch (error: any) {
        console.error('Error sending test notification:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error?.response?.data?.detail || 'Failed to send test notification',
            life: 5000,
        });
    } finally {
        isLoading.value = false;
    }
};

onMounted(async () => {
    isSupported.value = await isNotificationSupported();
    if (isSupported.value) {
        updatePermissionStatus();
        await refreshSubscriptionStatus();
    }
});
</script>

<style scoped>
.notification-settings {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.not-supported-message {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background-color: var(--p-yellow-50);
    border: 1px solid var(--p-yellow-200);
    border-radius: 6px;
    color: var(--p-yellow-900);
}

.not-supported-message i {
    font-size: 1.5rem;
}

.permission-status {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background-color: var(--p-surface-50);
    border-radius: 6px;
}

.status-label {
    font-weight: 600;
    color: var(--p-text-color);
}

.description {
    margin: 0;
    color: var(--p-text-muted-color);
    line-height: 1.5;
}

.actions {
    display: flex;
    gap: 0.75rem;
}

.denied-help {
    padding: 0.75rem;
    background-color: var(--p-red-50);
    border: 1px solid var(--p-red-200);
    border-radius: 6px;
}

.denied-help p {
    margin: 0;
    color: var(--p-red-900);
    font-size: 0.875rem;
    line-height: 1.5;
}

.test-section {
    padding: 0.75rem;
    background-color: var(--p-surface-100);
    border: 1px dashed var(--p-surface-300);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.test-description {
    margin: 0;
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}
</style>
