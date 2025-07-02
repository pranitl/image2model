#!/bin/bash

# Image2Model Production Deployment Script
# This script deploys the application using Docker Compose

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

# Function to check environment file
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Please create one from .env.example"
        exit 1
    fi
    
    # Check required environment variables
    source .env
    
    required_vars=(
        "POSTGRES_PASSWORD"
        "SECRET_KEY"
        "FAL_KEY_ID"
        "FAL_KEY_SECRET"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_error "Please set these variables in your .env file."
        exit 1
    fi
    
    print_success "Environment configuration check passed"
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    print_success "Docker images built successfully"
}

# Function to deploy application
deploy() {
    print_status "Deploying application..."
    
    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down
    
    # Remove orphaned containers
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Application deployed successfully"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to start
    sleep 30
    
    services=("postgres" "redis" "backend" "frontend")
    
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "${service}.*Up"; then
            print_success "$service is running"
        else
            print_error "$service is not running"
            docker-compose -f docker-compose.prod.yml logs "$service"
            exit 1
        fi
    done
    
    # Test API endpoint
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend API is responding"
    else
        print_error "Backend API is not responding"
        exit 1
    fi
    
    print_success "All services are healthy"
}

# Function to show deployment info
show_info() {
    echo
    print_success "Deployment completed successfully!"
    echo
    echo "Service URLs:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Flower (Celery Monitor): http://localhost:5555"
    echo
    echo "Useful commands:"
    echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f [service]"
    echo "  Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "  Restart service: docker-compose -f docker-compose.prod.yml restart [service]"
    echo
}

# Function to show help
show_help() {
    echo "Image2Model Deployment Script"
    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  deploy      Deploy the application (default)"
    echo "  build       Build Docker images only"
    echo "  down        Stop all services"
    echo "  logs        Show logs for all services"
    echo "  status      Show status of all services"
    echo "  help        Show this help message"
    echo
}

# Main deployment function
main_deploy() {
    echo "🚀 Image2Model Production Deployment"
    echo "====================================="
    echo
    
    check_prerequisites
    check_environment
    build_images
    deploy
    check_health
    show_info
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main_deploy
        ;;
    "build")
        check_prerequisites
        build_images
        ;;
    "down")
        print_status "Stopping all services..."
        docker-compose -f docker-compose.prod.yml down
        print_success "All services stopped"
        ;;
    "logs")
        docker-compose -f docker-compose.prod.yml logs -f
        ;;
    "status")
        docker-compose -f docker-compose.prod.yml ps
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac