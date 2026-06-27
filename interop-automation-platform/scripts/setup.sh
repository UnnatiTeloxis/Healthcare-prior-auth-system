#!/bin/bash
set -e

echo "Setting up Interop Automation Platform..."

if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

COMPOSE="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE="docker-compose"
fi

if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo "Building Docker images..."
$COMPOSE build

echo "Starting services..."
$COMPOSE up -d

echo "Waiting for services to be ready..."
sleep 15

echo "Setup complete!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To run migrations: make migrate"
echo "To seed data:      make seed"
