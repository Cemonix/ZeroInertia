# Frontend Integration Testing Guide

This directory contains the integration testing infrastructure for the Zero Inertia frontend application.

## Overview

We use **integration tests** rather than isolated unit tests because they:
- Test the full data flow through the application (components → stores → services → API)
- Catch integration issues between layers
- Provide more confidence that features work end-to-end
- Are more resilient to refactoring (test behavior, not implementation)

## Tech Stack

- **Vitest** - Fast unit test framework with native ESM support
- **@testing-library/vue** - User-centric testing utilities for Vue components
- **MSW (Mock Service Worker)** - Network-level API mocking
- **@pinia/testing** - Pinia store testing utilities

## Project Structure

```
src/tests/
├── README.md                    # This file
├── setup.ts                     # Global test setup and MSW initialization
├── utils/
│   └── test-utils.ts           # Test helpers and rendering utilities
├── mocks/
│   ├── handlers.ts             # MSW request handlers
│   └── server.ts               # MSW server configuration
└── integration/
    ├── task-store.test.ts      # Task management integration tests
    └── auth-store.test.ts      # Authentication integration tests
```

## Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode (during development)
npm run test -- --watch

# Run tests with coverage
npm run coverage

# Run specific test file
npm run test task-store.test.ts
```

## Writing Integration Tests

### 1. Testing Pinia Stores

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTaskStore } from '@/stores/task';

describe('Task Store Integration', () => {
    beforeEach(() => {
        // Create fresh Pinia instance for each test
        setActivePinia(createPinia());
    });

    it('should load tasks from API', async () => {
        const taskStore = useTaskStore();

        await taskStore.loadTasksForProject('project-1');

        expect(taskStore.tasks).toHaveLength(2);
        expect(taskStore.loading).toBe(false);
    });
});
```

### 2. Testing Vue Components

```typescript
import { renderWithProviders } from '@/tests/utils/test-utils';
import { screen } from '@testing-library/vue';
import TaskCard from '@/components/tasks/TaskCard.vue';

it('should display task information', async () => {
    const { getByText } = renderWithProviders(TaskCard, {
        props: {
            task: { id: '1', title: 'Test Task', ... }
        }
    });

    expect(getByText('Test Task')).toBeInTheDocument();
});
```

### 3. Adding New API Mocks

When you need to mock a new API endpoint, add it to `mocks/handlers.ts`:

```typescript
export const handlers = [
    // ... existing handlers

    http.get(`${API_BASE_URL}/api/v1/your-endpoint`, () => {
        return HttpResponse.json({
            // your mock response
        });
    }),
];
```

## Test Utilities

### `renderWithProviders()`

Renders Vue components with all necessary providers (Pinia, Router, PrimeVue):

```typescript
const { getByText, router, pinia } = renderWithProviders(MyComponent, {
    props: { /* component props */ },
    initialRoute: '/tasks',
    piniaOptions: {
        initialState: {
            task: { tasks: [] }
        }
    }
});
```

### `waitForRouter()`

Waits for Vue Router to be ready:

```typescript
await waitForRouter(router);
```

### `flushPromises()`

Flushes all pending promises (useful for async operations):

```typescript
await flushPromises();
```

## Mock Data

Mock data is managed through factory functions in `mocks/handlers.ts` to ensure test isolation:

```typescript
import { resetMockTasks, createMockTasks } from '../mocks/handlers';

beforeEach(() => {
    // Reset mock data to initial state
    resetMockTasks();
});

// Or create custom test data
const customTasks = createMockTasks();
```

**Why factory functions?** Directly mutating shared mock arrays can cause test pollution where one test's changes affect another. Factory functions return fresh copies, ensuring true test isolation.

## MSW (Mock Service Worker)

MSW intercepts HTTP requests at the network level, providing realistic API mocking:

### How It Works

1. **Setup** (`setup.ts`) - MSW server starts before all tests
2. **Handlers** (`mocks/handlers.ts`) - Define API responses
3. **Intercept** - All axios/fetch requests are intercepted
4. **Reset** - Handlers reset after each test

### Benefits

- Tests actual HTTP request flow
- No need to mock axios or service modules
- Works with CSRF tokens, interceptors, and error handlers
- Easy to simulate different API scenarios (success, error, loading)

### Simulating Errors

```typescript
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

it('should handle API errors', async () => {
    // Override handler for this test only
    server.use(
        http.get('/api/v1/tasks', () => {
            return HttpResponse.json(
                { detail: 'Server error' },
                { status: 500 }
            );
        })
    );

    const taskStore = useTaskStore();
    await taskStore.loadTasksForProject('project-1');

    expect(taskStore.error).toBeTruthy();
});
```

## Best Practices

### ✅ DO

- **Test user-facing behavior**, not implementation details
- **Use descriptive test names** that explain what should happen
- **Reset state** between tests using `beforeEach`
- **Test error cases** and loading states
- **Keep tests focused** - one concept per test
- **Use real API responses** in mocks (match backend schema)

### ❌ DON'T

- Don't mock Pinia stores directly - test them through integration
- Don't use `vi.mock()` for services - use MSW instead
- Don't test private/internal methods - test public API
- Don't share state between tests
- Don't make tests depend on each other

## Common Patterns

### Testing Async Store Actions

```typescript
it('should handle async operations', async () => {
    const store = useTaskStore();

    // Check loading state
    const promise = store.loadTasksForProject('project-1');
    expect(store.loading).toBe(true);

    await promise;

    expect(store.loading).toBe(false);
    expect(store.tasks).toHaveLength(2);
});
```

### Testing Computed Properties

```typescript
it('should filter tasks by section', async () => {
    const store = useTaskStore();
    await store.loadTasksForProject('project-1');

    const sectionTasks = store.getTasksBySection('section-1');

    expect(sectionTasks).toHaveLength(2);
});
```

### Testing User Interactions

```typescript
import { fireEvent } from '@testing-library/vue';

it('should toggle task completion on click', async () => {
    const { getByRole } = renderWithProviders(TaskCard, {
        props: { task: mockTask }
    });

    const checkbox = getByRole('checkbox');
    await fireEvent.click(checkbox);

    expect(taskStore.tasks[0].completed).toBe(true);
});
```

## Debugging Tests

### Verbose Output

```bash
npm run test -- --reporter=verbose
```

### Debug Single Test

```typescript
it.only('should do something', async () => {
    // Only this test will run
});
```

### Inspect Component Output

```typescript
const { debug } = renderWithProviders(MyComponent);
debug(); // Prints current DOM to console
```

### MSW Logging

MSW warns about unhandled requests. Add missing handlers to `mocks/handlers.ts`:

```
[MSW] Warning: intercepted a request without a matching request handler:
  • GET http://localhost:8000/api/v1/new-endpoint
```

## Coverage

View coverage reports:

```bash
npm run coverage
```

Coverage reports are generated in `coverage/` directory. Open `coverage/index.html` in your browser.

### Coverage Goals

- **Stores**: Aim for 80%+ coverage
- **Components**: Aim for 70%+ coverage (focus on critical user paths)
- **Services**: Covered through store integration tests

## Adding New Tests

1. Create test file in `src/tests/integration/`
2. Import utilities: `import { describe, it, expect, beforeEach } from 'vitest'`
3. Add mock data to `mocks/handlers.ts` if needed
4. Write tests using `renderWithProviders` or store testing pattern
5. Run tests: `npm run test`

## Example: Complete Integration Test

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTaskStore } from '@/stores/task';
import { resetMockTasks } from '../mocks/handlers';

describe('Task Management Integration', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        resetMockTasks();
    });

    it('should load, update, and delete tasks', async () => {
        const taskStore = useTaskStore();

        // Load tasks
        await taskStore.loadTasksForProject('project-1');
        expect(taskStore.tasks).toHaveLength(2);

        // Update task
        await taskStore.updateTask('task-1', { title: 'Updated' });
        expect(taskStore.tasks[0].title).toBe('Updated');

        // Delete task
        await taskStore.deleteTask('task-1');
        expect(taskStore.tasks).toHaveLength(1);
    });
});
```

## Next Steps

- Add component integration tests for critical UI flows
- Test complex user interactions (drag & drop, modals)
- Add E2E tests with Playwright for full application flows
- Set up CI/CD to run tests automatically

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library Vue](https://testing-library.com/docs/vue-testing-library/intro)
- [MSW Documentation](https://mswjs.io/)
- [Pinia Testing Guide](https://pinia.vuejs.org/cookbook/testing.html)
