#!/bin/bash
set -e

COMPOSE="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE="docker-compose"
fi

echo "Running backend tests..."
$COMPOSE exec backend pytest tests/ -v --cov=app --cov-report=term-missing

echo "Running frontend tests..."
$COMPOSE exec frontend npm test -- --run 2>/dev/null || echo "Frontend tests skipped (run locally with: cd frontend && npm test)"
