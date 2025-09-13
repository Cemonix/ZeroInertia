# Zero Inertia

An intelligent to-do list application that integrates AI for task categorization, activity timing, motivational features with TTS, and progress visualization.

## Architecture

- **Backend**: Python FastAPI with PostgreSQL, SQLAlchemy 2.0 (async), JWT authentication
- **Frontend**: Vue.js 3 with Composition API, Vite, Pinia, Tailwind CSS, PrimeVue, D3.js for charts

## Features

- 📋 **Task Management**: Full CRUD operations with timer functionality
- ⏱️ **Activity Timer**: Start/stop timers that track time spent per task
- 🤖 **AI Categorization**: Automatic task grouping using AI
- 💬 **AI Motivator**: Generated motivational messages with TTS
- 📊 **Progress Charts**: Time analytics visualized with D3.js charts

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 22+
- Docker & Docker Compose
- Poetry (for Python dependency management)
