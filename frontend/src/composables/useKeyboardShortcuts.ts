import { onMounted, onUnmounted } from 'vue';

export interface ShortcutAction {
    key: string;
    ctrl?: boolean;
    meta?: boolean;
    alt?: boolean;
    shift?: boolean;
    handler: (event: KeyboardEvent) => void;
    description?: string;
}

const globalShortcuts: ShortcutAction[] = [];
let listenerCount = 0;

function isInputField(target: EventTarget | null): boolean {
    if (!target) return false;
    const element = target as HTMLElement;
    return (
        element.tagName === 'INPUT' ||
        element.tagName === 'TEXTAREA' ||
        element.isContentEditable
    );
}

function matchesShortcut(event: KeyboardEvent, shortcut: ShortcutAction): boolean {
    if (event.key.toLowerCase() !== shortcut.key.toLowerCase()) return false;

    // If both ctrl and meta are specified, allow either (cross-platform support)
    if (shortcut.ctrl && shortcut.meta) {
        if (!event.ctrlKey && !event.metaKey) return false;
    } else {
        if (shortcut.ctrl && !event.ctrlKey) return false;
        if (shortcut.meta && !event.metaKey) return false;
    }

    if (shortcut.alt && !event.altKey) return false;
    if (shortcut.shift && !event.shiftKey) return false;
    return true;
}

function handleGlobalKeyDown(event: KeyboardEvent) {
    if (isInputField(event.target)) return;

    for (const shortcut of globalShortcuts) {
        if (matchesShortcut(event, shortcut)) {
            event.preventDefault();
            shortcut.handler(event);
            break;
        }
    }
}

export function useKeyboardShortcuts() {
    const localShortcuts: ShortcutAction[] = [];

    function register(shortcut: ShortcutAction) {
        globalShortcuts.push(shortcut);
        localShortcuts.push(shortcut);
    }

    function unregister(key: string) {
        const index = globalShortcuts.findIndex(s => s.key === key);
        if (index !== -1) {
            globalShortcuts.splice(index, 1);
        }
        const localIndex = localShortcuts.findIndex(s => s.key === key);
        if (localIndex !== -1) {
            localShortcuts.splice(localIndex, 1);
        }
    }

    onMounted(() => {
        if (listenerCount === 0) {
            window.addEventListener('keydown', handleGlobalKeyDown);
        }
        listenerCount++;
    });

    onUnmounted(() => {
        for (const shortcut of localShortcuts) {
            const index = globalShortcuts.findIndex(s => s === shortcut);
            if (index !== -1) {
                globalShortcuts.splice(index, 1);
            }
        }

        listenerCount--;
        if (listenerCount === 0) {
            window.removeEventListener('keydown', handleGlobalKeyDown);
        }
    });

    return {
        register,
        unregister,
    };
}
