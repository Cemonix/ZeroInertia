# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

## Project Overview

"Zero Inertia" is a personal productivity ecosystem - a "second brain" application that combines task management, achievement logging, knowledge management, progress visualization, and AI-powered motivation. The goal is to create a unified system for managing both tasks and personal growth.

**Tech Stack:**

**Backend:**
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLAlchemy 2.0 (async mode)
- **Migrations**: Alembic
- **Authentication**: OAuth 2.0 (Google) + JWT tokens
- **Validation**: Pydantic v2
- **Testing**: Pytest with httpx AsyncClient
- **Code Quality**: Ruff (linting), MyPy (type checking), Black (formatting)
- **Key Libraries**: python-jose (JWT), authlib (OAuth), python-multipart, pytz

**Frontend:**
- **Framework**: Vue.js 3 with Composition API (`<script setup>`)
- **Build Tool**: Vite
- **Language**: TypeScript
- **State Management**: Pinia
- **UI Components**: PrimeVue, PrimeIcons
- **Calendar**: vue-cal
- **HTTP Client**: Axios
- **Charts**: D3.js (custom visualizations)
- **Testing**: Vitest, Vue Test Utils, Testing Library, MSW (Mock Service Worker)
- **Router**: Vue Router
- **Date Handling**: date-fns (lightweight alternative to moment.js)

## Modules

### 1. Task Management ✅ (Complete)
**Status:** Production-ready with comprehensive features
**Key Files:**
- Backend: [task.py](backend/app/api/v1/task.py), [task_service.py](backend/app/services/task_service.py), [task.py](backend/app/models/task.py)
- Frontend: [task.ts](frontend/src/stores/task.ts), [TaskModal.vue](frontend/src/components/tasks/TaskModal.vue), [TaskCard.vue](frontend/src/components/tasks/TaskCard.vue)

**Features:**
- Create, edit, complete, archive, and delete tasks
- Task descriptions with rich text support
- Due dates with date-time picker
- Priority levels (low, medium, high)
- Task labels for categorization
- Recurring tasks with flexible patterns (daily, weekly, monthly, yearly)
- Task reordering with drag-and-drop
- Date-based task loading for efficient calendar views
- Checklist items within tasks
- Notifications for task updates

**Technical Highlights:**
- Server-side filtering by date range (`/api/v1/tasks/by-date`)
- Optimistic UI updates with rollback on error
- Task archiving instead of hard deletes
- Integration with vue-cal for calendar view

### 2. Projects & Sections ✅ (Complete)
**Key Files:**
- Backend: [project.py](backend/app/api/v1/project.py), [section.py](backend/app/api/v1/section.py)
- Frontend: [project.ts](frontend/src/stores/project.ts), [ProjectTree.vue](frontend/src/components/sidebar/ProjectTree.vue), [ProjectBoard.vue](frontend/src/components/board/ProjectBoard.vue)

**Features:**
- Hierarchical organization: Projects → Sections → Tasks
- Project CRUD operations with color coding
- Section management within projects
- Kanban board view for project tasks
- Drag-and-drop task reordering within sections
- Project tree navigation in sidebar
- Default inbox project for unorganized tasks

### 3. Knowledge Hub (Notes) ✅ (Complete)
**Purpose:** Note-taking and knowledge management (Obsidian-like)
**Key Files:**
- Backend: [note.py](backend/app/api/v1/note.py), [note_service.py](backend/app/services/note_service.py)
- Frontend: [note.ts](frontend/src/stores/note.ts), note components in [frontend/src/components/notes/](frontend/src/components/notes/)

**Features:**
- Create/edit markdown notes with rich editor
- Organize notes in hierarchical folders
- Search notes by title and content
- Markdown rendering with syntax highlighting
- Note versioning and history
- Tags for note categorization

### 4. Labels ✅ (Complete)
**Key Files:**
- Backend: [label.py](backend/app/api/v1/label.py)
- Frontend: [label.ts](frontend/src/stores/label.ts)

**Features:**
- Color-coded labels for task categorization
- Assign multiple labels to tasks
- Label management (create, edit, delete)
- Filter tasks by label

### 5. Checklists ✅ (Complete)
**Key Files:**
- Backend: [checklist.py](backend/app/api/v1/checklist.py), [checklist_service.py](backend/app/services/checklist_service.py)
- Frontend: [checklist.ts](frontend/src/stores/checklist.ts)

**Features:**
- Multiple checklists per task
- Checklist items with completion tracking
- Progress calculation (% complete)
- Reorder checklists and items with drag-and-drop
- Bulk operations on checklist items

### 6. Progress Tracker (Streaks) 🔥 ✅ (Complete)
**Purpose:** Maintain motivation through streak tracking and statistics
**Key Files:**
- Backend: [streak.py](backend/app/api/v1/streak.py), [statistics.py](backend/app/api/v1/statistics.py)
- Frontend: [TodayCalendar.vue](frontend/src/components/today/TodayCalendar.vue)

**Features:**
- Daily task completion tracking
- Streak counter (consecutive days with completed tasks)
- Calendar heatmap visualization (GitHub-style)
- Weekly/monthly completion statistics
- Total tasks completed counter
- Today view with integrated calendar

### 7. Media Tracker 📚🎮 ✅ (Complete)
**Purpose:** Track achievements and completed media (books, games, movies, shows)
**Key Files:**
- Backend: [media.py](backend/app/api/v1/media.py), [media_service.py](backend/app/services/media_service.py)
- Frontend: [media.ts](frontend/src/stores/media.ts)

**Features:**
- Add media items (book, game, movie, TV show, podcast, course)
- Track status: planned / in-progress / completed
- Completion date tracking
- Rating system (1-5 stars)
- Notes and reviews for each item
- Filter by media type and status
- Statistics: total completed, by type, average ratings

### 8. Authentication & User Management 🔐 ✅ (Complete)
**Key Files:**
- Backend: [auth.py](backend/app/api/v1/auth.py), [jwt_service.py](backend/app/services/jwt_service.py)
- Frontend: [auth.ts](frontend/src/stores/auth.ts)

**Features:**
- OAuth 2.0 authentication (Google provider)
- JWT token-based session management
- Secure cookie storage for tokens
- Token refresh mechanism
- User profile management
- Protected API endpoints with dependency injection

### 9. AI Integration 🤖 (Not Implemented)
**Purpose:** Provide intelligent insights, motivation and task management assistance

**Planned Features:**
- Task completion summaries
- AI task categorization
- Smart task suggestions based on history
- TTS (Text-to-Speech) motivational feedback
- Day planning based on history and tasks
- Pattern detection in productivity

## Architecture

The project follows a monorepo structure with separate `backend/` and `frontend/` directories.

### Backend Architecture (Clean Architecture Pattern)
```
backend/app/
├── api/v1/              # API routes (thin controllers)
├── core/                # Core configuration, database, settings
├── models/              # SQLAlchemy ORM models (domain entities)
├── schemas/             # Pydantic schemas (DTOs)
├── services/            # Business logic layer
├── middleware/          # Custom middleware
└── tests/               # Integration & unit tests
```

**Key Patterns:**
- **Clean Architecture**: Separation of concerns with API → Service → Repository layers
- **Dependency Injection**: Database sessions and current user injected via FastAPI dependencies
- **Async/Await**: All database operations use async SQLAlchemy 2.0
- **Service Layer**: Business logic isolated in service modules for testability
- **Repository Pattern**: Database operations encapsulated in service functions

**Database:**
- PostgreSQL with 29 Alembic migrations tracking schema evolution
- UUID primary keys for better distributed system support
- Soft deletes (archived flag) for user data retention
- Timezone-aware datetime fields for proper date handling
- Relationship loading with `selectinload()` to prevent N+1 queries

### Frontend Architecture (Composition API + Service Layer)
```
frontend/src/
├── components/          # Vue components organized by feature
│   ├── board/          # Kanban board components
│   ├── layout/         # App shell, navigation, sidebar
│   ├── pickers/        # Date/time, recurrence pickers
│   ├── sidebar/        # Project tree navigation
│   ├── tasks/          # Task modal, card, list
│   └── today/          # Today view with calendar
├── router/             # Vue Router configuration
├── services/           # API client layer (axios)
├── stores/             # Pinia state management
├── tests/              # Integration tests with Vitest & MSW
└── types/              # TypeScript type definitions
```

**Key Patterns:**
- **Composition API**: All components use `<script setup>` syntax
- **Service Layer**: API calls abstracted into service modules (taskService.ts, etc.)
- **State Management**: Pinia stores for global state with computed getters
- **Optimistic Updates**: UI updates immediately, rollback on API error
- **Component Composition**: Small, focused components with clear responsibilities

**UI Framework:**
- PrimeVue for consistent component library
- Vue-cal for calendar visualization
- Custom D3.js integration for statistics charts
- Responsive design with mobile support

### Testing Infrastructure

**Backend Testing:**
- **Framework**: Pytest with async support
- **Database**: Separate test database with per-test isolation
- **Fixtures**: [conftest.py](backend/app/tests/conftest.py) provides reusable fixtures:
  - `test_engine`: Async SQLAlchemy engine with NullPool
  - `db_session`: Fresh database session per test
  - `test_user`: Authenticated user with OAuth credentials
  - `authenticated_client`: HTTP client with JWT cookie
  - `test_project`, `test_section`, `test_task`: Pre-created test data
- **Coverage**: 80+ integration tests across all API endpoints
- **Commands**: `poetry run pytest` and `poetry run pytest --cov=app`

**Frontend Testing:**
- **Framework**: Vitest with Vue Test Utils and Testing Library
- **API Mocking**: MSW (Mock Service Worker) with handlers in [handlers.ts](frontend/src/tests/mocks/handlers.ts)
- **Store Testing**: Pinia store integration tests with real API mocks
- **Isolation**: `resetMockTasks()` / `resetMockChecklists()` factory functions
- **Coverage**: Integration tests for task loading, checklist operations, date filtering
- **Commands**: `npm run test` and `npm run test:coverage`

### Deployment & Infrastructure
- **Docker Compose**: Production setup with Nginx reverse proxy
- **Environment**: `.env` files for configuration (separate for dev/prod)
- **Database Migrations**: Alembic for versioned schema changes
- **Static Assets**: Vite builds optimized production bundles

## Notable Implementation Details

### Recurring Tasks System
The recurrence system supports complex patterns:
- **Frequencies**: daily, weekly, monthly, yearly
- **Intervals**: Every N days/weeks/months
- **Weekly**: Select specific days of week (Monday, Wednesday, Friday)
- **Monthly**: By day of month (15th) or relative day (second Tuesday)
- **End conditions**: Never, after N occurrences, or until specific date
- **Implementation**: [recurrence.py](backend/app/models/recurrence.py) model with JSON serialization

### Date-Based Task Loading
Efficient calendar view with server-side filtering:
- **Endpoint**: `GET /api/v1/tasks/by-date?date_from=...&date_to=...`
- **Features**: Inclusive start, exclusive end, includes tasks without dates
- **Frontend**: Automatic loading on date navigation, duplicate prevention
- **Files**: [task_service.py:183-217](backend/app/services/task_service.py), [TodayCalendar.vue:165-199](frontend/src/components/today/TodayCalendar.vue)

### OAuth Authentication Flow
1. User clicks "Login with Google"
2. Redirects to Google OAuth consent screen
3. Google redirects back with authorization code
4. Backend exchanges code for user info
5. Creates/finds user in database
6. Issues JWT access token stored in HTTP-only cookie
7. Frontend receives user profile and stores in Pinia
8. **Files**: [auth.py](backend/app/api/v1/auth.py), [oauth_service.py](backend/app/services/oauth_service.py)

### Pinia Store Pattern
All stores follow consistent pattern:
- **State**: Reactive refs for data arrays and loading/error states
- **Computed Getters**: Functions that derive data (not `.value` refs)
- **Actions**: Async functions for API calls with error handling
- **Example**: `store.getChecklistsByTask(taskId)` - call as function, not `.value`

### Calendar Integration (vue-cal)
- **Component**: [TodayCalendar.vue](frontend/src/components/today/TodayCalendar.vue)
- **Features**: Task visualization by date, drag-and-drop rescheduling
- **Event Handling**: `@view-change` event with payload normalization
- **Performance**: Loads only visible date range, caches loaded dates

### Notifications System
- Toast notifications using PrimeVue Toast component
- Success/error feedback for all CRUD operations
- Auto-dismiss after 3 seconds
- Positioned top-right for non-intrusive UX

## Development Environment

### Local Development Setup
For optimal development experience with hot reload and fast iteration:

**Backend (FastAPI):**
- Python 3.13+ with Poetry for dependency management
- Local PostgreSQL installation or lightweight SQLite for development
- Run FastAPI with `uvicorn --reload` for auto-restart on changes
- Use environment variables for configuration

**Frontend (Vue.js):**
- Node.js 22+ with npm/pnpm
- Vite dev server with HMR (Hot Module Replacement)
- Proxy API calls to backend during development

**Database Options:**
- PostgreSQL (Docker compose)

### Development Commands

**Backend:**
```bash
# Setup environment
poetry install
poetry shell

# Run development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"

# Testing
poetry run pytest
poetry run pytest --cov=app

# Linting and formatting
poetry run ruff check
poetry run ruff format
poetry run mypy app
```

**Frontend:**
```bash
# Setup
npm install

# Development server
npm run dev

# Build
npm run build

# Testing
npm run test
npm run test:coverage

# Linting and type checking
npm run lint
npm run lint:fix
npm run type-check
```


### Docker Usage
Docker Compose reserved for:
- Production deployments
- CI/CD pipelines
- Team members who prefer containerized development

When implementing, follow the technology stack specified in the project plan and maintain the separation between backend API and frontend SPA.

## Backend Development Conventions

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── tests/
├── alembic/                 # Database migrations
├── pyproject.toml           # Poetry configuration
├── poetry.lock              # Poetry lock file
└── Dockerfile
```

### Code Conventions
- Use async/await for all database operations and external API calls
- Follow PEP 8 style guidelines with line length of 100 characters
- Use type hints for all function parameters and return values
- Separate business logic into service modules, keep API endpoints thin
- Use Pydantic models for request/response validation
- Implement proper error handling with custom exception classes
- Use dependency injection for database sessions and authentication
- Never create markdown file describing your last updates
- Do not write comments that describes your intentions. Comments should describe the code!

### Database
- Use SQLAlchemy 2.0 with async syntax (`select()`, `async with`)
- Define relationships using `relationship()` with lazy loading considerations
- Create Alembic migrations for all schema changes
- Use UUIDs for primary keys where appropriate
- Implement soft deletes for user data retention

### API Design
- Follow RESTful conventions with proper HTTP status codes
- Use `/api/v1/` prefix for all endpoints
- Implement pagination for list endpoints using `skip` and `limit`
- Return consistent JSON response format with data/error structure
- Use JWT tokens for authentication with proper expiration
- Implement rate limiting on sensitive endpoints

## Frontend Development Conventions

### Project Structure
```
frontend/
├── src/
│   ├── main.js              # App entry point
│   ├── App.vue              # Root component
│   ├── router/
│   ├── stores/
│   ├── views/
│   ├── components/
│   │   ├── layout/
│   │   ├── tasks/
│   │   └── charts/
│   ├── composables/
│   ├── services/
│   └── utils/
├── public/
├── package.json
├── vite.config.js
└── Dockerfile
```

### Code Conventions
- Use Composition API with `<script setup>` syntax for all components
- Follow Vue 3 style guide and best practices
- Use TypeScript for type safety
- Implement proper prop validation and emit definitions
- Use PrimeVue components consistently for UI elements

### State Management
- Use Pinia stores for global state management
- Keep component-specific state local using `ref()` and `reactive()`
- Implement proper error handling in store actions
- Use computed properties for derived state
- Persist authentication state to localStorage

## Code Quality & Best Practices

### Backend Code Quality
**Linting & Formatting:**
- Ruff for fast Python linting (configured in `pyproject.toml`)
- 100-character line length limit
- Automatic import sorting
- Command: `poetry run ruff check` and `poetry run ruff format`

**Type Safety:**
- MyPy for static type checking
- Type hints required for all function signatures
- Strict mode enabled for better type coverage
- Command: `poetry run mypy app`

**Testing Standards:**
- Minimum 80% code coverage target
- Integration tests for all API endpoints
- Fixture-based test data isolation
- Async test support with pytest-asyncio

### Frontend Code Quality
**Linting & Formatting:**
- ESLint with Vue-specific rules
- TypeScript strict mode enabled
- Consistent code style with Prettier integration
- Commands: `npm run lint` and `npm run lint:fix`

**Type Safety:**
- TypeScript with strict type checking
- Explicit types for props, emits, and function signatures
- Type definitions in `/src/types/` directory
- Command: `npm run type-check`

**Component Standards:**
- Use `<script setup lang="ts">` for all components
- PropType validation with TypeScript interfaces
- Explicit `defineEmits()` and `defineProps()`
- Avoid deeply nested components (max 3 levels)
- Prefer composition over complex component hierarchies

**Testing Standards:**
- Integration tests for Pinia stores
- MSW for API mocking (no real HTTP calls in tests)
- Factory functions for test data isolation
- Coverage reports with `npm run test:coverage`

### Git Practices
- Feature branches with descriptive names
- Meaningful commit messages
- Database migrations committed with related code changes
- No sensitive data in repository (.env files gitignored)

### Performance Considerations
**Backend:**
- Use `selectinload()` to prevent N+1 query problems
- Database connection pooling (NullPool for tests)
- Async endpoints for all I/O operations
- Query optimization with proper indexes

**Frontend:**
- Lazy loading for route components
- Computed properties for expensive calculations
- Date-range loading instead of fetching all data
- Optimistic UI updates for better perceived performance
- Vite code splitting for smaller bundle sizes