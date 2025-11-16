import { http, HttpResponse } from 'msw';
import type { Task } from '@/models/task';
import type { Project } from '@/models/project';
import type { Section } from '@/models/section';
import { env } from '@/config/env';

const API_BASE_URL = env.API_BASE_URL || 'http://localhost:8000';

function isLoginBody(body: unknown): body is { email: string; password: string } {
    return (
        typeof body === 'object' &&
        body !== null &&
        'email' in body &&
        'password' in body &&
        typeof body.email === 'string' &&
        typeof body.password === 'string'
    );
}

function isTaskBody(body: unknown): body is Partial<Task> {
    return typeof body === 'object' && body !== null;
}

export const createMockTasks = (): Task[] => [
    {
        id: 'task-1',
        title: 'Test Task 1',
        description: 'Description for test task 1',
        completed: false,
        archived: false,
        snooze_count: 0,
        project_id: 'project-1',
        section_id: 'section-1',
        order_index: 0,
        priority_id: 'priority-medium',
        due_datetime: null,
        duration_minutes: null,
        reminder_minutes: null,
        recurrence_interval: null,
        recurrence_unit: null,
        recurrence_days: null,
        labels: [],
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        archived_at: null,
    },
    {
        id: 'task-2',
        title: 'Test Task 2',
        description: 'Description for test task 2',
        completed: true,
        archived: false,
        snooze_count: 0,
        project_id: 'project-1',
        section_id: 'section-1',
        order_index: 1,
        priority_id: 'priority-high',
        due_datetime: '2025-12-31T12:00:00Z',
        duration_minutes: 60,
        reminder_minutes: 15,
        recurrence_interval: null,
        recurrence_unit: null,
        recurrence_days: null,
        labels: [],
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        archived_at: null,
    },
];

export const createMockProjects = (): Project[] => [
    {
        id: 'project-1',
        parent_id: null,
        title: 'Test Project',
        order_index: 0,
        is_inbox: false,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
    },
];

export const createMockSections = (): Section[] => [
    {
        id: 'section-1',
        title: 'To Do',
        project_id: 'project-1',
        order_index: 0,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
    },
    {
        id: 'section-2',
        title: 'In Progress',
        project_id: 'project-1',
        order_index: 1,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
    },
];

let mockTasks = createMockTasks();
const mockProjects = createMockProjects();
const mockSections = createMockSections();

export const resetMockTasks = () => {
    mockTasks = createMockTasks();
};

export const getMockTasks = () => mockTasks;

export const handlers = [
    http.get(`${API_BASE_URL}/csrf`, () => {
        return HttpResponse.json({ csrf_token: 'mock-csrf-token' });
    }),

    http.get(`${API_BASE_URL}/api/v1/csrf-token`, () => {
        return HttpResponse.json({ csrf_token: 'mock-csrf-token' });
    }),

    http.get(`${API_BASE_URL}/api/v1/auth/is_authenticated`, () => {
        return HttpResponse.json({ is_authenticated: false });
    }),

    http.post(`${API_BASE_URL}/api/v1/auth/login`, async ({ request }) => {
        const body = await request.json();

        if (!isLoginBody(body)) {
            return HttpResponse.json(
                { detail: 'Invalid request body' },
                { status: 400 }
            );
        }

        if (body.email === 'test@example.com' && body.password === 'password123') {
            return HttpResponse.json({
                access_token: 'mock-access-token',
                token_type: 'bearer',
                user: {
                    id: 'user-1',
                    email: 'test@example.com',
                    username: 'testuser',
                },
            });
        }

        return HttpResponse.json(
            { detail: 'Invalid credentials' },
            { status: 401 }
        );
    }),

    http.post(`${API_BASE_URL}/api/v1/auth/logout`, () => {
        return HttpResponse.json({ message: 'Logged out successfully' });
    }),

    http.get(`${API_BASE_URL}/api/v1/auth/me`, () => {
        return HttpResponse.json({
            id: 'user-1',
            email: 'test@example.com',
            username: 'testuser',
        });
    }),

    http.get(`${API_BASE_URL}/api/v1/tasks`, ({ request }) => {
        const url = new URL(request.url);
        const projectId = url.searchParams.get('project_id');

        let filteredTasks = [...mockTasks];
        if (projectId) {
            filteredTasks = filteredTasks.filter(t => t.project_id === projectId);
        }

        return HttpResponse.json({
            items: filteredTasks,
            total: filteredTasks.length,
            page: 1,
            page_size: 500,
            pages: 1,
        });
    }),

    http.get(`${API_BASE_URL}/api/v1/tasks/:id`, ({ params }) => {
        const task = mockTasks.find(t => t.id === params.id);
        if (!task) {
            return HttpResponse.json(
                { detail: 'Task not found' },
                { status: 404 }
            );
        }
        return HttpResponse.json(task);
    }),

    http.post(`${API_BASE_URL}/api/v1/tasks`, async ({ request }) => {
        const body = await request.json();

        if (!isTaskBody(body)) {
            return HttpResponse.json(
                { detail: 'Invalid request body' },
                { status: 400 }
            );
        }

        const newTask: Task = {
            id: `task-${Date.now()}`,
            title: body.title || 'New Task',
            description: body.description || null,
            completed: false,
            archived: false,
            snooze_count: 0,
            project_id: body.project_id || 'project-1',
            section_id: body.section_id || 'section-1',
            order_index: mockTasks.length,
            priority_id: body.priority_id || null,
            due_datetime: body.due_datetime || null,
            duration_minutes: body.duration_minutes || null,
            reminder_minutes: body.reminder_minutes || null,
            recurrence_interval: null,
            recurrence_unit: null,
            recurrence_days: null,
            labels: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            archived_at: null,
        };
        mockTasks.push(newTask);
        return HttpResponse.json(newTask, { status: 201 });
    }),

    http.patch(`${API_BASE_URL}/api/v1/tasks/:id`, async ({ params, request }) => {
        const taskIndex = mockTasks.findIndex(t => t.id === params.id);
        if (taskIndex === -1) {
            return HttpResponse.json(
                { detail: 'Task not found' },
                { status: 404 }
            );
        }

        const body = await request.json();

        if (!isTaskBody(body)) {
            return HttpResponse.json(
                { detail: 'Invalid request body' },
                { status: 400 }
            );
        }

        mockTasks[taskIndex] = {
            ...mockTasks[taskIndex],
            ...body,
            updated_at: new Date().toISOString(),
        };

        return HttpResponse.json(mockTasks[taskIndex]);
    }),

    http.delete(`${API_BASE_URL}/api/v1/tasks/:id`, ({ params }) => {
        const taskIndex = mockTasks.findIndex(t => t.id === params.id);
        if (taskIndex === -1) {
            return HttpResponse.json(
                { detail: 'Task not found' },
                { status: 404 }
            );
        }

        mockTasks.splice(taskIndex, 1);
        return HttpResponse.json(null, { status: 204 });
    }),

    http.get(`${API_BASE_URL}/api/v1/projects`, () => {
        return HttpResponse.json(mockProjects);
    }),

    http.get(`${API_BASE_URL}/api/v1/projects/:id`, ({ params }) => {
        const project = mockProjects.find(p => p.id === params.id);
        if (!project) {
            return HttpResponse.json(
                { detail: 'Project not found' },
                { status: 404 }
            );
        }
        return HttpResponse.json(project);
    }),

    http.get(`${API_BASE_URL}/api/v1/sections`, ({ request }) => {
        const url = new URL(request.url);
        const projectId = url.searchParams.get('project_id');

        let filteredSections = [...mockSections];
        if (projectId) {
            filteredSections = filteredSections.filter(s => s.project_id === projectId);
        }

        return HttpResponse.json(filteredSections);
    }),
];
