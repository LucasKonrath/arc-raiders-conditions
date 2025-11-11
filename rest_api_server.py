#!/usr/bin/env python3
"""
ARC Raiders Map Conditions REST API Server

This creates a REST API that can be consumed by ChatGPT and other AI assistants
that support function calling with HTTP endpoints.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import logging

# Import our existing scraper
from arc_raiders_scraper import ARCRaidersScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arc-raiders-api")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web-based AI tools

# Global scraper instance
scraper = ARCRaidersScraper()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "arc-raiders-conditions-api",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/conditions', methods=['GET'])
def get_map_conditions():
    """
    Get current active map conditions for all ARC Raiders maps
    
    Query Parameters:
    - format: json, text, or summary (default: json)
    """
    try:
        format_type = request.args.get('format', 'json')
        
        # Get the data
        data = scraper.scrape()
        
        if "error" in data:
            return jsonify({"error": data["error"]}), 500
        
        if format_type == "text":
            return jsonify({
                "success": True,
                "format": "text",
                "data": scraper.format_output(data)
            })
        elif format_type == "summary":
            active_count = sum(1 for m in data["maps"] if m.get("current_condition"))
            major_count = sum(1 for m in data["maps"] if m.get("is_major_condition"))
            summary = f"📊 ARC Raiders Status: {active_count}/{data['total_maps']} maps have active conditions"
            if major_count > 0:
                summary += f" ({major_count} major conditions)"
            
            return jsonify({
                "success": True,
                "format": "summary",
                "data": summary
            })
        else:  # json format
            return jsonify({
                "success": True,
                "format": "json",
                "data": data
            })
    
    except Exception as e:
        logger.error(f"Error in get_map_conditions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/conditions/<map_name>', methods=['GET'])
def get_specific_map_condition(map_name):
    """
    Get condition details for a specific map
    
    Path Parameters:
    - map_name: Name of the map
    
    Query Parameters:
    - format: json or text (default: json)
    """
    try:
        format_type = request.args.get('format', 'json')
        
        # Get the data
        data = scraper.scrape()
        
        if "error" in data:
            return jsonify({"error": data["error"]}), 500
        
        # Find the specific map
        map_data = None
        for m in data["maps"]:
            if m["name"].lower().replace(" ", "-") == map_name.lower() or m["name"].lower() == map_name.lower():
                map_data = m
                break
        
        if not map_data:
            return jsonify({"error": f"Map '{map_name}' not found"}), 404
        
        if format_type == "text":
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
            
            return jsonify({
                "success": True,
                "format": "text",
                "data": "\n".join(output)
            })
        else:  # json format
            return jsonify({
                "success": True,
                "format": "json",
                "data": map_data
            })
    
    except Exception as e:
        logger.error(f"Error in get_specific_map_condition: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/conditions/active', methods=['GET'])
def get_active_conditions_only():
    """
    Get only maps that currently have active conditions
    
    Query Parameters:
    - major_only: true/false - if true, only return maps with major conditions (default: false)
    - format: json, text, or summary (default: json)
    """
    try:
        include_major_only = request.args.get('major_only', 'false').lower() == 'true'
        format_type = request.args.get('format', 'json')
        
        # Get the data
        data = scraper.scrape()
        
        if "error" in data:
            return jsonify({"error": data["error"]}), 500
        
        # Filter maps
        active_maps = []
        for m in data["maps"]:
            has_condition = m.get("current_condition") is not None
            if include_major_only:
                has_condition = has_condition and m.get("is_major_condition", False)
            
            if has_condition:
                active_maps.append(m)
        
        if format_type == "summary":
            filter_desc = "major conditions" if include_major_only else "active conditions"
            if not active_maps:
                summary = f"⚪ No maps currently have {filter_desc}"
            else:
                summary = f"🟢 {len(active_maps)} maps have {filter_desc}"
            
            return jsonify({
                "success": True,
                "format": "summary",
                "data": summary
            })
        elif format_type == "text":
            if not active_maps:
                filter_desc = "major conditions" if include_major_only else "active conditions"
                return jsonify({
                    "success": True,
                    "format": "text",
                    "data": f"⚪ No maps currently have {filter_desc}"
                })
            
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
            
            return jsonify({
                "success": True,
                "format": "text",
                "data": "\n".join(output)
            })
        else:  # json format
            return jsonify({
                "success": True,
                "format": "json",
                "data": {
                    "active_maps": active_maps,
                    "total_active": len(active_maps),
                    "filter": "major_only" if include_major_only else "all_active"
                }
            })
    
    except Exception as e:
        logger.error(f"Error in get_active_conditions_only: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/conditions/upcoming', methods=['GET'])
def get_next_conditions():
    """
    Get upcoming conditions and their timing for all maps
    
    Query Parameters:
    - format: json or text (default: json)
    """
    try:
        format_type = request.args.get('format', 'json')
        
        # Get the data
        data = scraper.scrape()
        
        if "error" in data:
            return jsonify({"error": data["error"]}), 500
        
        # Filter maps with next conditions
        maps_with_next = [m for m in data["maps"] if m.get("next_condition")]
        
        if format_type == "text":
            if not maps_with_next:
                return jsonify({
                    "success": True,
                    "format": "text",
                    "data": "⏳ No upcoming conditions scheduled"
                })
            
            output = []
            output.append(f"⏳ UPCOMING CONDITIONS ({len(maps_with_next)} maps)")
            output.append("=" * 50)
            
            # Sort by time if possible
            try:
                maps_with_next.sort(key=lambda x: x.get("next_time", ""))
            except:
                pass
            
            for map_data in maps_with_next:
                next_info = map_data['next_condition']
                if map_data['next_time']:
                    next_info += f" at {map_data['next_time']}"
                output.append(f"🗺️  {map_data['name']}: {next_info}")
            
            return jsonify({
                "success": True,
                "format": "text",
                "data": "\n".join(output)
            })
        else:  # json format
            return jsonify({
                "success": True,
                "format": "json",
                "data": {
                    "upcoming_conditions": maps_with_next,
                    "total_upcoming": len(maps_with_next)
                }
            })
    
    except Exception as e:
        logger.error(f"Error in get_next_conditions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/docs', methods=['GET'])
def get_api_docs():
    """API documentation"""
    docs = {
        "service": "ARC Raiders Map Conditions API",
        "version": "1.0.0",
        "description": "REST API for real-time ARC Raiders map conditions",
        "endpoints": {
            "GET /health": "Health check",
            "GET /api/v1/conditions": "Get all map conditions",
            "GET /api/v1/conditions/{map_name}": "Get specific map condition",
            "GET /api/v1/conditions/active": "Get only active conditions",
            "GET /api/v1/conditions/upcoming": "Get upcoming conditions"
        },
        "maps": [
            "dam-battlegrounds",
            "buried-city", 
            "the-spaceport",
            "the-blue-gate",
            "practice-range",
            "stella-montis"
        ],
        "formats": ["json", "text", "summary"],
        "examples": {
            "all_conditions": "/api/v1/conditions?format=text",
            "specific_map": "/api/v1/conditions/dam-battlegrounds",
            "active_only": "/api/v1/conditions/active?format=summary",
            "major_only": "/api/v1/conditions/active?major_only=true",
            "upcoming": "/api/v1/conditions/upcoming"
        }
    }
    
    return jsonify(docs)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    
    print("🎮 Starting ARC Raiders Conditions REST API Server")
    print("📋 Available endpoints:")
    print("   GET /health - Health check")
    print("   GET /api/v1/conditions - Get all map conditions") 
    print("   GET /api/v1/conditions/{map_name} - Get specific map")
    print("   GET /api/v1/conditions/active - Get active conditions only")
    print("   GET /api/v1/conditions/upcoming - Get upcoming conditions")
    print("   GET /api/v1/docs - API documentation")
    print("")
    print(f"🌐 Server will run on: http://0.0.0.0:{port}")
    print(f"📖 API docs: http://0.0.0.0:{port}/api/v1/docs")
    print("")
    
    app.run(host='0.0.0.0', port=port, debug=False)