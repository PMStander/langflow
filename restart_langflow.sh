#!/bin/bash

# Stop any running Langflow processes
echo "Stopping any running Langflow processes..."
pkill -f "langflow"

# Wait a moment for processes to terminate
sleep 2

# Start Langflow in the background
echo "Starting Langflow..."
cd /Users/peetstander/Projects/langflow
python -m langflow run &

# Wait for Langflow to start
echo "Waiting for Langflow to start..."
sleep 5

echo "Langflow has been restarted!"
