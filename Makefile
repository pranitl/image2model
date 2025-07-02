# Image2Model Docker Development Makefile

.PHONY: help build up down restart logs shell-backend shell-frontend shell-worker clean prune test

# Default target
help:
	@echo "Image2Model Docker Development Commands:"
	@echo ""
	@echo "Setup & Management:"
	@echo "  make build          - Build all Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - Show logs from all services"
	@echo ""
	@echo "Development:"
	@echo "  make shell-backend  - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"
	@echo "  make shell-worker   - Open shell in worker container"
	@echo "  make shell-db       - Open psql shell in database"
	@echo ""
	@echo "Production:"
	@echo "  make prod-build     - Build production images"
	@echo "  make prod-deploy    - Deploy production environment"
	@echo "  make prod-start     - Start production services"
	@echo "  make prod-stop      - Stop production services"
	@echo "  make prod-logs      - Show production logs"
	@echo "  make prod-status    - Show production container status"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-reset       - Reset database (DESTRUCTIVE)"
	@echo ""
	@echo "Monitoring:"
	@echo "  make status         - Show container status"
	@echo "  make flower         - Open Celery Flower monitoring"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Stop containers and remove volumes"
	@echo "  make prune          - Remove unused Docker resources"
	@echo "  make test           - Run tests in containers"

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "Backend Docs: http://localhost:8000/docs"
	@echo "Flower (Celery): http://localhost:5555"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis: localhost:6379"

# Start services with logs
up-logs:
	docker-compose up

# Stop all services
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# Show logs from all services
logs:
	docker-compose logs -f

# Show logs from specific service
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-worker:
	docker-compose logs -f worker

logs-db:
	docker-compose logs -f postgres

# Open shell in backend container
shell-backend:
	docker-compose exec backend /bin/bash

# Open shell in frontend container
shell-frontend:
	docker-compose exec frontend /bin/sh

# Open shell in worker container
shell-worker:
	docker-compose exec worker /bin/bash

# Open PostgreSQL shell
shell-db:
	docker-compose exec postgres psql -U postgres -d image2model

# Show container status
status:
	docker-compose ps

# Run database migrations
db-migrate:
	docker-compose exec backend alembic upgrade head

# Reset database (DESTRUCTIVE)
db-reset:
	@echo "WARNING: This will destroy all data in the database!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker-compose down
	docker volume rm image2model-postgres-data || true
	docker-compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 10
	docker-compose up -d

# Open Celery Flower monitoring
flower:
	@echo "Opening Flower monitoring at http://localhost:5555"
	@python -m webbrowser http://localhost:5555 2>/dev/null || echo "Open http://localhost:5555 in your browser"

# Run tests
test:
	docker-compose exec backend python -m pytest
	docker-compose exec frontend npm test

# Run linting
lint:
	docker-compose exec backend flake8 app/
	docker-compose exec frontend npm run lint

# Clean up - stop containers and remove volumes
clean:
	docker-compose down -v
	docker system prune -f

# Prune unused Docker resources
prune:
	docker system prune -a -f
	docker volume prune -f

# Install dependencies
install:
	docker-compose exec backend pip install -r requirements.txt
	docker-compose exec frontend npm install

# Development mode - start with hot reload
dev:
	docker-compose up --build

# Production Commands
prod-build:
	./scripts/deploy.sh build

prod-deploy:
	./scripts/deploy.sh deploy

prod-start:
	docker-compose -f docker-compose.prod.yml up -d

prod-stop:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

prod-status:
	docker-compose -f docker-compose.prod.yml ps

# Show environment information
env-info:
	@echo "Environment Information:"
	@echo "Docker version: $(shell docker --version)"
	@echo "Docker Compose version: $(shell docker-compose --version)"
	@echo "Current directory: $(PWD)"
	@echo "Active containers: $(shell docker-compose ps -q | wc -l)"

# Quick setup for new developers
setup:
	@echo "Setting up Image2Model development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make build && make up"