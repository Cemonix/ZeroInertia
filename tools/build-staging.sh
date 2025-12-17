#!/usr/bin/env bash

# This script builds the development environment for the ZeroInertia project.
set -e
echo "Building staging environment..."

# Build the Docker images and start the containers
docker compose --env-file backend/.env.staging -f docker-compose.staging.yml up --build -d

echo "Staging environment is up and running!"