<template>
    <Dialog
        v-model:visible="isDialogVisible"
        modal
        :header="'Notification Settings'"
        :style="{ width: '30rem' }"
        :dismissableMask="true"
    >
        <div class="notification-settings">
            <!-- Unsupported Browser Message -->
            <div v-if="showUnsupportedMessage" class="message-box unsupported-message">
                <FontAwesomeIcon icon="fa-solid fa-exclamation-triangle" class="message-icon" />
                <div class="message-content">
                    <p class="message-title">{{ supportInfo.warningMessage }}</p>
                    <p class="message-help">{{ supportInfo.helpMessage }}</p>
                </div>
            </div>

            <!-- Brave Browser Warning -->
            <div v-else-if="showBraveWarning" class="message-box brave-warning">
                <FontAwesomeIcon icon="fa-solid fa-exclamation-circle" class="message-icon" />
                <div class="message-content">
                    <p class="message-title">{{ supportInfo.warningMessage }}</p>
                    <div class="brave-instructions">
                        <p><strong>Setup instructions:</strong></p>
                        <ol>
                            <li>Click the menu in your address bar</li>
                            <li>Navigate to: <code>Settings → Privacy and security</code></li>
                            <li>Enable <strong>"Use Google services for push messaging"</strong></li>
                            <li>Refresh this page and try enabling notifications again</li>
                        </ol>
                    </div>
                </div>
            </div>

            <!-- Main Notification Controls -->
            <template v-if="supportInfo.canAttempt">
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
                        v-if="canEnableNotifications"
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

                <!-- Test Notification Section -->
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

                <!-- Permission Denied Help -->
                <div v-if="permission === 'denied'" class="message-box denied-message">
                    <FontAwesomeIcon icon="fa-solid fa-exclamation-triangle" class="message-icon" />
                    <div class="message-content">
                        <p class="message-title">Notifications blocked</p>
                        <p class="message-help">
                            To enable them, you need to allow notifications in your browser settings.
                            Look for a lock or info icon in your address bar.
                        </p>
                    </div>
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
    getBrowserNotificationCapability,
    getUserSubscriptions,
    type NotificationSupportInfo,
} from '@/services/notificationService';

const props = defineProps<{
    visible: boolean;
}>();

const emit = defineEmits<{
    (event: 'update:visible', value: boolean): void;
}>();

const toast = useToast();
const permission = ref<NotificationPermission>('default');
const supportInfo = ref<NotificationSupportInfo>({
    capability: 'fully-supported',
    isSupported: true,
    canAttempt: true
});
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

const showBraveWarning = computed(() => supportInfo.value.capability === 'brave');

const showUnsupportedMessage = computed(() => !supportInfo.value.canAttempt);

const canEnableNotifications = computed(() => {
    return supportInfo.value.canAttempt &&
           (permission.value !== 'granted' || !hasSubscriptions.value);
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
    supportInfo.value = await getBrowserNotificationCapability();

    if (supportInfo.value.canAttempt) {
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

/* Message Box Base Styles */
.message-box {
    display: flex;
    align-items: flex-start;
    gap: 0.875rem;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid;
}

.message-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
    margin-top: 0.125rem;
}

.message-content {
    flex: 1;
}

.message-title {
    margin: 0 0 0.5rem 0;
    font-weight: 600;
    line-height: 1.4;
}

.message-help {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.5;
    white-space: pre-line;
}

/* Unsupported Browser Styling */
.unsupported-message {
    background-color: var(--p-yellow-50);
    border-color: var(--p-yellow-200);
    color: var(--p-yellow-900);
}

.unsupported-message .message-icon {
    color: var(--p-yellow-600);
}

/* Brave Browser Warning Styling */
.brave-warning {
    background-color: var(--p-blue-50);
    border-color: var(--p-blue-200);
    color: var(--p-blue-900);
}

.brave-warning .message-icon {
    color: var(--p-blue-600);
}

.brave-instructions {
    margin-top: 0.75rem;
}

.brave-instructions p {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
}

.brave-instructions ol {
    margin: 0.5rem 0 0 0;
    padding-left: 1.25rem;
    font-size: 0.875rem;
    line-height: 1.6;
}

.brave-instructions li {
    margin-bottom: 0.375rem;
}

.brave-instructions code {
    background-color: rgba(0, 0, 0, 0.08);
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.813rem;
}

/* Permission Denied Styling */
.denied-message {
    background-color: var(--p-red-50);
    border-color: var(--p-red-200);
    color: var(--p-red-900);
}

.denied-message .message-icon {
    color: var(--p-red-600);
}

/* Permission Status */
.permission-status {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background-color: var(--p-content-hover-background);
    border-radius: 6px;
}

.status-label {
    font-weight: 600;
    color: var(--p-text-color);
}

/* Description */
.description {
    margin: 0;
    color: var(--p-text-muted-color);
    line-height: 1.5;
}

/* Actions */
.actions {
    display: flex;
    gap: 0.75rem;
}

/* Test Section */
.test-section {
    padding: 0.75rem;
    background-color: var(--p-content-hover-background);
    border: 1px dashed var(--p-content-border-color);
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
