"""
Notion Web Scraper Module
Extracts bill/transaction data from Notion pages.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import json
import time
from typing import Dict, List, Optional, Tuple, Union
import streamlit as st
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionScraper:
    """Scrapes bill/transaction data from Notion pages."""
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        """
        Initialize the Notion scraper - SPEED OPTIMIZED.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Maximum wait time for page elements (reduced for speed)
        """
        self.headless = headless
        self.timeout = timeout
        self.ua = UserAgent()
        self.driver = None
        
    def _detect_environment(self):
        """Detect if running in Streamlit Cloud, Docker, or local environment."""
        # Check for Streamlit Cloud environment
        if hasattr(st, '__version__') and os.getenv('STREAMLIT_SHARING_URL'):
            return 'streamlit_cloud'
        
        # Check for Docker environment
        if os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER'):
            return 'docker'
        
        # Check for system Chrome/Chromium paths (Docker-like)
        if os.getenv('CHROME_BIN') and os.getenv('CHROMEDRIVER_PATH'):
            return 'docker'
        
        # Default to local environment
        return 'local'

    @st.cache_resource
    def _create_streamlit_driver(_self):
        """Create a cached Chrome driver for Streamlit Cloud (static method for caching)."""
        logger.info("🌐 Creating Streamlit Cloud compatible driver...")
        
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType
        
        # Streamlit Cloud optimized options - SPEED OPTIMIZED
        options = Options()
        options.add_argument("--headless=new")  # Use new headless mode for speed
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Don't load images for speed
        options.add_argument("--disable-javascript")  # Disable JS for faster loading
        options.add_argument("--window-size=1024,768")  # Smaller window for speed
        options.add_argument("--page-load-strategy=eager")  # Don't wait for all resources
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use Chromium type for better cloud compatibility
        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=options,
        )
        
        # Configure driver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(15)  # Reduced from 30 for speed
        driver.implicitly_wait(5)  # Reduced from 10 for speed
        
        logger.info("✅ Streamlit Cloud driver created successfully!")
        return driver

    def _create_docker_driver(self):
        """Create a Chrome driver for Docker environment - SPEED OPTIMIZED."""
        logger.info("🐳 Creating Docker compatible driver...")
        
        options = Options()
        
        # Set binary location for Docker
        chrome_bin = os.getenv('CHROME_BIN', '/usr/bin/chromium')
        if os.path.exists(chrome_bin):
            options.binary_location = chrome_bin
            logger.info(f"🔧 Using Chrome binary: {chrome_bin}")
        
        if self.headless:
            options.add_argument("--headless=new")  # Use new headless mode for speed
        
        # SPEED OPTIMIZED Chrome options for Docker
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Don't load images for speed
        options.add_argument("--disable-javascript")  # Disable JS for faster loading
        options.add_argument("--window-size=1024,768")  # Smaller window for speed
        options.add_argument("--page-load-strategy=eager")  # Don't wait for all resources
        options.add_argument(f"--user-agent={self.ua.random}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Try system chromedriver first
        chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
        
        if os.path.exists(chromedriver_path):
            logger.info(f"🔧 Using system ChromeDriver: {chromedriver_path}")
            from selenium.webdriver.chrome.service import Service
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            logger.info("🔧 Using webdriver-manager for Docker...")
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(15)  # Reduced from 30 for speed
        driver.implicitly_wait(5)  # Reduced from 10 for speed
        
        logger.info("✅ Docker driver created successfully!")
        return driver

    def _create_local_driver(self):
        """Create a Chrome driver for local development - SPEED OPTIMIZED."""
        logger.info("🖥️ Creating local development driver...")
        
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")  # Use new headless mode for speed
        
        # SPEED OPTIMIZED Chrome options for Local
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Don't load images for speed
        options.add_argument("--disable-javascript")  # Disable JS for faster loading
        options.add_argument("--window-size=1024,768")  # Smaller window for speed
        options.add_argument("--page-load-strategy=eager")  # Don't wait for all resources
        options.add_argument(f"--user-agent={self.ua.random}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Try webdriver-manager first for local
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("✅ Local driver with webdriver-manager created!")
        except Exception as e:
            logger.warning(f"webdriver-manager failed: {e}, trying system Chrome...")
            # Fallback to system Chrome
            driver = webdriver.Chrome(options=options)
            logger.info("✅ Local driver with system Chrome created!")
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(15)  # Reduced from 30 for speed
        driver.implicitly_wait(5)  # Reduced from 10 for speed
        
        return driver

    def setup_driver(self):
        """Setup Chrome WebDriver with environment-specific optimization."""
        env = self._detect_environment()
        logger.info(f"🔍 Detected environment: {env}")
        
        try:
            if env == 'streamlit_cloud':
                logger.info("🌐 Using Streamlit Cloud optimized setup...")
                self.driver = self._create_streamlit_driver()
                
            elif env == 'docker':
                logger.info("🐳 Using Docker optimized setup...")
                self.driver = self._create_docker_driver()
                
            else:  # local
                logger.info("🖥️ Using local development setup...")
                self.driver = self._create_local_driver()
            
            logger.info("✅ Chrome driver setup successful!")
            logger.info(f"✅ Browser version: {self.driver.capabilities.get('browserVersion', 'Unknown')}")
            logger.info(f"✅ ChromeDriver version: {self.driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"💥 CRITICAL: Failed to setup Chrome driver in {env} environment: {e}")
            logger.error(f"💥 Error type: {type(e).__name__}")
            logger.error(f"💥 This will cause Notion scraping to fail and return SAMPLE data!")
            import traceback
            logger.error(f"💥 Full traceback: {traceback.format_exc()}")
            
            # Environment-specific troubleshooting
            if env == 'streamlit_cloud':
                logger.error("🔧 Streamlit Cloud troubleshooting:")
                logger.error("  - Ensure webdriver-manager is in requirements.txt")
                logger.error("  - Check Streamlit Cloud resource limits")
                logger.error("  - Try deploying with fewer dependencies")
            elif env == 'docker':
                logger.error("🔧 Docker troubleshooting:")
                logger.error("  - Verify CHROME_BIN and CHROMEDRIVER_PATH are set")
                logger.error("  - Run: apt-get install chromium chromium-driver")
                logger.error("  - Check Dockerfile Chrome installation")
            else:
                logger.error("🔧 Local troubleshooting:")
                logger.error("  - Install Chrome: brew install google-chrome")
                logger.error("  - Or install Chromium: brew install chromium")
                logger.error("  - Ensure Chrome is in PATH")
            
            raise
    
    def scrape_notion_page(self, url: str) -> pd.DataFrame:
        """
        Scrape bill data from a Notion page.
        
        Args:
            url: URL of the Notion page
            
        Returns:
            pd.DataFrame: Extracted bill data
        """
        logger.info(f"🔍 DETAILED DEBUG: Starting to scrape Notion page: {url}")
        
        # Environment debugging
        import os
        import platform
        logger.info(f"🖥️ Environment: OS={platform.system()}, Python={platform.python_version()}")
        logger.info(f"🔧 Chrome bin: {os.getenv('CHROME_BIN', 'Not set')}")
        logger.info(f"🔧 ChromeDriver: {os.getenv('CHROMEDRIVER_PATH', 'Not set')}")
        
        try:
            # Try different scraping methods
            logger.info("📡 Attempting Selenium scraping...")
            df = self._scrape_with_selenium(url)
            logger.info(f"📡 Selenium result: {len(df) if not df.empty else 'EMPTY'} rows")
            
            if df.empty:
                logger.warning("⚠️ Selenium scraping failed, trying requests method")
                df = self._scrape_with_requests(url)
                logger.info(f"📡 Requests result: {len(df) if not df.empty else 'EMPTY'} rows")
            
            if df.empty:
                logger.error("❌ Both scraping methods failed, creating sample data")
                df = self._create_fallback_data()
                logger.info(f"📝 Fallback result: {len(df)} sample rows")
            else:
                logger.info(f"✅ Successfully scraped {len(df)} rows from Notion")
            
            result = self._process_scraped_data(df)
            logger.info(f"🔄 After processing: {len(result)} rows")
            return result
            
        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR scraping Notion page: {e}")
            logger.error(f"💥 Error type: {type(e).__name__}")
            import traceback
            logger.error(f"💥 Traceback: {traceback.format_exc()}")
            logger.info("📝 Creating fallback sample data due to critical error")
            return self._create_fallback_data()
    
    def _scrape_with_selenium(self, url: str) -> pd.DataFrame:
        """Scrape using Selenium WebDriver."""
        try:
            self.setup_driver()
            
            logger.info("Loading page with Selenium...")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Wait for content to be present
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Try to find table elements
            data_rows = []
            
            # Look for different table structures that Notion might use
            table_selectors = [
                'div[role="table"]',
                'table',
                '.notion-table-view',
                '.notion-database-view',
                '[data-block-id*="table"]',
                '.notion-collection-view'
            ]
            
            table_found = False
            
            for selector in table_selectors:
                try:
                    tables = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if tables:
                        logger.info(f"Found table with selector: {selector}")
                        data_rows = self._extract_table_data_selenium(tables[0])
                        table_found = True
                        break
                except Exception as e:
                    logger.debug(f"Failed with selector {selector}: {e}")
                    continue
            
            if not table_found:
                # Try to extract any structured data
                logger.info("No table found, trying to extract structured text data...")
                data_rows = self._extract_text_data_selenium()
            
            self.driver.quit()
            
            if data_rows:
                df = pd.DataFrame(data_rows)
                logger.info(f"Successfully extracted {len(df)} rows with Selenium")
                logger.info(f"Sample data: {data_rows[:3] if len(data_rows) >= 3 else data_rows}")
                return df
            else:
                logger.warning("No data extracted with Selenium")
                return pd.DataFrame()
                
        except Exception as e:
            if self.driver:
                self.driver.quit()
            logger.error(f"Selenium scraping failed: {e}")
            return pd.DataFrame()
    
    def _scrape_with_requests(self, url: str) -> pd.DataFrame:
        """Scrape using requests and BeautifulSoup (backup method)."""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            logger.info("Making request to Notion page...")
            response = requests.get(url, headers=headers, timeout=15)  # Reduced from 30 for speed
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for structured data in various formats
            data_rows = []
            
            # Try to find tables
            tables = soup.find_all(['table', 'div'], attrs={'role': 'table'})
            
            for table in tables:
                rows = self._extract_table_data_bs4(table)
                if rows:
                    data_rows.extend(rows)
            
            # If no tables found, try to extract structured text
            if not data_rows:
                data_rows = self._extract_text_data_bs4(soup)
            
            if data_rows:
                df = pd.DataFrame(data_rows)
                logger.info(f"Successfully extracted {len(df)} rows with requests")
                logger.info(f"Sample data: {data_rows[:3] if len(data_rows) >= 3 else data_rows}")
                return df
            else:
                logger.warning("No data extracted with requests")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Requests scraping failed: {e}")
            return pd.DataFrame()
    
    def _extract_table_data_selenium(self, table_element) -> List[Dict]:
        """Extract data from table element using Selenium."""
        data_rows = []
        
        try:
            # Try to find rows
            rows = table_element.find_elements(By.CSS_SELECTOR, 'tr, div[role="row"], .notion-table-row')
            
            headers = []
            
            for i, row in enumerate(rows):
                try:
                    # Get cells in the row
                    cells = row.find_elements(By.CSS_SELECTOR, 'td, th, div[role="cell"], .notion-table-cell')
                    
                    if not cells:
                        continue
                    
                    cell_texts = [cell.text.strip() for cell in cells]
                    
                    if i == 0 and not headers:
                        # First row might be headers
                        headers = cell_texts
                        if self._looks_like_headers(headers):
                            continue
                    
                    # Create row data
                    if headers and len(cell_texts) == len(headers):
                        row_data = dict(zip(headers, cell_texts))
                    else:
                        # Create generic column names
                        row_data = {f'col_{j}': text for j, text in enumerate(cell_texts)}
                    
                    if any(text for text in cell_texts if text):  # Skip empty rows
                        data_rows.append(row_data)
                        
                except Exception as e:
                    logger.debug(f"Error processing row {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
        
        return data_rows
    
    def _extract_text_data_selenium(self) -> List[Dict]:
        """Extract structured data from page text using Selenium."""
        data_rows = []
        
        try:
            # Get all text content
            body = self.driver.find_element(By.TAG_NAME, 'body')
            text_content = body.text
            
            # Parse structured text data
            lines = text_content.split('\n')
            
            current_date = None
            
            # Look for patterns that might indicate financial data
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a date header (like "2025/08/01:" or "08/01:")
                # First try full date format YYYY/MM/DD:
                full_date_match = re.match(r'^(\d{4}/\d{2}/\d{2})[:：]\s*$', line)
                if full_date_match:
                    current_date = full_date_match.group(1).replace('/', '-')
                    logger.info(f"Found full date section: {current_date}")
                    continue
                
                # Fallback to short date format MM/DD: (assume current year)
                short_date_match = re.match(r'^(\d{2}/\d{2})[:：]\s*$', line)
                if short_date_match:
                    current_year = str(datetime.now().year)
                    current_date = f"{current_year}-{short_date_match.group(1).replace('/', '-')}"
                    logger.info(f"Found short date section: {current_date}")
                    continue
                
                # Try to parse line as transaction data
                row_data = self._parse_transaction_line(line)
                if row_data:
                    # Add current date if not present
                    if row_data.get('date') is None and current_date:
                        row_data['date'] = current_date
                    elif row_data.get('date') is None:
                        # Use today's date as fallback
                        row_data['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                    
                    data_rows.append(row_data)
                    logger.debug(f"Parsed transaction: {row_data}")
                    
        except Exception as e:
            logger.error(f"Error extracting text data: {e}")
        
        return data_rows
    
    def _extract_table_data_bs4(self, table) -> List[Dict]:
        """Extract data from table using BeautifulSoup."""
        data_rows = []
        
        try:
            rows = table.find_all(['tr', 'div'], recursive=True)
            headers = []
            
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th', 'div'], recursive=False)
                
                if not cells:
                    continue
                
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                if i == 0 and not headers:
                    headers = cell_texts
                    if self._looks_like_headers(headers):
                        continue
                
                if headers and len(cell_texts) == len(headers):
                    row_data = dict(zip(headers, cell_texts))
                else:
                    row_data = {f'col_{j}': text for j, text in enumerate(cell_texts)}
                
                if any(text for text in cell_texts if text):
                    data_rows.append(row_data)
                    
        except Exception as e:
            logger.error(f"Error extracting BS4 table data: {e}")
        
        return data_rows
    
    def _extract_text_data_bs4(self, soup) -> List[Dict]:
        """Extract structured data from page text using BeautifulSoup."""
        data_rows = []
        
        try:
            # Get all text content
            text_content = soup.get_text()
            lines = text_content.split('\n')
            
            current_date = None
            current_year = "2024"  # Default year
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a date header (like "08/01:" or "08/02:")
                date_header_match = re.match(r'^(\d{2}/\d{2})[:：]\s*$', line)
                if date_header_match:
                    current_date = f"{current_year}-{date_header_match.group(1).replace('/', '-')}"
                    logger.info(f"Found date section: {current_date}")
                    continue
                
                row_data = self._parse_transaction_line(line)
                if row_data:
                    # Add current date if not present
                    if row_data.get('date') is None and current_date:
                        row_data['date'] = current_date
                    elif row_data.get('date') is None:
                        # Use today's date as fallback
                        row_data['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                    
                    data_rows.append(row_data)
                    logger.debug(f"Parsed transaction: {row_data}")
                    
        except Exception as e:
            logger.error(f"Error extracting BS4 text data: {e}")
        
        return data_rows
    
    def _parse_transaction_line(self, line: str) -> Optional[Dict]:
        """Parse a line of text that might contain transaction data."""
        try:
            line = line.strip()
            if not line:
                return None
            
            # Pattern for your specific format: "description: amount [T] category" 
            # Examples: "一家川菜：59 Food", "Fob Copy：30 T Utilities", "中餐：56 T Food"
            patterns = [
                # Numbered format with category: "1: description: amount [T] category"
                r'^\d+[:.：]\s*(.+?)[:：]\s*(\d+(?:\.\d+)?)\s*T?\s*([A-Za-z]+)\s*$',
                
                # Direct format with category: "description: amount [T] category"  
                r'^(.+?)[:：]\s*(\d+(?:\.\d+)?)\s*T?\s*([A-Za-z]+)\s*$',
                
                # Fallback: Numbered format without category: "1: description: amount T"
                r'^\d+[:.：]\s*(.+?)[:：]\s*(\d+(?:\.\d+)?)\s*T?\s*$',
                
                # Fallback: Direct format without category: "description: amount T"
                r'^(.+?)[:：]\s*(\d+(?:\.\d+)?)\s*T?\s*$',
                
                # Standard patterns for other formats
                r'(\d{1,2}[/-]\d{1,2}[/-]?\d{2,4})\s+[\$]?(\d+\.?\d*)\s+(.+)',
                r'(.+?)\s+[\$]?(\d+\.?\d*)\s+(\d{1,2}[/-]\d{1,2}[/-]?\d{2,4})',
                r'[\$]?(\d+\.?\d*)\s+(\d{1,2}[/-]\d{1,2}[/-]?\d{2,4})\s+(.+)',
            ]
            
            current_date = None  # Will be set from context (like "08/01:")
            
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    
                    if i <= 1:  # Your specific format with category
                        desc_val = groups[0].strip()
                        amount_val = float(groups[1])
                        category_val = groups[2].strip() if len(groups) > 2 else None
                        
                        # Skip if description looks like a date header
                        if re.match(r'^\d{2}/\d{2}', desc_val):
                            continue
                        
                        # Clean up description - remove extra spaces and clean formatting
                        desc_val = re.sub(r'\s+', ' ', desc_val).strip()
                            
                        return {
                            'description': desc_val,
                            'amount': amount_val,
                            'category': category_val,
                            'date': None  # Will be filled in by context
                        }
                    elif i <= 3:  # Your specific format without category (fallback)
                        desc_val = groups[0].strip()
                        amount_val = float(groups[1])
                        
                        # Skip if description looks like a date header
                        if re.match(r'^\d{2}/\d{2}', desc_val):
                            continue
                        
                        # Clean up description - remove extra spaces and clean formatting
                        desc_val = re.sub(r'\s+', ' ', desc_val).strip()
                            
                        return {
                            'description': desc_val,
                            'amount': amount_val,
                            'date': None  # Will be filled in by context
                        }
                    else:  # Standard patterns
                        # Try to identify which group is what
                        date_val = None
                        amount_val = None
                        desc_val = None
                        
                        for group in groups:
                            if re.match(r'\d{1,2}[/-]\d{1,2}[/-]?\d{2,4}', group):
                                date_val = group
                            elif re.match(r'^\d+\.?\d*$', group):
                                amount_val = float(group)
                            else:
                                desc_val = group
                        
                        if date_val and amount_val and desc_val:
                            return {
                                'date': date_val,
                                'amount': amount_val,
                                'description': desc_val
                            }
                        elif amount_val and desc_val:  # No date found
                            return {
                                'description': desc_val,
                                'amount': amount_val,
                                'date': None
                            }
                            
        except Exception as e:
            logger.debug(f"Error parsing line '{line}': {e}")
        
        return None
    
    def _looks_like_headers(self, texts: List[str]) -> bool:
        """Check if texts look like table headers."""
        header_keywords = ['date', 'amount', 'description', 'category', 'transaction', 'merchant', 'cost', 'expense']
        
        text_lower = [text.lower() for text in texts if text]
        
        return any(keyword in ' '.join(text_lower) for keyword in header_keywords)
    
    def _process_scraped_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean scraped data."""
        if df.empty:
            return df
        
        logger.info(f"Processing {len(df)} scraped rows...")
        
        # Try to identify and standardize columns
        df = self._standardize_columns(df)
        
        # Clean and validate data
        df = self._clean_scraped_data(df)
        
        logger.info(f"Processed data: {len(df)} rows, columns: {list(df.columns)}")
        
        return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names from scraped data."""
        # Create a mapping of possible column names to standard names
        column_mapping = {
            # Date columns
            'date': 'date',
            'transaction date': 'date',
            'trans date': 'date',
            'posting date': 'date',
            'when': 'date',
            'time': 'date',
            
            # Amount columns
            'amount': 'amount',
            'cost': 'amount',
            'price': 'amount',
            'total': 'amount',
            'expense': 'amount',
            'spent': 'amount',
            'money': 'amount',
            'value': 'amount',
            
            # Description columns
            'description': 'description',
            'desc': 'description',
            'merchant': 'description',
            'vendor': 'description',
            'store': 'description',
            'item': 'description',
            'what': 'description',
            'details': 'description',
            
            # Category columns
            'category': 'category',
            'cat': 'category',
            'kind': 'category',
            'group': 'category',
            
            # Account columns
            'account': 'account',
            'bank': 'account',
            'card': 'account',
            
            # Type columns
            'type': 'type',
            'transaction_type': 'type',
            'trans_type': 'type',
        }
        
        # Normalize column names (handle empty/None columns)
        normalized_columns = []
        for col in df.columns:
            if col is None or str(col).strip() == '':
                normalized_columns.append(f'unnamed_column_{len(normalized_columns)}')
            else:
                normalized_columns.append(str(col).lower().strip())
        
        df.columns = normalized_columns
        
        # Apply mapping and handle duplicates
        new_columns = {}
        used_names = set()
        
        for col in df.columns:
            mapped_col = column_mapping.get(col, col)
            
            # Handle duplicate column names
            if mapped_col in used_names:
                counter = 1
                original_mapped_col = mapped_col
                while mapped_col in used_names:
                    mapped_col = f"{original_mapped_col}_{counter}"
                    counter += 1
            
            new_columns[col] = mapped_col
            used_names.add(mapped_col)
        
        df = df.rename(columns=new_columns)
        
        # Remove duplicate columns (keep first occurrence)
        df = df.loc[:, ~df.columns.duplicated()]
        
        logger.info(f"Standardized columns: {list(df.columns)}")
        
        return df
    
    def _clean_scraped_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate scraped data."""
        try:
            logger.info(f"Cleaning data with {len(df)} rows and columns: {list(df.columns)}")
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Handle multiple amount columns (if any)
            amount_columns = [col for col in df.columns if 'amount' in col.lower()]
            if amount_columns:
                # Use first amount column as primary
                primary_amount_col = amount_columns[0]
                if primary_amount_col != 'amount':
                    df = df.rename(columns={primary_amount_col: 'amount'})
                
                # Clean amount column
                df['amount'] = df['amount'].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', '')
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                
                # Remove rows with invalid amounts
                valid_amount_mask = ~df['amount'].isna()
                df = df[valid_amount_mask]
                
                if len(df) > 0:
                    df['amount'] = df['amount'].abs()  # Take absolute value
                    logger.info(f"Cleaned amount column: {len(df)} valid amounts")
            
            # Handle multiple date columns (if any)
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            if date_columns:
                # Use first date column as primary
                primary_date_col = date_columns[0]
                if primary_date_col != 'date':
                    df = df.rename(columns={primary_date_col: 'date'})
                
                # Clean date column - use explicit format to avoid timestamp issues
                df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%Y-%m-%d')
                
                # Remove rows with invalid dates
                valid_date_mask = ~df['date'].isna()
                df = df[valid_date_mask]
                logger.info(f"Cleaned date column: {len(df)} valid dates")
            
            # Handle multiple description columns (if any)
            desc_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['description', 'desc', 'merchant', 'vendor'])]
            if desc_columns:
                # Use first description column as primary
                primary_desc_col = desc_columns[0]
                if primary_desc_col != 'description':
                    df = df.rename(columns={primary_desc_col: 'description'})
                
                # Clean description column
                df['description'] = df['description'].astype(str).str.strip()
                df = df[df['description'] != '']
                df = df[df['description'] != 'nan']
                logger.info(f"Cleaned description column: {len(df)} valid descriptions")
            
            # Handle category columns
            category_columns = [col for col in df.columns if 'category' in col.lower()]
            needs_categorization = True
            
            if category_columns:
                # Use first category column as primary
                primary_cat_col = category_columns[0]
                if primary_cat_col != 'category':
                    df = df.rename(columns={primary_cat_col: 'category'})
                
                # Check if existing categories are meaningful (not all 'Other' or empty)
                if 'category' in df.columns:
                    unique_categories = df['category'].dropna().unique()
                    meaningful_categories = [cat for cat in unique_categories if cat not in ['Other', '', 'other', 'OTHER']]
                    if len(meaningful_categories) > 0:
                        needs_categorization = False
                        logger.info(f"Found existing meaningful categories: {meaningful_categories}")
            
            # Apply intelligent auto-categorization if needed
            if needs_categorization and 'description' in df.columns:
                from .data_processor import DataProcessor
                processor = DataProcessor()
                df['category'] = processor.auto_categorize(df['description'])
                logger.info("Applied intelligent auto-categorization to scraped data")
            elif needs_categorization:
                df['category'] = 'Other'
            
            # Add missing columns with defaults
            if 'account' not in df.columns:
                df['account'] = 'Main Account'
            
            if 'type' not in df.columns:
                df['type'] = 'Expense'
            
            # Remove any remaining invalid rows
            df = df.reset_index(drop=True)
            
            # Final validation
            required_cols = ['date', 'amount', 'description']
            missing_required = [col for col in required_cols if col not in df.columns]
            if missing_required:
                logger.warning(f"Missing required columns: {missing_required}")
                # Try to create missing columns from available data
                if 'date' not in df.columns and len(df) > 0:
                    df['date'] = pd.Timestamp.now()
                if 'amount' not in df.columns and len(df) > 0:
                    df['amount'] = 0.0
                if 'description' not in df.columns and len(df) > 0:
                    df['description'] = 'Unknown Transaction'
            
            logger.info(f"Final cleaned data: {len(df)} rows, columns: {list(df.columns)}")
            
        except Exception as e:
            logger.error(f"Error cleaning scraped data: {e}")
            # Return empty dataframe if cleaning fails completely
            if len(df) == 0:
                return pd.DataFrame()
        
        return df
    
    def _create_fallback_data(self) -> pd.DataFrame:
        """Create fallback sample data when scraping fails."""
        logger.warning("❌ Creating fallback sample data - actual scraping failed...")
        
        # Import the DataProcessor to use its sample data creation
        from .data_processor import DataProcessor
        processor = DataProcessor()
        sample_df = processor.create_sample_data(100)  # Create 100 sample transactions
        
        # CRITICAL: Mark this as sample data so it's not confused with real Notion data
        sample_df['_data_source'] = 'sample_fallback'
        sample_df['_is_sample_data'] = True
        
        logger.error("🚨 RETURNING SAMPLE DATA - NOT REAL NOTION DATA!")
        return sample_df
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()


class NotionDataExtractor:
    """High-level interface for extracting data from Notion pages."""
    
    def __init__(self):
        self.scraper = NotionScraper()
    
    def extract_bill_data(self, notion_url: str) -> pd.DataFrame:
        """
        Extract bill data from a Notion page.
        
        Args:
            notion_url: URL of the Notion page containing bill data
            
        Returns:
            pd.DataFrame: Processed bill data ready for analysis
        """
        try:
            # Extract data from Notion
            df = self.scraper.scrape_notion_page(notion_url)
            
            if df.empty:
                logger.warning("No data extracted from Notion page")
                return pd.DataFrame()
            
            # Further process with DataProcessor
            from .data_processor import DataProcessor
            processor = DataProcessor()
            processed_df = processor.process_dataframe(df)
            
            logger.info(f"Successfully extracted and processed {len(processed_df)} transactions")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Error extracting bill data: {e}")
            return pd.DataFrame()
        finally:
            self.scraper.close()
    
    def save_extracted_data(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Save extracted data to a file.
        
        Args:
            df: DataFrame to save
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            str: Path to saved file or None if saving failed
        """
        try:
            import os
            
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"notion_bills_{timestamp}.csv"
            
            filepath = f"data/{filename}"
            df.to_csv(filepath, index=False)
            
            logger.info(f"Saved extracted data to {filepath}")
            return filepath
            
        except Exception as e:
            logger.warning(f"Could not save extracted data: {e}")
            return None