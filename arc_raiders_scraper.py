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
        
        # Get all text content - it comes as a single flattened line
        page_text = soup.get_text()
        
        # Map names to look for
        map_names = [
            "Dam Battlegrounds",
            "Buried City", 
            "The Spaceport",
            "The Blue Gate",
            "Practice Range",
            "Stella Montis"
        ]
        
        for map_name in map_names:
            map_data = {
                'name': map_name,
                'current_condition': None,
                'is_major_condition': False,
                'next_condition': None,
                'next_time': None,
                'status': 'available'
            }
            
            # Create pattern to find the map section
            # Look for the map name followed by content until the next map name
            other_maps = [name for name in map_names if name != map_name]
            next_map_pattern = "|".join(re.escape(name) for name in other_maps)
            
            map_pattern = rf'{re.escape(map_name)}\s*(.*?)(?={next_map_pattern}|Data based on UTC|$)'
            match = re.search(map_pattern, page_text, re.IGNORECASE | re.DOTALL)
            
            if match:
                section_text = match.group(1).strip()
                
                # Look for CURRENT condition with regex
                current_match = re.search(r'CURRENT\s+([A-Z\s]+?)(?:\s+MAJOR CONDITION|\s+Next Condition|\s+$)', section_text, re.IGNORECASE)
                if current_match:
                    condition = current_match.group(1).strip()
                    # Clean up the condition name (remove extra spaces)
                    condition = re.sub(r'\s+', ' ', condition)
                    map_data['current_condition'] = condition
                
                # Check for MAJOR CONDITION
                if re.search(r'MAJOR CONDITION', section_text, re.IGNORECASE):
                    map_data['is_major_condition'] = True
                
                # Look for Next Condition
                next_match = re.search(r'Next Condition\s+([A-Z\s]+?)\s+(\d{1,2}:\d{2}\s+[AP]M)', section_text, re.IGNORECASE)
                if next_match:
                    next_condition = re.sub(r'\s+', ' ', next_match.group(1).strip())
                    next_time = next_match.group(2).strip()
                    map_data['next_condition'] = next_condition
                    map_data['next_time'] = next_time
                
                # Check for special statuses
                if re.search(r'No active condition', section_text, re.IGNORECASE):
                    map_data['status'] = 'no_active_condition'
                elif re.search(r'Map not available', section_text, re.IGNORECASE):
                    map_data['status'] = 'not_available'
            
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