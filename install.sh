#!/bin/bash

# ARC Raiders Conditions MCP Server Installation Script

set -e

echo "🎮 ARC Raiders Conditions MCP Server Setup"
echo "=========================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' || echo "0.0")
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 8 ]]; then
    echo "❌ Python 3.8 or higher is required. Found: Python $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install mcp requests beautifulsoup4 lxml

# Test the scraper first
echo "🧪 Testing the scraper..."
if python3 arc_raiders_scraper.py > /dev/null 2>&1; then
    echo "✅ Scraper test passed"
else
    echo "⚠️  Scraper test failed - continuing anyway"
fi

# Get the absolute path
SCRIPT_PATH=$(pwd)/mcp_server.py

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Test the MCP server:"
echo "   python3 mcp_server.py"
echo ""
echo "2. Add to Claude Desktop config:"
echo ""
echo "macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo ""
echo "Add this configuration:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"arc-raiders-conditions\": {"
echo "      \"command\": \"python3\","
echo "      \"args\": [\"$SCRIPT_PATH\"],"
echo "      \"env\": {}"
echo "    }"
echo "  }"
echo "}"
echo ""
echo "3. Restart Claude Desktop"
echo ""
echo "🤖 Available MCP Tools:"
echo "- get_map_conditions: Get all current map conditions"
echo "- get_specific_map_condition: Get details for one map"
echo "- get_active_conditions_only: Show only active conditions"
echo "- get_next_conditions: Show upcoming conditions"
echo ""
echo "🎮 Ready to provide ARC Raiders intel to AI!"