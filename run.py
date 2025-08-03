#!/usr/bin/env python3
"""
Quick start script for Bill Analysis System
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required. Please upgrade your Python installation.")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["data", "exports"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting Bill Analysis System...")
    print("📱 The application will open in your default browser")
    print("🌐 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main function"""
    print("💰 Bill Analysis System - Quick Start")
    print("=" * 50)
    
    check_python_version()
    install_requirements()
    create_directories()
    run_application()

if __name__ == "__main__":
    main()