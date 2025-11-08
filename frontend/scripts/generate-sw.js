/**
 * Generate firebase-messaging-sw.js with environment variables
 * This script reads the template and replaces placeholders with actual env vars
 */

import { readFileSync, writeFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import dotenv from "dotenv";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from .env file
const envPath = join(__dirname, "../.env");
dotenv.config({ path: envPath });

// Read package.json to get Firebase version
const packageJsonPath = join(__dirname, "../package.json");
const packageJson = JSON.parse(readFileSync(packageJsonPath, "utf-8"));
const firebaseVersion = packageJson.dependencies.firebase?.replace(/[\^~]/, "") || "12.5.0";

// Read template
const templatePath = join(__dirname, "../public/firebase-messaging-sw.template.js");
let template = readFileSync(templatePath, "utf-8");

// Get environment variables
const replacements = {
    __FIREBASE_VERSION__: firebaseVersion,
    __VITE_FIREBASE_API_KEY__: process.env.VITE_FIREBASE_API_KEY || "",
    __VITE_FIREBASE_AUTH_DOMAIN__: process.env.VITE_FIREBASE_AUTH_DOMAIN || "",
    __VITE_FIREBASE_PROJECT_ID__: process.env.VITE_FIREBASE_PROJECT_ID || "",
    __VITE_FIREBASE_STORAGE_BUCKET__:
        process.env.VITE_FIREBASE_STORAGE_BUCKET || "",
    __VITE_FIREBASE_MESSAGING_SENDER_ID__:
        process.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
    __VITE_FIREBASE_APP_ID__: process.env.VITE_FIREBASE_APP_ID || "",
    __VITE_FIREBASE_MEASUREMENT_ID__:
        process.env.VITE_FIREBASE_MEASUREMENT_ID || "",
};

// Validate that all required env vars are present
const missingVars = Object.entries(replacements)
    .filter(([_, value]) => !value)
    .map(([key]) => key.replace(/__/g, ""));

if (missingVars.length > 0) {
    console.warn(
        "Warning: Missing environment variables:",
        missingVars.join(", ")
    );
    console.warn(
        "The service worker will be generated with empty values for these fields."
    );
}

// Replace placeholders
for (const [placeholder, value] of Object.entries(replacements)) {
    template = template.replace(new RegExp(placeholder, "g"), value);
}

// Write the generated file
const outputPath = join(__dirname, "../public/firebase-messaging-sw.js");
writeFileSync(outputPath, template);

console.log(`✅ Generated firebase-messaging-sw.js (Firebase v${firebaseVersion})`);
