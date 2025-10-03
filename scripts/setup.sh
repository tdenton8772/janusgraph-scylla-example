#!/bin/bash
# Setup script for JanusGraph ScyllaDB Example Project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
    
    print_success "All system requirements are met"
}

create_python_venv() {
    print_status "Setting up Python virtual environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created Python virtual environment"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Installed Python dependencies"
    else
        print_warning "requirements.txt not found"
    fi
}

setup_environment() {
    print_status "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Create .env file from template if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.template" ]; then
            cp .env.template .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your ScyllaDB connection details"
        else
            print_warning ".env.template not found, creating basic .env file"
            cat > .env << EOF
# Local development settings
SCYLLA_HOST=localhost
SCYLLA_PORT=9042
SCYLLA_USERNAME=
SCYLLA_PASSWORD=
SCYLLA_KEYSPACE=janusgraph
ECOMMERCE_KEYSPACE=ecommerce
SCYLLA_SSL_ENABLED=false

# JanusGraph settings
JANUSGRAPH_HOST=localhost
JANUSGRAPH_PORT=8182

# Application settings
NUM_USERS=50
NUM_PRODUCTS=100
MAX_ORDERS_PER_USER=3
MAX_REVIEWS_PER_PRODUCT=5
LOG_LEVEL=INFO
EOF
            print_success "Created basic .env file"
        fi
    else
        print_status ".env file already exists"
    fi
}

start_docker_services() {
    print_status "Starting Docker services..."
    
    cd "$PROJECT_ROOT/docker"
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in docker/ directory"
        exit 1
    fi
    
    # Stop any existing containers
    docker-compose down
    
    # Start services
    print_status "Starting JanusGraph and related services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for JanusGraph to be ready..."
    sleep 30
    
    # Check if JanusGraph is responding
    for i in {1..12}; do
        if curl -s http://localhost:8182 > /dev/null; then
            print_success "JanusGraph is ready!"
            break
        else
            print_status "Waiting for JanusGraph... (attempt $i/12)"
            sleep 10
        fi
        
        if [ $i -eq 12 ]; then
            print_error "JanusGraph failed to start within timeout"
            print_status "Check Docker logs: docker-compose -f docker/docker-compose.yml logs"
            exit 1
        fi
    done
}

stop_docker_services() {
    print_status "Stopping Docker services..."
    
    cd "$PROJECT_ROOT/docker"
    docker-compose down
    
    print_success "Docker services stopped"
}

show_status() {
    print_status "Checking service status..."
    
    cd "$PROJECT_ROOT/docker"
    docker-compose ps
    
    print_status "Service URLs:"
    echo "  JanusGraph Gremlin Server: ws://localhost:8182/gremlin"
    echo "  ScyllaDB CQL: localhost:9042"
    
    if curl -s http://localhost:8182 > /dev/null; then
        print_success "JanusGraph is accessible"
    else
        print_warning "JanusGraph is not responding"
    fi
}

run_demo() {
    print_status "Running the demo application..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        print_error "Virtual environment not found. Run setup first."
        exit 1
    fi
    
    # Run the demo
    python3 python/ecommerce_demo.py --all
}

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup       Setup the complete development environment"
    echo "  start       Start Docker services (JanusGraph, ScyllaDB)"
    echo "  stop        Stop Docker services"
    echo "  status      Show service status"
    echo "  demo        Run the demo application"
    echo "  clean       Clean up Docker containers and volumes"
    echo "  help        Show this help message"
    echo ""
    echo "For first-time setup, run: $0 setup && $0 start"
}

clean_up() {
    print_status "Cleaning up Docker resources..."
    
    cd "$PROJECT_ROOT/docker"
    docker-compose down -v --remove-orphans
    
    # Remove any dangling volumes
    docker volume prune -f
    
    print_success "Cleanup complete"
}

# Main script logic
case "${1:-help}" in
    "setup")
        print_status "Starting complete setup..."
        check_requirements
        create_python_venv
        setup_environment
        print_success "Setup complete! Now run: $0 start"
        ;;
    "start")
        start_docker_services
        ;;
    "stop")
        stop_docker_services
        ;;
    "status")
        show_status
        ;;
    "demo")
        run_demo
        ;;
    "clean")
        clean_up
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac