#!/usr/bin/env bash

# This script builds the staging environment for the ZeroInertia project.
set -e
echo "Building staging environment..."

# Build the Docker images and start the containers
# The backend entrypoint will automatically run migrations before starting
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml up --build -d

echo ""
echo "Staging environment is starting..."
echo "The backend will automatically run migrations and seed the database."
echo ""
echo "Waiting for all services to be healthy..."
sleep 5

# Check status
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml ps

echo ""
echo "✅ Staging environment is up!"
echo ""
echo "📍 Access points:"
echo "   - Application: http://localhost:8082"
echo "   - Grafana:     http://localhost:8082/grafana/"
echo "   - Prometheus:  http://localhost:9091"
echo ""
echo "📊 View logs with:"
echo "   docker compose --env-file backend/.env.staging -f docker-compose.staging.yml logs -f"