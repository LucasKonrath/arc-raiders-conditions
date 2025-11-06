#!/usr/bin/env python3
"""
Simple runner script for the ARC Raiders Map Conditions Scraper
"""

from arc_raiders_scraper import ARCRaidersScraper

def run_scraper():
    """Run the scraper and display results"""
    scraper = ARCRaidersScraper()
    data = scraper.scrape()
    print(scraper.format_output(data))

if __name__ == "__main__":
    run_scraper()