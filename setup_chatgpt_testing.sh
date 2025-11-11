#!/bin/bash

# Quick setup script for testing with ChatGPT via ngrok

echo "🚀 ARC Raiders API - ChatGPT Testing Setup"
echo "=========================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed"
    echo ""
    echo "📦 Install ngrok:"
    echo "1. Visit: https://ngrok.com/download"
    echo "2. Or use Homebrew: brew install ngrok"
    echo "3. Sign up for free account and authenticate"
    echo ""
    exit 1
fi

echo "✅ ngrok is installed"

# Start the API server in background
echo "🔧 Starting ARC Raiders API server..."
/Users/lucasdamaceno/Documents/pocs/arc-raiders-conditions/.venv/bin/python rest_api_server.py &
API_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if ! curl -s http://localhost:5001/health > /dev/null; then
    echo "❌ API server failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ API server running on port 5001"

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel..."
echo "⚠️  Keep this terminal open while testing with ChatGPT"
echo ""

# Create ngrok config
cat > ngrok_config.yml << EOF
version: "2"
tunnels:
  arc-raiders-api:
    proto: http
    addr: 5001
    hostname: arc-raiders-api-$(date +%s).ngrok.io
EOF

echo "📋 Instructions:"
echo "1. Copy the HTTPS URL that ngrok provides below"
echo "2. Replace 'https://your-production-server.com' in the OpenAPI schema"
echo "3. Use the updated schema in ChatGPT Actions"
echo ""
echo "Press Ctrl+C to stop both ngrok and the API server"
echo ""

# Trap to cleanup on exit
trap "echo 'Stopping servers...'; kill $API_PID 2>/dev/null; exit" INT TERM

# Start ngrok
ngrok http 5001 --log=stdout