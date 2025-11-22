# Zero Inertia

**A personal productivity ecosystem designed to be your second brain.**

Zero Inertia is built on a simple philosophy: staying in motion is easier than starting from rest. By combining task management, knowledge organization, progress visualization, and achievement tracking into one unified system, it helps you maintain momentum in both your daily tasks and long-term personal growth.

Whether you're planning your day, organizing knowledge in markdown notes, tracking your reading and gaming achievements, or visualizing your productivity streaks, Zero Inertia keeps everything connected and accessible. No more context switching between different apps or losing track of what matters.

## What You Can Do

**Manage Your Work**
Create tasks with rich descriptions, organize them into projects and sections, set priorities and due dates, and build checklists. Recurring tasks handle your routines automatically, while the Kanban board gives you a visual overview of everything in progress.

**Build Your Knowledge Base**
Write markdown notes with full syntax highlighting, organize them in hierarchical folders, and search across everything instantly. Whether it's meeting notes, research, or personal journals, your knowledge stays structured and findable.

**Track Your Progress**
See your productivity streaks on a GitHub-style calendar heatmap. Watch your daily completion stats grow and use visual feedback to maintain motivation. The system celebrates consistency, not perfection.

**Log Your Achievements**
Keep a record of every book you've read, game you've completed, show you've watched, or course you've finished. Rate them, add notes, and build a personal archive of your intellectual and entertainment journey.

**Stay Notified**
Get push notifications for task reminders through Firebase Cloud Messaging, so important deadlines never slip through the cracks.

## Getting Started

### What You'll Need

- Python 3.13+ and Poetry
- Node.js 22+
- PostgreSQL and Redis
- A Firebase project (free tier works fine)

### Setting Up Firebase

Firebase powers the push notification system. Here's how to set it up:

1. Head to the [Firebase Console](https://console.firebase.google.com/) and create a new project
2. Enable Cloud Messaging in your project settings
3. Generate a service account key (Project Settings → Service Accounts → Generate New Private Key)
4. Save it as `backend/firebase-service-account.json`
5. Grab your Firebase web app config from Project Settings → General
6. Generate a VAPID key pair in Cloud Messaging → Web Push certificates

### Running the Backend

```bash
cd backend

# Install dependencies
poetry install
poetry shell

# Configure your environment
cp .env.dev.example .env
# Open .env and add your database, Redis, OAuth, JWT, and Firebase credentials

# Set up the database
poetry run alembic upgrade head

# Start the server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be running at `http://localhost:8000`

### Running the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure your environment
cp .env.example .env
# Add your API URL and Firebase configuration

# Build the Firebase service worker
npm run generate-sw

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:5173`

### Docker Quick Start

If you prefer to run PostgreSQL and Redis in containers:

```bash
./tools/build-dev.sh
```

Then follow the backend and frontend setup steps above.

## Development

### Running Tests

```bash
# Backend tests with coverage
cd backend
poetry run pytest --cov=app

# Frontend tests
cd frontend
npm run test
npm run coverage
```

### Code Quality

```bash
# Backend linting and type checking
cd backend
poetry run ruff check
poetry run ruff format
poetry run mypy app

# Frontend type checking
cd frontend
npm run type-check
```

### Database Migrations

```bash
cd backend

# Create a new migration after model changes
poetry run alembic revision --autogenerate -m "description"

# Apply pending migrations
poetry run alembic upgrade head

# Roll back the last migration
poetry run alembic downgrade -1
```

## Deployment

The project includes an automated deployment script:

```bash
./tools/deploy.sh
```

This script handles everything: pulling the latest code, backing up the database, building Docker containers, running health checks, and cleaning up resources. The production setup uses Docker Compose with FastAPI, Vue.js served through Nginx, PostgreSQL, Redis, and Caddy for automatic HTTPS certificates.

Make sure your `.env.prod` file is configured with production credentials for the database, Redis, Google OAuth, JWT secrets, and Firebase service account path. The frontend needs production environment variables including the API URL and Firebase configuration with your VAPID public key.

## Built With

Zero Inertia uses FastAPI and PostgreSQL on the backend, Vue.js 3 with TypeScript on the frontend, Firebase Cloud Messaging for notifications, and Redis for caching. The production deployment runs on Docker with Caddy handling HTTPS termination.

## License

This project is free software licensed under the GNU General Public License v3.0.
