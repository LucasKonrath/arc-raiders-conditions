#!/usr/bin/env python3
"""
ARC Raiders Map Conditions Scraper

This script scrapes the current active map conditions from https://arc-raiders.dev
and displays them in a clean, readable format.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Dict, List, Optional


class ARCRaidersScraper:
    def __init__(self):
        self.url = "https://arc-raiders.dev"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_page(self) -> Optional[BeautifulSoup]:
        """Fetch and parse the main page"""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_map_conditions(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract map conditions from the parsed HTML"""
        map_conditions = []
        
        # Look for map sections - they typically have headings like "Dam Battlegrounds", "Buried City", etc.
        map_sections = soup.find_all(['h2', 'h3'], string=re.compile(r'(Dam Battlegrounds|Buried City|The Spaceport|The Blue Gate|Practice Range|Stella Montis)', re.IGNORECASE))
        
        for section in map_sections:
            map_name = section.get_text().strip()
            map_data = {
                'name': map_name,
                'current_condition': None,
                'is_major_condition': False,
                'next_condition': None,
                'next_time': None,
                'status': 'available'
            }
            
            # Find the parent container for this map - go up several levels to get the full section
            container = section
            for _ in range(5):  # Go up the DOM tree to find the main container
                if container.parent:
                    container = container.parent
                else:
                    break
            
            # Get all text from the container
            container_text = container.get_text()
            
            # Parse the text more directly
            lines = [line.strip() for line in container_text.split('\n') if line.strip()]
            
            current_idx = -1
            next_idx = -1
            
            # Find indices of key elements
            for i, line in enumerate(lines):
                if 'CURRENT' in line.upper():
                    current_idx = i
                elif 'NEXT CONDITION' in line.upper():
                    next_idx = i
            
            # Extract current condition
            if current_idx >= 0 and current_idx + 1 < len(lines):
                potential_condition = lines[current_idx + 1]
                # Skip "MAJOR CONDITION" line
                if 'MAJOR CONDITION' in potential_condition.upper():
                    map_data['is_major_condition'] = True
                    if current_idx + 2 < len(lines):
                        potential_condition = lines[current_idx + 2]
                
                # Clean condition names
                if potential_condition and not any(skip in potential_condition.upper() for skip in ['NEXT CONDITION', 'CURRENT', 'MAJOR CONDITION', 'AM', 'PM']):
                    map_data['current_condition'] = potential_condition.strip()
            
            # Extract next condition and time
            if next_idx >= 0:
                # Look for condition name and time in the following lines
                for i in range(next_idx + 1, min(next_idx + 4, len(lines))):
                    if i < len(lines):
                        line = lines[i].strip()
                        if ':' in line and ('AM' in line.upper() or 'PM' in line.upper()):
                            map_data['next_time'] = line
                        elif line and not any(skip in line.upper() for skip in ['NEXT CONDITION', 'CURRENT', 'MAJOR CONDITION', 'AM', 'PM']):
                            if not map_data['next_condition']:  # Only set if not already set
                                map_data['next_condition'] = line
            
            # Check for special statuses
            if 'NO ACTIVE CONDITION' in container_text.upper():
                map_data['status'] = 'no_active_condition'
            elif 'NOT AVAILABLE' in container_text.upper():
                map_data['status'] = 'not_available'
            
            # Check for major condition marker
            if 'MAJOR CONDITION' in container_text.upper():
                map_data['is_major_condition'] = True
            
            map_conditions.append(map_data)
        
        return map_conditions
    
    def _has_condition_info(self, element) -> bool:
        """Check if an element contains condition information"""
        if not element:
            return False
        text = element.get_text().lower()
        return any(keyword in text for keyword in ['current', 'next condition', 'major condition', 'no active', 'not available'])
    
    def get_current_time_info(self, soup: BeautifulSoup) -> Dict:
        """Extract current time and timezone information"""
        time_info = {
            'current_time': None,
            'timezone': None
        }
        
        # Look for current time display
        time_elements = soup.find_all(string=re.compile(r'\d{1,2}:\d{2}:\d{2}'))
        for elem in time_elements:
            if 'PM' in elem or 'AM' in elem:
                time_info['current_time'] = elem.strip()
                break
        
        # Look for timezone
        tz_elements = soup.find_all(string=re.compile(r'America/|UTC|GMT'))
        if tz_elements:
            time_info['timezone'] = tz_elements[0].strip()
        
        return time_info
    
    def scrape(self) -> Dict:
        """Main scraping method"""
        print("Fetching ARC Raiders map conditions...")
        
        soup = self.fetch_page()
        if not soup:
            return {'error': 'Failed to fetch page'}
        
        time_info = self.get_current_time_info(soup)
        map_conditions = self.extract_map_conditions(soup)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'time_info': time_info,
            'maps': map_conditions,
            'total_maps': len(map_conditions)
        }
    
    def format_output(self, data: Dict) -> str:
        """Format the scraped data for display"""
        if 'error' in data:
            return f"❌ {data['error']}"
        
        output = []
        output.append("🎮 ARC RAIDERS MAP CONDITIONS")
        output.append("=" * 50)
        
        if data['time_info']['current_time']:
            output.append(f"⏰ Current Time: {data['time_info']['current_time']}")
        if data['time_info']['timezone']:
            output.append(f"🌍 Timezone: {data['time_info']['timezone']}")
        output.append(f"📊 Total Maps: {data['total_maps']}")
        output.append("")
        
        for map_data in data['maps']:
            output.append(f"🗺️  {map_data['name']}")
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
            
            output.append("")
        
        output.append(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)


def main():
    """Main function to run the scraper"""
    scraper = ARCRaidersScraper()
    data = scraper.scrape()
    
    # Display formatted output
    print(scraper.format_output(data))
    
    # Optionally save to JSON file
    output_file = "arc_raiders_conditions.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Data saved to {output_file}")
    except Exception as e:
        print(f"\n❌ Error saving to file: {e}")


if __name__ == "__main__":
    main()