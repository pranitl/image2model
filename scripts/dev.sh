#!/bin/bash

# Image2Model Development Environment Script
# This script manages the development environment using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup development environment
setup_dev_env() {
    print_status "Setting up development environment..."
    
    # Check if .env exists, if not create from example
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_success "Created .env from .env.example"
        print_warning "Please review and update .env file with your configuration"
    fi
    
    # Create necessary directories
    mkdir -p backend/uploads backend/results backend/models backend/logs
    mkdir -p frontend/dist
    
    print_success "Development environment setup completed"
}

# Function to start development services
start_dev() {
    print_status "Starting development environment..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    docker-compose up --build -d
    
    print_success "Development environment started"
    
    # Show service status
    sleep 5
    show_status
}

# Function to start with logs
start_with_logs() {
    print_status "Starting development environment with logs..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start services with logs
    docker-compose up --build
}

# Function to stop development services
stop_dev() {
    print_status "Stopping development environment..."
    docker-compose down
    print_success "Development environment stopped"
}

# Function to restart a specific service
restart_service() {
    local service=$1
    if [ -z "$service" ]; then
        print_error "Please specify a service to restart"
        echo "Available services: backend, frontend, worker, postgres, redis, flower"
        exit 1
    fi
    
    print_status "Restarting $service..."
    docker-compose restart "$service"
    print_success "$service restarted"
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Function to show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Flower (Celery Monitor): http://localhost:5555"
    echo "  PgAdmin: http://localhost:5050"
    echo "  Redis Commander: http://localhost:8081"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Backend tests
    if docker-compose ps | grep -q "backend.*Up"; then
        print_status "Running backend tests..."
        docker-compose exec backend pytest
    else
        print_warning "Backend container is not running"
    fi
    
    # Frontend tests (if they exist)
    if docker-compose ps | grep -q "frontend.*Up"; then
        print_status "Running frontend tests..."
        docker-compose exec frontend npm test -- --run --reporter=verbose
    else
        print_warning "Frontend container is not running"
    fi
}

# Function to clean up
cleanup() {
    print_status "Cleaning up development environment..."
    
    # Stop and remove containers
    docker-compose down -v --remove-orphans
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this)
    read -p "Do you want to remove unused Docker volumes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
    fi
    
    print_success "Cleanup completed"
}

# Function to access container shell
shell() {
    local service=$1
    if [ -z "$service" ]; then
        print_error "Please specify a service for shell access"
        echo "Available services: backend, frontend, worker, postgres, redis"
        exit 1
    fi
    
    print_status "Opening shell in $service container..."
    if [ "$service" = "postgres" ]; then
        docker-compose exec "$service" psql -U postgres -d image2model
    elif [ "$service" = "redis" ]; then
        docker-compose exec "$service" redis-cli
    else
        docker-compose exec "$service" /bin/bash
    fi
}

# Function to show help
show_help() {
    echo "Image2Model Development Environment Script"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  setup       Setup development environment"
    echo "  start       Start development services (detached)"
    echo "  logs        Start development services with logs"
    echo "  stop        Stop all services"
    echo "  restart     Restart a specific service"
    echo "  status      Show service status and URLs"
    echo "  test        Run tests"
    echo "  logs        Show logs (optionally for specific service)"
    echo "  shell       Access container shell"
    echo "  cleanup     Clean up containers, images, and volumes"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 setup               # Setup development environment"
    echo "  $0 start               # Start all services"
    echo "  $0 restart backend     # Restart backend service"
    echo "  $0 logs frontend       # Show frontend logs"
    echo "  $0 shell backend       # Access backend container shell"
    echo
}

# Parse command line arguments
case "${1:-help}" in
    "setup")
        check_prerequisites
        setup_dev_env
        ;;
    "start")
        check_prerequisites
        setup_dev_env
        start_dev
        ;;
    "logs"|"up")
        check_prerequisites
        setup_dev_env
        start_with_logs
        ;;
    "stop"|"down")
        stop_dev
        ;;
    "restart")
        restart_service "$2"
        ;;
    "status"|"ps")
        show_status
        ;;
    "test")
        run_tests
        ;;
    "logs")
        show_logs "$2"
        ;;
    "shell"|"exec")
        shell "$2"
        ;;
    "cleanup"|"clean")
        cleanup
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac