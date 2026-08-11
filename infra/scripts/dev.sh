#!/usr/bin/env bash
set -euo pipefail

echo "Starting CoachOS local development environment..."

# Verify docker compose availability
if command -v docker &> /dev/null; then
    docker compose up --build
else
    echo "Docker not found. Please install Docker or start services manually according to docs/architecture/LOCAL_DEVELOPMENT.md"
    exit 1
fi
