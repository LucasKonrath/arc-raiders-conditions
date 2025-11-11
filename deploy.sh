#!/bin/bash

# Deployment script for ARC Raiders REST API

echo "🚀 ARC Raiders API Deployment Helper"
echo "===================================="

show_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) Local development server"
    echo "2) Generate Heroku deployment files"
    echo "3) Generate Railway deployment files"  
    echo "4) Generate Docker files"
    echo "5) Test API locally"
    echo "6) Exit"
    echo ""
}

deploy_local() {
    echo "🔧 Starting local development server..."
    echo "📍 Server will be available at: http://localhost:5000"
    echo "📖 API docs: http://localhost:5000/api/v1/docs"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    source .venv/bin/activate
    python rest_api_server.py
}

generate_heroku() {
    echo "📦 Generating Heroku deployment files..."
    
    # Create Procfile
    cat > Procfile << EOF
web: python rest_api_server.py
EOF
    
    # Create runtime.txt
    cat > runtime.txt << EOF
python-3.11.0
EOF
    
    # Update requirements.txt for production
    cat > requirements_heroku.txt << EOF
flask>=2.0.0
flask-cors>=3.0.0
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0
gunicorn>=20.0.0
EOF
    
    echo "✅ Created:"
    echo "   - Procfile"
    echo "   - runtime.txt"
    echo "   - requirements_heroku.txt"
    echo ""
    echo "📋 Next steps for Heroku:"
    echo "1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
    echo "2. heroku login"
    echo "3. heroku create your-app-name"
    echo "4. cp requirements_heroku.txt requirements.txt"
    echo "5. git add ."
    echo "6. git commit -m 'Deploy to Heroku'"
    echo "7. git push heroku main"
}

generate_railway() {
    echo "🚂 Generating Railway deployment files..."
    
    # Create railway.toml
    cat > railway.toml << EOF
[build]
builder = "nixpacks"

[deploy]
startCommand = "python3 rest_api_server.py"
healthcheckPath = "/health"
restartPolicyType = "always"

[[services]]
name = "arc-raiders-api"
source = "."
EOF
    
    echo "✅ Created: railway.toml"
    echo ""
    echo "📋 Next steps for Railway:"
    echo "1. Install Railway CLI: https://docs.railway.app/develop/cli"
    echo "2. railway login"
    echo "3. railway init"
    echo "4. railway up"
}

generate_docker() {
    echo "🐳 Generating Docker files..."
    
    # Create Dockerfile
    cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "rest_api_server.py"]
EOF
    
    # Create docker-compose.yml
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  arc-raiders-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF
    
    # Create .dockerignore
    cat > .dockerignore << EOF
.git
.gitignore
README.md
MCP_README.md
CHATGPT_INTEGRATION.md
.venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
claude_desktop_config.json
arc_raiders_conditions.json
EOF
    
    echo "✅ Created:"
    echo "   - Dockerfile"
    echo "   - docker-compose.yml"
    echo "   - .dockerignore"
    echo ""
    echo "📋 Next steps for Docker:"
    echo "1. docker-compose up --build"
    echo "2. API will be available at http://localhost:5000"
}

test_api() {
    echo "🧪 Testing API locally..."
    
    # Check if server is running
    if curl -s http://localhost:5000/health >/dev/null 2>&1; then
        echo "✅ Server is running!"
        echo ""
        echo "🔍 Testing endpoints:"
        
        echo "1. Health check:"
        curl -s http://localhost:5000/health | python -m json.tool
        echo ""
        
        echo "2. Summary:"
        curl -s "http://localhost:5000/api/v1/conditions?format=summary" | python -m json.tool
        echo ""
        
        echo "3. Dam Battlegrounds:"
        curl -s "http://localhost:5000/api/v1/conditions/dam-battlegrounds?format=text" | python -m json.tool
        echo ""
        
    else
        echo "❌ Server is not running on localhost:5000"
        echo "💡 Start it with option 1 or run: python rest_api_server.py"
    fi
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            deploy_local
            ;;
        2)
            generate_heroku
            ;;
        3)
            generate_railway
            ;;
        4)
            generate_docker
            ;;
        5)
            test_api
            ;;
        6)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-6."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done