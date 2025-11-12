#!/bin/bash

# Zero Inertia Deployment Script
# Usage: ./deploy.sh [--skip-backup]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="./backend/.env"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_warning "Running as root. Consider using a non-root user with docker permissions."
fi

# Parse arguments
SKIP_BACKUP=false
if [ "$1" == "--skip-backup" ]; then
    SKIP_BACKUP=true
fi

log_info "Starting Zero Inertia deployment..."

# Pull latest code
log_info "Pulling latest code from Git..."
git fetch origin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    log_error "Not on main branch. Current branch: $CURRENT_BRANCH"
    exit 1
fi
git pull origin main
log_success "Code updated"

# Backup database (optional)
if [ "$SKIP_BACKUP" = false ]; then
    log_info "Creating database backup..."

    # Extract database credentials from Docker Compose config (respects .env and defaults)
    DB_USER=$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config | grep -A 5 'postgres:' | grep 'POSTGRES_USER:' | sed 's/.*POSTGRES_USER: //' | tr -d '"')
    DB_NAME=$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config | grep -A 5 'postgres:' | grep 'POSTGRES_DB:' | sed 's/.*POSTGRES_DB: //' | tr -d '"')

    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"

    # Backup PostgreSQL
    if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres pg_dump \
            -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql" 2>/dev/null; then
            log_success "Database backed up to $BACKUP_DIR/db_backup_$TIMESTAMP.sql"
        else
            log_warning "Database backup failed, but continuing deployment..."
        fi
    else
        log_warning "PostgreSQL container not running, skipping backup"
    fi
else
    log_info "Skipping database backup (--skip-backup flag)"
fi

# Build new images
log_info "Building Docker images..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --no-cache
log_success "Images built successfully"

# Stop old containers
log_info "Stopping old containers..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down
log_success "Old containers stopped"

# Start new containers
log_info "Starting new containers..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
log_success "New containers started"

# Wait for services to be healthy
log_info "Waiting for services to be healthy..."
sleep 10

# Check backend health
if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps backend | grep -q "Up"; then
    log_success "Backend is running"
else
    log_error "Backend failed to start"
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs backend
    exit 1
fi

# Check frontend health
if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps frontend | grep -q "Up"; then
    log_success "Frontend is running"
else
    log_error "Frontend failed to start"
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs frontend
    exit 1
fi

# Clean up old images
log_info "Cleaning up old Docker images..."
docker image prune -f
log_success "Cleanup complete"

# Show running containers
log_info "Current running containers:"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

# Final message
echo ""
log_success "🚀 Deployment completed successfully!"
log_info "Application is running at: https://zeroinertia.cemonix.dev"
echo ""
