#!/bin/bash
set -e

ENV=${1:-prod}
COMPOSE="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE="docker-compose"
fi

if [ ! -f .env ]; then
    echo "Missing .env file. Copy .env.example to .env and configure production values."
    exit 1
fi

echo "Deploying Interop Automation Platform ($ENV)..."

if [ "$ENV" = "prod" ]; then
    $COMPOSE -f docker-compose.prod.yml build --no-cache
    $COMPOSE -f docker-compose.prod.yml up -d
    echo "Production deployment complete."
else
    $COMPOSE build
    $COMPOSE up -d
    echo "Development deployment complete."
fi

echo "Waiting for health checks..."
sleep 20
curl -sf http://localhost:8000/health && echo " Backend healthy"
curl -sf http://localhost:3000/ && echo " Frontend healthy" || curl -sf http://localhost/ && echo " Frontend healthy"
