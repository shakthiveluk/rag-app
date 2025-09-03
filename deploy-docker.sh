#!/bin/bash

# Docker Deployment Script for RAG Application
# This script builds and runs the application using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🐳 Docker Deployment for RAG Application${NC}"
    echo "=============================================="
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        print_info "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your actual API keys before continuing"
        read -p "Press Enter after updating .env file..."
    fi
    
    # Load environment variables
    source .env
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-actual-openai-api-key-here" ]; then
        print_error "Please set your OpenAI API key in .env file"
        exit 1
    fi
    
    print_status "Environment variables loaded"
}

# Build Docker image
build_image() {
    print_info "Building Docker image..."
    docker build -t rag-app .
    print_status "Docker image built successfully"
}

# Run with Docker Compose
run_compose() {
    print_info "Starting application with Docker Compose..."
    docker-compose up -d
    print_status "Application started successfully"
    
    print_info "Your app is running at: http://localhost:8501"
    print_info "To view logs: docker-compose logs -f"
    print_info "To stop: docker-compose down"
}

# Run with Docker directly
run_docker() {
    print_info "Starting application with Docker..."
    docker run -d \
        --name rag-app \
        -p 8501:8501 \
        --env-file .env \
        rag-app
    
    print_status "Application started successfully"
    print_info "Your app is running at: http://localhost:8501"
    print_info "To view logs: docker logs rag-app"
    print_info "To stop: docker stop rag-app"
}

# Main deployment function
main() {
    print_header
    
    # Check prerequisites
    check_docker
    check_env
    
    # Build image
    build_image
    
    # Choose deployment method
    echo
    print_info "Choose deployment method:"
    echo "1. Docker Compose (recommended)"
    echo "2. Docker directly"
    read -p "Enter choice (1-2): " choice
    
    case $choice in
        1)
            run_compose
            ;;
        2)
            run_docker
            ;;
        *)
            print_error "Invalid choice. Using Docker Compose..."
            run_compose
            ;;
    esac
    
    echo
    print_status "Deployment complete! 🎉"
    print_info "Check http://localhost:8501 to verify your app is running"
}

# Run main function
main "$@"
