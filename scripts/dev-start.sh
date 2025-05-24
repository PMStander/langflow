#!/bin/bash

# Development startup script for Langflow
# This script ensures proper startup sequence and handles common issues

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT=7860
FRONTEND_PORT=3000
MAX_WAIT_TIME=120  # 2 minutes
HEALTH_CHECK_INTERVAL=5

echo -e "${BLUE}🚀 Starting Langflow Development Environment${NC}"
echo -e "${BLUE}Project Root: ${PROJECT_ROOT}${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    print_warning "Killing existing process on port $port"
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_wait=$3
    
    print_status "Waiting for $service_name to be ready at $url..."
    
    local count=0
    while [ $count -lt $max_wait ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            print_status "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
        count=$((count + HEALTH_CHECK_INTERVAL))
    done
    
    print_error "$service_name failed to start within ${max_wait} seconds"
    return 1
}

# Function to check database connectivity
check_database() {
    print_status "Checking database connectivity..."
    
    cd "$PROJECT_ROOT"
    
    # Load environment variables
    if [ -f ".env.development" ]; then
        export $(grep -v '^#' .env.development | xargs)
    fi
    
    # Simple database connectivity check
    python3 -c "
import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_db():
    try:
        db_url = os.getenv('LANGFLOW_DATABASE_URL', '')
        if not db_url:
            print('No database URL configured')
            return False
            
        # Convert to async URL if needed
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        await engine.dispose()
        print('Database connection successful')
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False

result = asyncio.run(check_db())
sys.exit(0 if result else 1)
" || {
        print_error "Database connectivity check failed"
        print_warning "Please ensure your database is running and accessible"
        return 1
    }
}

# Function to start backend
start_backend() {
    print_status "Starting Langflow backend..."
    
    cd "$PROJECT_ROOT"
    
    # Load development environment
    if [ -f ".env.development" ]; then
        export $(grep -v '^#' .env.development | xargs)
        print_status "Loaded development environment variables"
    fi
    
    # Check if backend port is in use
    if check_port $BACKEND_PORT; then
        print_warning "Backend port $BACKEND_PORT is already in use"
        read -p "Kill existing process? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_port $BACKEND_PORT
        else
            print_error "Cannot start backend - port $BACKEND_PORT is in use"
            return 1
        fi
    fi
    
    # Start backend in background
    print_status "Starting backend on port $BACKEND_PORT..."
    nohup python -m langflow run --backend-only --host 127.0.0.1 --port $BACKEND_PORT > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > .backend.pid
    print_status "Backend started with PID $BACKEND_PID"
    
    # Wait for backend to be ready
    if wait_for_service "http://127.0.0.1:$BACKEND_PORT/health" "Backend" $MAX_WAIT_TIME; then
        return 0
    else
        print_error "Backend failed to start"
        kill $BACKEND_PID 2>/dev/null || true
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting Langflow frontend..."
    
    cd "$PROJECT_ROOT/src/frontend"
    
    # Check if frontend port is in use
    if check_port $FRONTEND_PORT; then
        print_warning "Frontend port $FRONTEND_PORT is already in use"
        read -p "Kill existing process? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_port $FRONTEND_PORT
        else
            print_error "Cannot start frontend - port $FRONTEND_PORT is in use"
            return 1
        fi
    fi
    
    # Set environment variables for frontend
    export VITE_BACKEND_URL="http://127.0.0.1:$BACKEND_PORT"
    export VITE_PORT=$FRONTEND_PORT
    
    # Start frontend in background
    print_status "Starting frontend on port $FRONTEND_PORT..."
    nohup npm start > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    echo $FRONTEND_PID > ../../.frontend.pid
    print_status "Frontend started with PID $FRONTEND_PID"
    
    # Wait for frontend to be ready
    if wait_for_service "http://127.0.0.1:$FRONTEND_PORT" "Frontend" $MAX_WAIT_TIME; then
        return 0
    else
        print_error "Frontend failed to start"
        kill $FRONTEND_PID 2>/dev/null || true
        return 1
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_ROOT/.backend.pid")
        kill $BACKEND_PID 2>/dev/null || true
        rm -f "$PROJECT_ROOT/.backend.pid"
    fi
    
    if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend.pid")
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f "$PROJECT_ROOT/.frontend.pid"
    fi
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    # Create logs directory
    mkdir -p "$PROJECT_ROOT/logs"
    
    # Check database connectivity
    if ! check_database; then
        print_error "Database check failed. Please fix database issues before continuing."
        exit 1
    fi
    
    # Start backend
    if ! start_backend; then
        print_error "Failed to start backend"
        exit 1
    fi
    
    # Start frontend
    if ! start_frontend; then
        print_error "Failed to start frontend"
        cleanup
        exit 1
    fi
    
    print_status "🎉 Langflow development environment is ready!"
    print_status "Frontend: http://127.0.0.1:$FRONTEND_PORT"
    print_status "Backend:  http://127.0.0.1:$BACKEND_PORT"
    print_status ""
    print_status "Logs:"
    print_status "  Backend:  logs/backend.log"
    print_status "  Frontend: logs/frontend.log"
    print_status ""
    print_status "Press Ctrl+C to stop all services"
    
    # Wait for user interrupt
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
