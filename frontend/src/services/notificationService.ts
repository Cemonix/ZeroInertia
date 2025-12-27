/**
 * Push Notification Service
 * Handles push notification subscriptions using Firebase Cloud Messaging
 */
import { getToken, onMessage, deleteToken } from "firebase/messaging";
import { getMessagingInstance } from "@/config/firebase";
import apiClient from "./apiClient";
import { VAPID_PUBLIC_KEY } from "@/config/firebase";

export interface PushSubscription {
    id: string;
    user_id: string;
    endpoint: string;
    user_agent: string | null;
    created_at: string;
    updated_at: string;
}

export type BrowserNotificationCapability = 'fully-supported' | 'brave' | 'unsupported';

export interface NotificationSupportInfo {
    capability: BrowserNotificationCapability;
    isSupported: boolean;
    canAttempt: boolean;
    warningMessage?: string;
    helpMessage?: string;
}

/**
 * Reliably detect if the browser is Brave
 * Uses the official Brave detection API which returns a Promise
 */
async function detectBraveBrowser(): Promise<boolean> {
    try {
        return (navigator as any).brave && await (navigator as any).brave.isBrave?.() === true;
    } catch {
        return false;
    }
}

/**
 * Request notification permission from the user
 * @returns Permission state: 'granted', 'denied', or 'default'
 */
export async function requestNotificationPermission(): Promise<NotificationPermission> {
    if (!("Notification" in window)) {
        return "denied";
    }

    return await Notification.requestPermission();
}

/**
 * Subscribe to push notifications
 * Gets FCM token and sends it to the backend
 * @throws Error if subscription fails
 */
export async function subscribeToNotifications(): Promise<void> {
    try {
        const messaging = await getMessagingInstance();

        if (!messaging) {
            throw new Error("Firebase Messaging is not supported in this browser");
        }

        const permission = await requestNotificationPermission();

        if (permission !== "granted") {
            throw new Error("Notification permission not granted");
        }

        const swRegistration = await navigator.serviceWorker.ready;

        const token = await getToken(messaging, {
            vapidKey: VAPID_PUBLIC_KEY,
            serviceWorkerRegistration: swRegistration,
        });

        if (!token) {
            throw new Error("Failed to get FCM token from Firebase");
        }

        await apiClient.post("/api/v1/notifications/subscribe", {
            endpoint: token,
            user_agent: navigator.userAgent,
        });
    } catch (error: any) {
        if (error?.name === "AbortError" || error?.message?.includes("Registration failed")) {
            const isBrave = await detectBraveBrowser();
            if (isBrave) {
                throw new Error(
                    "Push notifications are blocked. In Brave, go to Settings → Privacy and security → " +
                    "Use Google services for push messaging, then enable it and try again."
                );
            }
            throw new Error(
                "Push notifications are blocked by your browser or network. " +
                "Check your browser settings or try disabling privacy shields/extensions."
            );
        }
        throw error;
    }
}

/**
 * Unsubscribe from push notifications
 * @throws Error if unsubscription fails
 */
export async function unsubscribeFromNotifications(): Promise<void> {
    const messaging = await getMessagingInstance();

    if (messaging) {
        try {
            await deleteToken(messaging);
        } catch {
            // Continue even if local token deletion fails
        }
    }

    await apiClient.delete("/api/v1/notifications/subscriptions/all");
}

/**
 * Get all push subscriptions for the current user
 * @throws Error if fetching subscriptions fails
 */
export async function getUserSubscriptions(): Promise<PushSubscription[]> {
    const response = await apiClient.get<PushSubscription[]>(
        "/api/v1/notifications/subscriptions"
    );
    return response.data;
}

/**
 * Setup foreground message listener
 * Handles notifications when the app is open and in focus
 * Works with data-only FCM messages for consistent behavior across platforms
 */
export async function setupForegroundMessageListener(
    onMessageReceived: (payload: any) => void
): Promise<void> {
    const messaging = await getMessagingInstance();
    if (!messaging) {
        return;
    }

    onMessage(messaging, (payload) => {
        console.log('Foreground message received:', payload);

        // Extract notification data from payload.data (data-only messages)
        const data = payload.data || {};
        const title = data.title || payload.notification?.title || "Zero Inertia";
        const body = data.body || payload.notification?.body || "";
        const icon = data.icon || payload.notification?.icon || "/ZeroInertia.svg";

        // Call the callback with enhanced payload
        onMessageReceived({
            ...payload,
            notification: {
                title,
                body,
                icon,
            },
            data,
        });

        // Show browser notification if permission is granted
        if (Notification.permission === "granted") {
            new Notification(title, {
                body,
                icon,
                data,
            });
        }
    });
}

/**
 * Check if push notifications are supported in this browser
 */
export async function isNotificationSupported(): Promise<boolean> {
    const info = await getBrowserNotificationCapability();
    return info.isSupported;
}

/**
 * Get current notification permission status
 */
export function getNotificationPermission(): NotificationPermission {
    if (!("Notification" in window)) {
        return "denied";
    }
    return Notification.permission;
}

/**
 * Detect browser notification capability with granular support levels
 * @returns Detailed information about notification support
 */
export async function getBrowserNotificationCapability(): Promise<NotificationSupportInfo> {
    if (!("Notification" in window)) {
        return {
            capability: 'unsupported',
            isSupported: false,
            canAttempt: false,
            warningMessage: 'Your browser does not support push notifications.',
            helpMessage: 'Please upgrade to a modern browser like Chrome, Firefox, Edge, or Safari to receive task reminders.'
        };
    }

    if (!("serviceWorker" in navigator)) {
        return {
            capability: 'unsupported',
            isSupported: false,
            canAttempt: false,
            warningMessage: 'Service Workers are not supported in your browser.',
            helpMessage: 'Please upgrade to a modern browser to enable push notifications.'
        };
    }

    const messaging = await getMessagingInstance();
    if (!messaging) {
        return {
            capability: 'unsupported',
            isSupported: false,
            canAttempt: false,
            warningMessage: 'Firebase Cloud Messaging is not supported in your browser.',
            helpMessage: 'This may be due to browser restrictions or privacy settings.'
        };
    }

    const isBrave = await detectBraveBrowser();

    if (isBrave) {
        return {
            capability: 'brave',
            isSupported: true,
            canAttempt: true,
            warningMessage: 'Brave browser requires additional configuration for push notifications.',
            helpMessage: 'To enable notifications in Brave:\n1. Click the Brave icon in your address bar\n2. Go to Settings → Privacy and security\n3. Enable "Use Google services for push messaging"\n4. Refresh this page and try again'
        };
    }

    return {
        capability: 'fully-supported',
        isSupported: true,
        canAttempt: true
    };
}
