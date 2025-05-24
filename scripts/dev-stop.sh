#!/bin/bash

# Development stop script for Langflow
# This script safely stops all development services

set -e

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

echo -e "${BLUE}🛑 Stopping Langflow Development Environment${NC}"

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

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            print_status "Stopping $service_name (PID: $pid)..."
            kill $pid
            
            # Wait for process to stop
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                print_warning "Force killing $service_name..."
                kill -9 $pid 2>/dev/null || true
            fi
            
            print_status "$service_name stopped"
        else
            print_warning "$service_name PID file exists but process is not running"
        fi
        
        rm -f "$pid_file"
    else
        print_warning "No PID file found for $service_name"
    fi
}

# Function to kill processes by port
kill_by_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        print_status "Killing $service_name processes on port $port..."
        echo $pids | xargs kill -9 2>/dev/null || true
        print_status "$service_name processes on port $port killed"
    else
        print_status "No processes found on port $port"
    fi
}

# Main cleanup function
cleanup() {
    cd "$PROJECT_ROOT"
    
    # Stop services by PID files first
    kill_by_pid_file ".frontend.pid" "Frontend"
    kill_by_pid_file ".backend.pid" "Backend"
    
    # Kill any remaining processes on the ports
    kill_by_port $FRONTEND_PORT "Frontend"
    kill_by_port $BACKEND_PORT "Backend"
    
    # Clean up any other Langflow processes
    print_status "Cleaning up any remaining Langflow processes..."
    pkill -f "langflow" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    
    print_status "🎉 All Langflow development services stopped"
}

# Run cleanup
cleanup
