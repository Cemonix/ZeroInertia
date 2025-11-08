/**
 * Firebase configuration for Zero Inertia
 * Handles Firebase initialization and messaging setup
 */
import { initializeApp } from "firebase/app";
import { getMessaging, isSupported } from "firebase/messaging";
import type { FirebaseApp } from "firebase/app";
import type { Messaging } from "firebase/messaging";

export const VAPID_PUBLIC_KEY = import.meta.env.VITE_FIREBASE_VAPID_PUBLIC_KEY;

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase
const app: FirebaseApp = initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging
// This promise resolves when messaging is ready (or null if unsupported)
let messagingPromise: Promise<Messaging | null>;

const initializeMessaging = async (): Promise<Messaging | null> => {
    try {
        const supported = await isSupported();
        if (supported) {
            return getMessaging(app);
        } else {
            console.warn("Firebase Messaging is not supported in this browser");
            return null;
        }
    } catch (error) {
        console.error("Failed to initialize Firebase Messaging:", error);
        return null;
    }
};

messagingPromise = initializeMessaging();

/**
 * Get the Firebase Messaging instance.
 * Waits for initialization to complete if still pending.
 * @returns Promise that resolves to Messaging instance or null if unsupported
 */
export async function getMessagingInstance(): Promise<Messaging | null> {
    return messagingPromise;
}

export { app };
