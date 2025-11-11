#!/bin/bash

# Railway startup script that handles different Python environments

echo "🚀 Starting ARC Raiders API on Railway..."

# Try to find Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found!"
    exit 1
fi

echo "✅ Using Python: $PYTHON_CMD"

# Install dependencies if needed
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..."
    $PYTHON_CMD -m pip install --user -r requirements.txt
fi

# Start the server
echo "🌐 Starting server..."
exec $PYTHON_CMD rest_api_server.py