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

const shortcuts: ShortcutAction[] = [];

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
    // Skip if user is typing in an input field
    if (isInputField(event.target)) return;

    for (const shortcut of shortcuts) {
        if (matchesShortcut(event, shortcut)) {
            event.preventDefault();
            shortcut.handler(event);
            break;
        }
    }
}

export function useKeyboardShortcuts() {
    function register(shortcut: ShortcutAction) {
        shortcuts.push(shortcut);
    }

    function unregister(key: string) {
        const index = shortcuts.findIndex(s => s.key === key);
        if (index !== -1) {
            shortcuts.splice(index, 1);
        }
    }

    onMounted(() => {
        window.addEventListener('keydown', handleGlobalKeyDown);
    });

    onUnmounted(() => {
        window.removeEventListener('keydown', handleGlobalKeyDown);
    });

    return {
        register,
        unregister,
    };
}
