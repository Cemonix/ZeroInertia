// Firebase Cloud Messaging Service Worker
// Handles push notifications when the app is in the background or closed
// NOTE: This is a TEMPLATE file - do not commit with real credentials
// The actual service worker is generated during build with environment variables

// Import Firebase scripts (loaded from CDN)
// Version is automatically set from package.json during build
importScripts(
    "https://www.gstatic.com/firebasejs/__FIREBASE_VERSION__/firebase-app-compat.js"
);
importScripts(
    "https://www.gstatic.com/firebasejs/__FIREBASE_VERSION__/firebase-messaging-compat.js"
);

// Initialize Firebase in the service worker
// These placeholders are replaced during build with actual env vars
const firebaseConfig = {
  apiKey: "__VITE_FIREBASE_API_KEY__",
  authDomain: "__VITE_FIREBASE_AUTH_DOMAIN__",
  projectId: "__VITE_FIREBASE_PROJECT_ID__",
  storageBucket: "__VITE_FIREBASE_STORAGE_BUCKET__",
  messagingSenderId: "__VITE_FIREBASE_MESSAGING_SENDER_ID__",
  appId: "__VITE_FIREBASE_APP_ID__",
  measurementId: "__VITE_FIREBASE_MEASUREMENT_ID__"
};

firebase.initializeApp(firebaseConfig);


// Retrieve Firebase Messaging instance
const messaging = firebase.messaging();

// Handle background messages (when app is not in focus)
messaging.onBackgroundMessage((payload) => {
    console.log(
        "[firebase-messaging-sw.js] Received background message:",
        payload
    );

    // Extract notification data from payload.data (data-only messages)
    const data = payload.data || {};
    const notificationTitle = data.title || payload.notification?.title || "Zero Inertia";
    const notificationOptions = {
        body: data.body || payload.notification?.body || "",
        icon: data.icon || payload.notification?.icon || "/ZeroInertia.svg",
        badge: data.badge || payload.notification?.badge || "/ZeroInertia.svg",
        data: data,
        tag: data.task_id || "default", // Prevents duplicate notifications for same task
        requireInteraction: false, // Auto-dismiss after a while
    };

    // Show the notification
    self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click events
self.addEventListener("notificationclick", (event) => {
    console.log(
        "[firebase-messaging-sw.js] Notification clicked:",
        event.notification
    );

    event.notification.close();

    // Get task data from notification
    const taskId = event.notification.data?.task_id;
    const notificationType = event.notification.data?.type;

    // Determine URL to open
    let urlToOpen = "/";
    if (notificationType === "task_reminder" && taskId) {
        // TODO: Navigate to specific task when task detail pages are implemented
        urlToOpen = `/home`;
    }

    // Open or focus the app
    event.waitUntil(
        clients
            .matchAll({ type: "window", includeUncontrolled: true })
            .then((clientList) => {
                // Check if app is already open
                for (const client of clientList) {
                    if (
                        client.url ===
                            new URL(urlToOpen, self.location.origin).href &&
                        "focus" in client
                    ) {
                        return client.focus();
                    }
                }

                // If app is not open, open it
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});
