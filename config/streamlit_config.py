"""
Streamlit Cloud specific configuration for the Bill Analysis application.
"""

import os

def configure_streamlit_cloud():
    """Configure environment variables for Streamlit Cloud deployment."""
    
    # Set Streamlit Cloud indicator
    os.environ['STREAMLIT_SHARING_URL'] = os.getenv('STREAMLIT_SHARING_URL', 'https://billanalysis.streamlit.app')
    
    # Streamlit configuration
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Chrome/Selenium configuration for cloud
    # Note: Don't set CHROME_BIN or CHROMEDRIVER_PATH for Streamlit Cloud
    # Let webdriver-manager handle everything automatically
    
    print("✅ Streamlit Cloud configuration applied")

def get_streamlit_requirements():
    """Get additional requirements needed for Streamlit Cloud."""
    return [
        "webdriver-manager>=3.8.0",
        "selenium>=4.0.0",
        "streamlit>=1.20.0"
    ]

def validate_streamlit_environment():
    """Validate that the environment is properly configured for Streamlit Cloud."""
    issues = []
    
    # Check if running in Streamlit
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError:
        issues.append("❌ Streamlit not available")
    
    # Check webdriver-manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType
        print("✅ webdriver-manager imported successfully")
    except ImportError:
        issues.append("❌ webdriver-manager not available")
    
    # Check selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium imported successfully")
    except ImportError:
        issues.append("❌ Selenium not available")
    
    if issues:
        print("\n🚨 Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n🎉 Streamlit Cloud environment is properly configured!")
        return True

if __name__ == "__main__":
    configure_streamlit_cloud()
    validate_streamlit_environment()