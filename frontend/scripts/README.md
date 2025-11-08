# Build Scripts

## generate-sw.js

Generates `public/firebase-messaging-sw.js` from the template file with environment variables and Firebase version injected.

### How it works

1. Reads `package.json` to automatically detect the installed Firebase version
2. Reads `public/firebase-messaging-sw.template.js` (template with placeholders)
3. Loads environment variables from `.env` using dotenv
4. Replaces all placeholders:
   - `__FIREBASE_VERSION__` with the version from `package.json`
   - `__VITE_FIREBASE_*__` with actual values from `.env`
5. Writes the result to `public/firebase-messaging-sw.js`

### When it runs

- Automatically during `npm run dev` or `npm run build` (via Vite plugin)
- Can be run manually: `node scripts/generate-sw.js`

### Security

- **Template file** (`firebase-messaging-sw.template.js`): Safe to commit, contains only placeholders
- **Generated file** (`firebase-messaging-sw.js`): Contains real credentials, excluded from git via `.gitignore`
- Environment variables are loaded from `.env` which is also excluded from git

### Setup for new developers

1. Copy `.env.example` to `.env`
2. Fill in your Firebase configuration values
3. Run `npm run dev` - the service worker will be generated automatically
