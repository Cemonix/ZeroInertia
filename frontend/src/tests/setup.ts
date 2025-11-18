import { beforeAll, afterEach, afterAll, vi } from 'vitest';
import { server } from './mocks/server';

// Mock PrimeVue toast/confirm composables so components using useToast/useConfirm
// (TaskCard, BoardSection, TodayCalendar, etc.) don't throw in tests.
const mockToast = {
    add: vi.fn(),
};

vi.mock('primevue/usetoast', () => ({
    useToast: () => mockToast,
}));

vi.mock('primevue', () => ({
    useToast: () => mockToast,
}));

vi.mock('primevue/useconfirm', () => ({
    useConfirm: () => ({
        require: vi.fn(),
    }),
}));

beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' });
});

afterEach(() => {
    server.resetHandlers();
    vi.clearAllMocks();
});

afterAll(() => {
    server.close();
});

global.matchMedia = global.matchMedia || function () {
    return {
        matches: false,
        media: '',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    };
};

Object.defineProperty(window, 'scrollTo', {
    writable: true,
    value: vi.fn(),
});

// jsdom doesn't implement Element.scrollTo, but vue-cal calls it on a scrollable container.
// Provide a no-op implementation to avoid unhandled errors during tests.
if (!('scrollTo' in HTMLElement.prototype)) {
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
        value: vi.fn(),
        writable: true,
        configurable: true,
    });
}

class MockIntersectionObserver {
    observe = vi.fn();
    disconnect = vi.fn();
    unobserve = vi.fn();
}

Object.defineProperty(window, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: MockIntersectionObserver,
});

Object.defineProperty(global, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: MockIntersectionObserver,
});
