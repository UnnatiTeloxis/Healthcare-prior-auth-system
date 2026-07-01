.PHONY: help install build up down logs test migrate seed clean restart prod prod-down

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies locally"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services (development)"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - View logs"
	@echo "  make test      - Run backend tests"
	@echo "  make migrate   - Run database migrations"
	@echo "  make seed      - Seed database with test data"
	@echo "  make clean     - Clean Docker artifacts"
	@echo "  make restart   - Restart all services"
	@echo "  make prod      - Start production stack"
	@echo "  make prod-down - Stop production stack"

install:
	@echo "Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

build:
	@echo "Building Docker images..."
	docker compose build

up:
	@echo "Starting services..."
	docker compose up -d
	@echo "Services started!"
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	@echo "Stopping services..."
	docker compose down

logs:
	docker compose logs -f

parity-check:
	@echo "Running Inferno parity check on all JSON samples..."
	cd backend && python scripts/parity_check_all_samples.py

test:
	@echo "Running tests..."
	docker compose exec backend pytest tests/ -v

migrate:
	@echo "Running migrations..."
	docker compose exec backend alembic upgrade head

seed:
	@echo "Seeding database..."
	docker compose exec backend python /app/scripts/seed_data.py

clean:
	@echo "Cleaning Docker artifacts..."
	docker compose down -v
	docker system prune -f

restart: down up
	@echo "Services restarted!"

prod:
	@echo "Starting production stack..."
	docker compose -f docker-compose.prod.yml up -d --build

prod-down:
	@echo "Stopping production stack..."
	docker compose -f docker-compose.prod.yml down
