# ARC Raiders Conditions MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with real-time access to ARC Raiders map conditions from [arc-raiders.dev](https://arc-raiders.dev).

## Features

🎮 **Real-time Map Conditions**: Get current active conditions for all ARC Raiders maps  
🗺️ **Specific Map Queries**: Query individual maps for detailed condition info  
🔥 **Major Condition Filtering**: Focus on high-impact major conditions  
⏳ **Upcoming Conditions**: See what's coming next and when  
📊 **Multiple Output Formats**: JSON, formatted text, or quick summaries  
🤖 **AI-Friendly**: Designed for consumption by AI assistants via MCP

## Maps Tracked

- Dam Battlegrounds
- Buried City
- The Spaceport
- The Blue Gate
- Practice Range
- Stella Montis

## Installation

### Method 1: Direct Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
# or
pip install mcp requests beautifulsoup4 lxml
```

3. Run the MCP server:

```bash
python mcp_server.py
```

### Method 2: Development Installation

```bash
# Install in development mode
pip install -e .

# Run the server
arc-raiders-mcp
```

## MCP Tools Available

The server provides 4 tools that AI assistants can use:

### 1. `get_map_conditions`
Get current conditions for all maps.

**Parameters:**
- `format` (optional): "json", "text", or "summary" (default: "text")

**Example Usage:**
```
Get all current ARC Raiders map conditions
```

### 2. `get_specific_map_condition`
Get detailed info for a specific map.

**Parameters:**
- `map_name` (required): Name of the map
- `format` (optional): "json" or "text" (default: "text")

**Example Usage:**
```
Get the current condition for Dam Battlegrounds
```

### 3. `get_active_conditions_only`
Get only maps that currently have active conditions.

**Parameters:**
- `include_major_only` (optional): If true, only major conditions (default: false)
- `format` (optional): "json", "text", or "summary" (default: "text")

**Example Usage:**
```
Show me only maps with active conditions
Show me only maps with major conditions
```

### 4. `get_next_conditions`
Get upcoming conditions and timing.

**Parameters:**
- `format` (optional): "json" or "text" (default: "text")

**Example Usage:**
```
What conditions are coming up next?
```

## Claude Desktop Integration

To use this MCP server with Claude Desktop, add it to your `claude_desktop_config.json`:

### macOS
```bash
# Edit the config file
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Windows
```bash
# Edit the config file
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration:

```json
{
  "mcpServers": {
    "arc-raiders-conditions": {
      "command": "python",
      "args": ["/path/to/your/arc-raiders-conditions/mcp_server.py"],
      "env": {}
    }
  }
}
```

Replace `/path/to/your/arc-raiders-conditions/` with the actual path to your installation.

## Usage Examples

Once connected to an AI assistant via MCP, you can ask:

- "What are the current ARC Raiders map conditions?"
- "Show me only maps with active conditions"
- "What's the condition on Dam Battlegrounds?"
- "Which maps have major conditions right now?"
- "What conditions are coming up next?"
- "Give me a quick summary of the current status"

## Sample Output

### All Conditions (Text Format)
```
🎮 ARC RAIDERS MAP CONDITIONS
==================================================
⏰ Current Time: 4:43:16 PM
🌍 Timezone: America/Sao_Paulo
📊 Total Maps: 6

🗺️  Dam Battlegrounds
---------------------
   🟢 Current: HIDDEN CACHES
   ⏳ Next: NIGHT RAID at 8:00 PM

🗺️  The Spaceport
-----------------
   🟢 Current: HIDDEN BUNKER 🔥 MAJOR
   ⏳ Next: NIGHT RAID at 10:00 PM
```

### Active Conditions Only
```
🟢 ACTIVE CONDITIONS (2 maps)
==================================================
🗺️  Dam Battlegrounds
   🟢 Current: HIDDEN CACHES
   ⏳ Next: NIGHT RAID at 8:00 PM

🗺️  The Spaceport
   🟢 Current: HIDDEN BUNKER 🔥 MAJOR
   ⏳ Next: NIGHT RAID at 10:00 PM
```

### Summary Format
```
📊 ARC Raiders Status: 3/6 maps have active conditions (2 major conditions)
```

## Architecture

- **`mcp_server.py`**: Main MCP server implementation
- **`arc_raiders_scraper.py`**: Web scraping logic (reused from original script)
- **`pyproject.toml`**: Python package configuration
- **`package.json`**: Node.js compatibility and metadata

## Error Handling

The server includes robust error handling for:
- Network connectivity issues
- Website structure changes
- Invalid tool parameters
- MCP protocol errors

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Troubleshooting

### Server Won't Start
1. Check Python version (requires 3.8+)
2. Verify all dependencies are installed
3. Check firewall/network settings

### No Data Returned
1. Verify internet connection
2. Check if arc-raiders.dev is accessible
3. Website structure may have changed (check logs)

### AI Assistant Can't Connect
1. Verify MCP server is running
2. Check configuration file path
3. Restart AI assistant application

## License

MIT License - feel free to modify and distribute

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the [Issues](https://github.com/LucasKonrath/arc-raiders-conditions/issues) page
- Create a new issue with detailed information
- Include error logs and system information