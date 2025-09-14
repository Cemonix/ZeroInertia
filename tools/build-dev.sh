#!/usr/bin/env bash

# This script builds the development environment for the ZeroInertia project.
set -e
echo "Building development environment..."

# Build the Docker images and start the containers
docker compose --env-file backend/.env -f docker-compose.dev.yml up --build -d

echo "Development environment is up and running!"