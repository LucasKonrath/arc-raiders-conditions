# ARC Raiders Map Conditions Scraper

A Python script that scrapes the current active map conditions from [arc-raiders.dev](https://arc-raiders.dev) and displays them in a clean, readable format.

## Features

- 🎮 Scrapes real-time map conditions for all ARC Raiders maps
- 🗺️ Displays current conditions, next conditions, and timing
- 🔥 Identifies major conditions
- 💾 Saves data to JSON file for further processing
- ⏰ Shows current time and timezone information
- 🚀 Easy to use and extend

## Maps Tracked

- Dam Battlegrounds
- Buried City
- The Spaceport
- The Blue Gate
- Practice Range
- Stella Montis

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install requests beautifulsoup4 lxml
```

Or if you're using the virtual environment that was set up:

```bash
# The virtual environment is already configured with the required packages
```

## Usage

### Basic Usage

Run the scraper directly:

```bash
python arc_raiders_scraper.py
```

Or use the simple runner:

```bash
python run_scraper.py
```

### Sample Output

```
🎮 ARC RAIDERS MAP CONDITIONS
==================================================
⏰ Current Time: 12:55:32 PM
🌍 Timezone: America/Sao_Paulo
📊 Total Maps: 6

🗺️  Dam Battlegrounds
---------------------
   🟢 Current: HARVESTER
   ⏳ Next: HUSK GRAVEYARD at 1:00 PM

🗺️  Buried City
---------------
   🟢 Current: NIGHT RAID 🔥 MAJOR
   ⏳ Next: LUSH BLOOMS at 2:00 PM

🗺️  The Spaceport
-----------------
   🟢 Current: HARVESTER
   ⏳ Next: NIGHT RAID at 1:00 PM

🗺️  The Blue Gate
-----------------
   🟢 Current: HUSK GRAVEYARD
   ⏳ Next: LUSH BLOOMS at 3:00 PM

🗺️  Practice Range
------------------
   ⚪ No active condition

🗺️  Stella Montis
-----------------
   ❌ Map not available yet

🕒 Last updated: 2025-11-06 13:42:26
```

### JSON Output

The scraper also saves the data to `arc_raiders_conditions.json` with the following structure:

```json
{
  "timestamp": "2025-11-06T13:42:26.271347",
  "time_info": {
    "current_time": "12:55:32 PM",
    "timezone": "America/Sao_Paulo"
  },
  "maps": [
    {
      "name": "Dam Battlegrounds",
      "current_condition": "HARVESTER",
      "is_major_condition": false,
      "next_condition": "HUSK GRAVEYARD",
      "next_time": "1:00 PM",
      "status": "available"
    }
    // ... more maps
  ],
  "total_maps": 6
}
```

## Understanding the Output

### Condition Types
The scraper identifies various condition types such as:
- **HARVESTER** - Resource gathering focused conditions
- **NIGHT RAID** - Combat focused conditions
- **HUSK GRAVEYARD** - Special enemy encounters
- **LUSH BLOOMS** - Environmental conditions

### Status Indicators
- 🟢 **Current** - Active condition right now
- ⏳ **Next** - Upcoming condition with time
- 🔥 **MAJOR** - Major condition (more significant impact)
- ⚪ **No active condition** - Map has no current conditions
- ❌ **Map not available yet** - Map is not accessible

## Code Structure

- `ARCRaidersScraper` - Main scraper class
- `fetch_page()` - Downloads and parses the web page
- `extract_map_conditions()` - Parses HTML to extract map data
- `get_current_time_info()` - Extracts time and timezone info
- `format_output()` - Creates human-readable output
- `scrape()` - Main orchestration method

## Customization

You can easily extend the scraper by:

1. Modifying the `format_output()` method for different display formats
2. Adding new parsing logic in `extract_map_conditions()`
3. Implementing additional data export formats
4. Adding scheduling/automation features

## Error Handling

The scraper includes robust error handling for:
- Network connection issues
- HTML parsing problems
- Missing or changed website structure
- File I/O errors

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser (faster than default)
- Standard library modules: `json`, `re`, `datetime`, `typing`

## Notes

- The scraper respects the website's structure and uses appropriate headers
- Times are displayed as shown on the website (adjusting to your timezone)
- The script includes a notice that map condition data may sometimes be inaccurate as per the website's disclaimer
- Data is saved with timestamps for tracking changes over time

## Troubleshooting

If you encounter issues:

1. Check your internet connection
2. Verify the website is accessible: https://arc-raiders.dev
3. Ensure all dependencies are installed
4. Check if the website structure has changed (the scraper may need updates)

## License

This is a simple scraping tool for personal use. Please respect the terms of service of the arc-raiders.dev website.