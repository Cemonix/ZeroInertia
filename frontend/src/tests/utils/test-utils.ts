import { render } from '@testing-library/vue';
import type { RenderOptions } from '@testing-library/vue';
import { createPinia, setActivePinia } from 'pinia';
import { createRouter, createMemoryHistory } from 'vue-router';
import type { Router } from 'vue-router';
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';
import type { Component } from 'vue';

interface CustomRenderOptions extends Partial<RenderOptions<Component>> {
    initialRoute?: string;
    piniaOptions?: {
        stubActions?: boolean;
        initialState?: Record<string, any>;
    };
}

export function createTestRouter(initialRoute = '/'): Router {
    const router = createRouter({
        history: createMemoryHistory(),
        routes: [
            { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
            { path: '/tasks', name: 'tasks', component: { template: '<div>Tasks</div>' } },
            { path: '/projects', name: 'projects', component: { template: '<div>Projects</div>' } },
            { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
        ],
    });

    router.push(initialRoute);
    return router;
}

export function renderWithProviders(
    component: Component,
    options: CustomRenderOptions = {}
) {
    const { initialRoute = '/', piniaOptions = {}, ...renderOptions } = options;

    const pinia = createPinia();
    setActivePinia(pinia);

    if (piniaOptions.initialState) {
        Object.entries(piniaOptions.initialState).forEach(([storeName, state]) => {
            pinia.state.value[storeName] = state;
        });
    }

    const router = createTestRouter(initialRoute);

    return {
        ...render(component, {
            global: {
                plugins: [
                    pinia,
                    router,
                    [PrimeVue, { theme: { preset: Aura } }] as any,
                ],
                ...renderOptions.global,
            },
            ...renderOptions,
        }),
        router,
        pinia,
    };
}

export async function waitForRouter(router: Router) {
    await router.isReady();
}

export function flushPromises() {
    return new Promise(resolve => setImmediate(resolve));
}
