#!/usr/bin/env python3
"""
ARC Raiders Map Conditions MCP Server

This MCP server provides AI assistants with access to real-time ARC Raiders map conditions
from https://arc-raiders.dev. AI can query current conditions, next conditions, and timing
for all available maps.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Import our existing scraper
from arc_raiders_scraper import ARCRaidersScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arc-raiders-mcp")

# Initialize the MCP server
server = Server("arc-raiders-conditions")

# Global scraper instance
scraper = ARCRaidersScraper()


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    List available tools.
    """
    return [
        Tool(
            name="get_map_conditions",
            description="Get current active map conditions for all ARC Raiders maps",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["json", "text", "summary"],
                        "description": "Output format: json (structured data), text (formatted display), or summary (brief overview)",
                        "default": "text"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_specific_map_condition",
            description="Get condition details for a specific map",
            inputSchema={
                "type": "object",
                "properties": {
                    "map_name": {
                        "type": "string",
                        "enum": [
                            "Dam Battlegrounds",
                            "Buried City", 
                            "The Spaceport",
                            "The Blue Gate",
                            "Practice Range",
                            "Stella Montis"
                        ],
                        "description": "Name of the specific map to query"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "text"],
                        "description": "Output format",
                        "default": "text"
                    }
                },
                "required": ["map_name"]
            }
        ),
        Tool(
            name="get_active_conditions_only",
            description="Get only maps that currently have active conditions (filters out inactive maps)",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_major_only": {
                        "type": "boolean",
                        "description": "If true, only return maps with major conditions",
                        "default": False
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "text", "summary"],
                        "description": "Output format",
                        "default": "text"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_next_conditions",
            description="Get upcoming conditions and their timing for all maps",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["json", "text"],
                        "description": "Output format",
                        "default": "text"
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Handle tool calls.
    """
    try:
        if name == "get_map_conditions":
            return await get_map_conditions(arguments.get("format", "text"))
        
        elif name == "get_specific_map_condition":
            map_name = arguments.get("map_name")
            format_type = arguments.get("format", "text")
            return await get_specific_map_condition(map_name, format_type)
        
        elif name == "get_active_conditions_only":
            include_major_only = arguments.get("include_major_only", False)
            format_type = arguments.get("format", "text")
            return await get_active_conditions_only(include_major_only, format_type)
        
        elif name == "get_next_conditions":
            format_type = arguments.get("format", "text")
            return await get_next_conditions(format_type)
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_map_conditions(format_type: str = "text") -> List[TextContent]:
    """Get all map conditions."""
    data = scraper.scrape()
    
    if "error" in data:
        return [TextContent(type="text", text=f"❌ Error fetching map conditions: {data['error']}")]
    
    if format_type == "json":
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    elif format_type == "summary":
        active_count = sum(1 for m in data["maps"] if m.get("current_condition"))
        major_count = sum(1 for m in data["maps"] if m.get("is_major_condition"))
        summary = f"📊 ARC Raiders Status: {active_count}/{data['total_maps']} maps have active conditions"
        if major_count > 0:
            summary += f" ({major_count} major conditions)"
        return [TextContent(type="text", text=summary)]
    else:
        return [TextContent(type="text", text=scraper.format_output(data))]


async def get_specific_map_condition(map_name: str, format_type: str = "text") -> List[TextContent]:
    """Get condition for a specific map."""
    data = scraper.scrape()
    
    if "error" in data:
        return [TextContent(type="text", text=f"❌ Error fetching map conditions: {data['error']}")]
    
    # Find the specific map
    map_data = None
    for m in data["maps"]:
        if m["name"].lower() == map_name.lower():
            map_data = m
            break
    
    if not map_data:
        return [TextContent(type="text", text=f"❌ Map '{map_name}' not found")]
    
    if format_type == "json":
        return [TextContent(type="text", text=json.dumps(map_data, indent=2))]
    else:
        # Format single map output
        output = [f"🗺️  {map_data['name']}"]
        output.append("-" * len(f"🗺️  {map_data['name']}"))
        
        if map_data['status'] == 'not_available':
            output.append("   ❌ Map not available yet")
        elif map_data['status'] == 'no_active_condition':
            output.append("   ⚪ No active condition")
        else:
            if map_data['current_condition']:
                major_indicator = " 🔥 MAJOR" if map_data['is_major_condition'] else ""
                output.append(f"   🟢 Current: {map_data['current_condition']}{major_indicator}")
            
            if map_data['next_condition']:
                next_info = map_data['next_condition']
                if map_data['next_time']:
                    next_info += f" at {map_data['next_time']}"
                output.append(f"   ⏳ Next: {next_info}")
        
        return [TextContent(type="text", text="\n".join(output))]


async def get_active_conditions_only(include_major_only: bool = False, format_type: str = "text") -> List[TextContent]:
    """Get only maps with active conditions."""
    data = scraper.scrape()
    
    if "error" in data:
        return [TextContent(type="text", text=f"❌ Error fetching map conditions: {data['error']}")]
    
    # Filter maps
    active_maps = []
    for m in data["maps"]:
        has_condition = m.get("current_condition") is not None
        if include_major_only:
            has_condition = has_condition and m.get("is_major_condition", False)
        
        if has_condition:
            active_maps.append(m)
    
    if not active_maps:
        filter_desc = "major conditions" if include_major_only else "active conditions"
        return [TextContent(type="text", text=f"⚪ No maps currently have {filter_desc}")]
    
    if format_type == "json":
        return [TextContent(type="text", text=json.dumps(active_maps, indent=2))]
    else:
        output = []
        filter_desc = "🔥 MAJOR CONDITIONS" if include_major_only else "🟢 ACTIVE CONDITIONS"
        output.append(f"{filter_desc} ({len(active_maps)} maps)")
        output.append("=" * 50)
        
        for map_data in active_maps:
            output.append(f"🗺️  {map_data['name']}")
            if map_data['current_condition']:
                major_indicator = " 🔥 MAJOR" if map_data['is_major_condition'] else ""
                output.append(f"   🟢 Current: {map_data['current_condition']}{major_indicator}")
            
            if map_data['next_condition']:
                next_info = map_data['next_condition']
                if map_data['next_time']:
                    next_info += f" at {map_data['next_time']}"
                output.append(f"   ⏳ Next: {next_info}")
            output.append("")
        
        return [TextContent(type="text", text="\n".join(output))]


async def get_next_conditions(format_type: str = "text") -> List[TextContent]:
    """Get upcoming conditions for all maps."""
    data = scraper.scrape()
    
    if "error" in data:
        return [TextContent(type="text", text=f"❌ Error fetching map conditions: {data['error']}")]
    
    # Filter maps with next conditions
    maps_with_next = [m for m in data["maps"] if m.get("next_condition")]
    
    if format_type == "json":
        return [TextContent(type="text", text=json.dumps(maps_with_next, indent=2))]
    else:
        if not maps_with_next:
            return [TextContent(type="text", text="⏳ No upcoming conditions scheduled")]
        
        output = []
        output.append(f"⏳ UPCOMING CONDITIONS ({len(maps_with_next)} maps)")
        output.append("=" * 50)
        
        # Sort by time if possible (basic sorting by time string)
        try:
            maps_with_next.sort(key=lambda x: x.get("next_time", ""))
        except:
            pass  # If sorting fails, just use original order
        
        for map_data in maps_with_next:
            next_info = map_data['next_condition']
            if map_data['next_time']:
                next_info += f" at {map_data['next_time']}"
            output.append(f"🗺️  {map_data['name']}: {next_info}")
        
        return [TextContent(type="text", text="\n".join(output))]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server(server) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="arc-raiders-conditions",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())