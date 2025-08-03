#!/usr/bin/env python3
"""
Test script to validate the multiple Chrome driver strategies.
"""

import sys
import os
sys.path.append('.')

from src.notion_scraper import NotionScraper
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_driver_strategies():
    """Test all driver setup strategies."""
    print("🧪 Testing Chrome Driver Setup Strategies...")
    print("=" * 60)
    
    scraper = NotionScraper()
    
    try:
        print("\n🌐 Testing Streamlit-compatible setup...")
        if hasattr(scraper, 'get_streamlit_driver'):
            driver = scraper.get_streamlit_driver()
            if driver:
                print("✅ Streamlit driver setup successful!")
                print(f"Browser: {driver.capabilities.get('browserName', 'Unknown')}")
                print(f"Version: {driver.capabilities.get('browserVersion', 'Unknown')}")
                driver.quit()
            else:
                print("❌ Streamlit driver setup failed")
        else:
            print("⚠️ Streamlit driver method not found")
            
    except Exception as e:
        print(f"❌ Streamlit setup failed: {e}")
    
    try:
        print("\n🖥️ Testing multi-strategy setup...")
        scraper.setup_driver()
        if scraper.driver:
            print("✅ Multi-strategy setup successful!")
            print(f"Browser: {scraper.driver.capabilities.get('browserName', 'Unknown')}")
            print(f"Version: {scraper.driver.capabilities.get('browserVersion', 'Unknown')}")
            scraper.driver.quit()
        else:
            print("❌ Multi-strategy setup failed")
            
    except Exception as e:
        print(f"❌ Multi-strategy setup failed: {e}")
    
    print("\n🎯 Testing complete!")

if __name__ == "__main__":
    test_driver_strategies()