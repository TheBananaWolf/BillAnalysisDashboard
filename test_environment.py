#!/usr/bin/env python3
"""
Environment Detection and Testing Script
Tests the Chrome WebDriver setup in different environments.
"""

import sys
import os
sys.path.append('.')

from src.notion_scraper import NotionScraper
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_environment_detection():
    """Test environment detection and Chrome setup."""
    print("🧪 Testing Environment Detection and Chrome Setup")
    print("=" * 60)
    
    scraper = NotionScraper()
    
    # Test environment detection
    env = scraper._detect_environment()
    print(f"🔍 Detected environment: {env}")
    
    # Show environment details
    print("\n📊 Environment Details:")
    print(f"  - Streamlit available: {'Yes' if 'streamlit' in sys.modules else 'No'}")
    print(f"  - Docker container: {'Yes' if os.path.exists('/.dockerenv') else 'No'}")
    print(f"  - CHROME_BIN: {os.getenv('CHROME_BIN', 'Not set')}")
    print(f"  - CHROMEDRIVER_PATH: {os.getenv('CHROMEDRIVER_PATH', 'Not set')}")
    print(f"  - STREAMLIT_SHARING_URL: {os.getenv('STREAMLIT_SHARING_URL', 'Not set')}")
    
    # Test Chrome driver setup
    print(f"\n🚀 Testing Chrome WebDriver setup for {env} environment...")
    
    try:
        scraper.setup_driver()
        
        if scraper.driver:
            print("✅ Chrome WebDriver setup successful!")
            print(f"  - Browser: {scraper.driver.capabilities.get('browserName', 'Unknown')}")
            print(f"  - Version: {scraper.driver.capabilities.get('browserVersion', 'Unknown')}")
            print(f"  - ChromeDriver: {scraper.driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')}")
            
            # Test a simple page load
            print("\n🌐 Testing page load...")
            try:
                scraper.driver.get("https://httpbin.org/user-agent")
                page_title = scraper.driver.title
                print(f"✅ Page loaded successfully! Title: {page_title}")
            except Exception as load_error:
                print(f"❌ Page load failed: {load_error}")
            
            # Cleanup
            scraper.driver.quit()
            print("✅ WebDriver closed successfully")
            
        else:
            print("❌ Chrome WebDriver setup failed - driver is None")
            
    except Exception as e:
        print(f"❌ Chrome WebDriver setup failed: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    print("\n" + "=" * 60)
    print("🎯 Test complete!")

def test_streamlit_compatibility():
    """Test Streamlit-specific compatibility."""
    print("\n🌐 Testing Streamlit Compatibility")
    print("-" * 40)
    
    try:
        import streamlit as st
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType
        from selenium.webdriver.chrome.service import Service
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ All Streamlit-required imports successful")
        
        # Test webdriver-manager with Chromium
        print("🔧 Testing webdriver-manager with Chromium...")
        try:
            manager = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM)
            driver_path = manager.install()
            print(f"✅ ChromeDriver downloaded to: {driver_path}")
        except Exception as wdm_error:
            print(f"❌ webdriver-manager failed: {wdm_error}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")

def show_recommendations():
    """Show environment-specific recommendations."""
    print("\n💡 Deployment Recommendations")
    print("-" * 40)
    
    print("🌐 For Streamlit Cloud:")
    print("  1. Ensure requirements.txt includes:")
    print("     - webdriver-manager>=3.8.0")
    print("     - selenium>=4.0.0")
    print("  2. Don't set CHROME_BIN or CHROMEDRIVER_PATH")
    print("  3. Let webdriver-manager handle Chrome automatically")
    
    print("\n🐳 For Docker:")
    print("  1. Set environment variables:")
    print("     - CHROME_BIN=/usr/bin/chromium")
    print("     - CHROMEDRIVER_PATH=/usr/bin/chromedriver")
    print("  2. Install in Dockerfile:")
    print("     - RUN apt-get install chromium chromium-driver")
    
    print("\n🖥️ For Local Development:")
    print("  1. Install Chrome or Chromium")
    print("  2. Let webdriver-manager handle ChromeDriver")
    print("  3. No environment variables needed")

if __name__ == "__main__":
    test_environment_detection()
    test_streamlit_compatibility()
    show_recommendations()