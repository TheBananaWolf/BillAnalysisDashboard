"""
Data Processing Module
Handles loading, cleaning, and preprocessing of financial data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import io
from typing import Union, Dict, List, Optional
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data loading and preprocessing for bill analysis."""
    
    def __init__(self):
        self.required_columns = ['date', 'amount', 'description']
        self.optional_columns = ['category', 'account', 'type']
    
    def load_data(self, file_data) -> pd.DataFrame:
        """
        Load data from various file formats.
        
        Args:
            file_data: Uploaded file data from Streamlit
            
        Returns:
            pd.DataFrame: Processed dataframe
        """
        filename = file_data.name
        
        if filename.endswith('.csv'):
            df = pd.read_csv(file_data)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_data)
        elif filename.endswith('.json'):
            df = pd.read_json(file_data)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        return self.process_dataframe(df)
    
    def load_from_notion_url(self, notion_url: str) -> pd.DataFrame:
        """
        Load data from a Notion page URL.
        
        Args:
            notion_url: URL of the Notion page containing bill data
            
        Returns:
            pd.DataFrame: Processed dataframe
        """
        logger.info(f"Loading data from Notion URL: {notion_url}")
        
        try:
            from .notion_scraper import NotionDataExtractor
            
            extractor = NotionDataExtractor()
            df = extractor.extract_bill_data(notion_url)
            
            if df.empty:
                logger.warning("❌ No data extracted from Notion page - using sample data")
                df = self.create_sample_data()
                # Add a marker to identify sample data
                df['_data_source'] = 'sample'
            elif '_is_sample_data' in df.columns and df['_is_sample_data'].iloc[0]:
                # Data was already marked as sample by the scraper
                logger.error("🚨 Notion scraper returned SAMPLE DATA (not real data)")
                logger.error("🔍 Check debug logs to see why scraping failed")
                # Keep the existing _data_source from scraper (likely 'sample_fallback')
            else:
                logger.info(f"✅ Successfully extracted {len(df)} REAL transactions from Notion")
                # Add a marker to identify real data
                df['_data_source'] = 'notion'
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading from Notion URL: {e}")
            logger.info("Creating sample data as fallback")
            df = self.create_sample_data()
            df['_data_source'] = 'sample_fallback'
            return df
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and clean the dataframe.
        
        Args:
            df: Raw dataframe
            
        Returns:
            pd.DataFrame: Cleaned and processed dataframe
        """
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Map common column variations
        column_mapping = {
            'transaction_date': 'date',
            'trans_date': 'date',
            'posting_date': 'date',
            'transaction_amount': 'amount',
            'debit': 'amount',
            'credit': 'amount',
            'transaction_description': 'description',
            'desc': 'description',
            'merchant': 'description',
            'payee': 'description',
            'cat': 'category',
            'expense_category': 'category',
            'account_name': 'account',
            'bank_account': 'account'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Process date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Process amount column
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Take absolute value for amounts (assuming all are expenses)
        df['amount'] = df['amount'].abs()
        
        # Clean description
        df['description'] = df['description'].astype(str).str.strip()
        
        # Add category if not present
        if 'category' not in df.columns:
            df['category'] = self.auto_categorize(df['description'])
        
        # Add account if not present
        if 'account' not in df.columns:
            df['account'] = 'Main Account'
        
        # Add transaction type if not present
        if 'type' not in df.columns:
            df['type'] = 'Expense'
        
        # Remove rows with invalid data
        df = df.dropna(subset=['date', 'amount'])
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def auto_categorize(self, descriptions: pd.Series) -> pd.Series:
        """
        Automatically categorize transactions based on description.
        Optimized version with improved pattern matching and caching.
        
        Args:
            descriptions: Series of transaction descriptions
            
        Returns:
            pd.Series: Categorized transactions
        """
        # Use vectorized operations for better performance
        descriptions_lower = descriptions.astype(str).str.lower().str.strip()
        categories = pd.Series(['Other'] * len(descriptions), index=descriptions.index)
        
        # Optimized category patterns with priority ordering (most specific first)
        # Enhanced patterns based on user's actual Notion categories: Food, Utilities, Grocery, Bank
        category_patterns = {
            'Food': [
                # Specific brand matches (highest priority)
                r'\bmcdonald', r'\bsubway\b', r'\bstarbucks', r'\bkfc\b', r'\bpizza hut',
                r'\bdomino', r'\btaco bell', r'\bburger king', r'\bwendy', 
                # Delivery services
                r'uber eats', r'doordash', r'grubhub', r'postmates', r'food panda',
                # Restaurant types
                r'restaurant', r'cafe', r'coffee shop', r'diner', r'bistro', r'grill',
                r'bar', r'pub', r'kitchen', r'bakery', r'pizzeria',
                # Food categories
                r'\bfood\b', r'\bpizza\b', r'\bburger', r'\bsushi\b', r'\btaco',
                r'dining', r'lunch', r'dinner', r'breakfast', r'takeout', r'delivery',
                # Beverages
                r'\bbeer\b', r'\bwine\b', r'alcohol', r'\bdrink', r'beverage', r'\bsoda\b',
                r'\bjuice\b', r'\btea\b', r'\bmilk\b', r'\bwater\b', r'\bice\b',
                r'mocha', r'latte', r'espresso', r'cappuccino', r'smoothie',
                # Snacks and desserts
                r'\bsnack', r'\bbread\b', r'\bcake\b', r'\bcookie', r'\bcandy',
                # Chinese/Asian terms  
                r'川菜', r'中餐', r'餐厅', r'饭店', r'咖啡', r'茶', r'酒', r'啤酒',
                r'食物', r'饮料', r'小吃', r'面包', r'蛋糕', r'奶茶', r'火锅', r'烧烤',
                # User-specific patterns
                r'\bfob\b', r'fob copy'
            ],
            'Grocery': [
                # Major grocery chains (specific matches)
                r'\bwalmart', r'\btarget\b', r'\bcostco', r'whole foods', r'\bsafeway',
                r'\bkroger', r'\bpublix', r'trader joe', r'\baldi', r'\bwegman',
                r'\bstop & shop', r'\bfood lion', r'\bharris teeter',
                # Generic grocery terms
                r'grocery', r'supermarket', r'\bmarket\b', r'\bmart\b', 
                r'food store', r'groceries',
                # Product categories
                r'vegetables', r'\bfruits\b', r'\bmeat\b', r'\bdairy\b', r'produce',
                r'\bbread\b', r'\bmilk\b', r'\beggs\b', r'\bcheese\b',
                # User-specific patterns
                r't and t', r'\btnt\b', r'\bt&t\b'
            ],
            'Utilities': [
                # Utility services
                r'\belectric', r'electricity', r'\bwater\b', r'\bsewer\b', r'gas bill',
                r'\binternet\b', r'\bcable\b', r'\bphone\b', r'\bmobile\b', 
                r'\butility\b', r'\bbill\b', r'\bservice\b', r'maintenance', r'repair',
                r'\bheating\b', r'\bcooling\b', r'\bhvac\b', r'\bwifi\b',
                # Service providers
                r'\batt\b', r'verizon', r'comcast', r'\bxfinity', r'\bspectrum',
                r'\bt-mobile', r'sprint', r'\bge\b', r'\bpge\b',
                # Home & furniture (user categorizes these as utilities)
                r'\bikea\b', r'\bchair\b', r'\bdesk\b', r'\btable\b', r'\bbed\b', 
                r'\bsofa\b', r'furniture', r'\bhome depot', r'\blowes\b',
                r'\bhome\b', r'\bhouse\b', r'apartment', r'\bdecor\b', r'\blamp\b', 
                r'\bshelf\b', r'cabinet', r'dresser', r'mattress', r'\bpillow\b', 
                r'\bblanket\b', r'\brug\b', r'\bmirror\b'
            ],
            'Bank': [
                # Banking terms
                r'\bbank\b', r'\batm\b', r'\bfee\b', r'\bcharge\b', r'\binterest\b', 
                r'\bloan\b', r'credit card', r'\binsurance\b', r'investment', 
                r'\btransfer\b', r'\bpayment\b', r'financial', r'\bsavings\b', 
                r'\bcredit\b', r'\bdebt\b', r'\bmortgage\b',
                # Bank names
                r'chase', r'\bboa\b', r'bank of america', r'\bwells fargo', r'\bciti',
                r'\busaa\b', r'\bpnc\b', r'\btd bank', r'\bus bank',
                # User-specific patterns
                r'paypower', r'\bppp\b', r'\bppe\b',
                # Financial services
                r'\bvisa\b', r'mastercard', r'\bamex\b', r'paypal', r'venmo', 
                r'\bzelle\b', r'\bcashapp\b'
            ],
            # Additional optimized categories
            'Transportation': [
                # Gas stations
                r'\bshell\b', r'\bexxon\b', r'\bchevron\b', r'\bbp\b', r'\bmobil\b',
                r'\btexaco\b', r'\bsinoco\b', r'\barco\b', r'\b76\b',
                # Transportation services
                r'\buber\b', r'\blyft\b', r'\btaxi\b', r'\bmetro\b', r'\bbus\b', 
                r'\btrain\b', r'\bsubway\b', r'\bart\b', r'\bmta\b',
                # Vehicle related
                r'\bgas\b', r'\bfuel\b', r'parking', r'\btoll\b', r'car wash', 
                r'\bauto\b', r'\bgarage\b', r'\brepair\b', r'\boil change\b'
            ],
            'Shopping': [
                # Major retailers
                r'\bamazon\b', r'\bebay\b', r'\bbest buy\b', r'apple store', 
                r'\bmacy', r'\bnordstrom', r'\bkohl', r'\bjcp', r'\btjx\b',
                # Shopping categories
                r'\bmall\b', r'\bshop\b', r'\bretail\b', r'\bstore\b',
                r'clothing', r'\bshoes\b', r'fashion', r'electronics',
                r'\bphone\b', r'\btablet\b', r'\blaptop\b'
            ],
            'Entertainment': [
                # Streaming and media
                r'\bnetflix\b', r'\bspotify\b', r'\bhulu\b', r'\bdisney\b', 
                r'\bamazon prime', r'\byoutube\b', r'\bapple music',
                # Entertainment venues
                r'\bmovie\b', r'\btheater\b', r'\bcinema\b', r'\bconcert\b', 
                r'\bshow\b', r'\bclub\b', r'\bbar\b', r'\bgym\b',
                # Gaming and hobbies
                r'\bgame\b', r'\bsteam\b', r'\bplaystation\b', r'\bxbox\b', 
                r'entertainment', r'\bmusic\b', r'\bsport\b'
            ]
        }
        
        # Vectorized pattern matching for better performance
        for category, patterns in category_patterns.items():
            # Combine all patterns for this category into a single regex
            combined_pattern = '|'.join(f'({pattern})' for pattern in patterns)
            
            # Apply pattern to all descriptions at once
            mask = descriptions_lower.str.contains(combined_pattern, case=False, na=False, regex=True)
            
            # Update categories where pattern matches and category is still 'Other'
            categories.loc[mask & (categories == 'Other')] = category
        
        return categories
    
    def create_sample_data(self, num_transactions: int = 500) -> pd.DataFrame:
        """
        Create sample financial data for testing.
        
        Args:
            num_transactions: Number of transactions to generate
            
        Returns:
            pd.DataFrame: Sample financial data
        """
        np.random.seed(42)
        
        # Date range: last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        dates = pd.date_range(start=start_date, end=end_date, periods=num_transactions)
        
        # Categories and their typical amounts (based on user's actual categories)
        categories_data = {
            'Food': {'mean': 25, 'std': 15, 'min': 5, 'max': 150},
            'Grocery': {'mean': 75, 'std': 30, 'min': 20, 'max': 200},
            'Utilities': {'mean': 120, 'std': 30, 'min': 80, 'max': 450},  # Higher max for furniture
            'Bank': {'mean': 50, 'std': 40, 'min': 5, 'max': 300},
            'Transportation': {'mean': 35, 'std': 20, 'min': 10, 'max': 100},
            'Shopping': {'mean': 85, 'std': 50, 'min': 15, 'max': 500},
            'Entertainment': {'mean': 40, 'std': 25, 'min': 10, 'max': 150},
            'Other': {'mean': 50, 'std': 40, 'min': 5, 'max': 300}
        }
        
        # Sample descriptions for each category (based on user's actual data)
        descriptions_data = {
            'Food': [
                '一家川菜', 'Fob Copy', 'Beer', 'mocha', '中餐', 'Soda', 'Ice',
                'McDonald\'s #1234', 'Starbucks Coffee', 'Pizza Palace',
                'Local Restaurant', 'Subway Sandwiches', 'Coffee Shop',
                'Burger King', 'Chinese Takeout', 'Lunch Cafe'
            ],
            'Grocery': [
                't and t', 'Walmart Supercenter', 'Target Store', 'Whole Foods Market',
                'Local Grocery Store', 'Costco Wholesale', 'Safeway',
                'Trader Joe\'s', 'Kroger', 'Publix'
            ],
            'Utilities': [
                'Ikea', 'Chair', 'Desk', 'Electric Company', 'Water Department', 
                'Internet Provider', 'Cable TV', 'Mobile Phone', 'Gas Company',
                'Utility Payment', 'Phone Bill', 'Internet Bill', 'Furniture Store',
                'Home Improvement', 'Appliance Store'
            ],
            'Bank': [
                'PayPower', 'PPP', 'Bank Fee', 'ATM Withdrawal', 'Service Charge',
                'Transfer Fee', 'Account Maintenance', 'Wire Transfer',
                'Credit Card Payment', 'Loan Payment', 'Investment Transfer'
            ],
            'Transportation': [
                'Shell Gas Station', 'Uber Trip', 'Metro Transit',
                'Parking Meter', 'Car Wash', 'Exxon Mobile',
                'Lyft Ride', 'Bus Fare', 'Toll Plaza'
            ],
            'Shopping': [
                'Amazon Purchase', 'Best Buy Electronics', 'Clothing Store',
                'Home Depot', 'Apple Store', 'Online Shopping',
                'Department Store', 'Shoe Store', 'Electronics Shop'
            ],
            'Entertainment': [
                'Movie Theater', 'Netflix Subscription', 'Spotify Premium',
                'Concert Tickets', 'Sports Bar', 'Gaming Store',
                'Streaming Service', 'Music Store', 'Entertainment Venue'
            ],
            'Other': [
                'Miscellaneous', 'Unknown Charge', 'Other Expense',
                'Fee Payment', 'Service Fee', 'General Purchase'
            ]
        }
        
        transactions = []
        
        for i, date in enumerate(dates):
            # Choose category (weighted towards more common expenses)
            # Weights: Food, Grocery, Utilities, Bank, Transportation, Shopping, Entertainment, Other
            category_weights = [0.25, 0.2, 0.15, 0.1, 0.1, 0.1, 0.05, 0.05]
            category = np.random.choice(list(categories_data.keys()), p=category_weights)
            
            # Generate amount based on category
            cat_data = categories_data[category]
            amount = np.random.normal(cat_data['mean'], cat_data['std'])
            amount = max(cat_data['min'], min(cat_data['max'], amount))
            amount = round(amount, 2)
            
            # Choose description
            description = np.random.choice(descriptions_data[category])
            
            transactions.append({
                'date': date,
                'amount': amount,
                'description': description,
                'category': category,
                'account': 'Main Checking',
                'type': 'Expense'
            })
        
        df = pd.DataFrame(transactions)
        return df.sort_values('date').reset_index(drop=True)
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate data quality and return quality metrics.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dict: Data quality metrics
        """
        quality_report = {
            'total_rows': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'date_range': {
                'min': df['date'].min(),
                'max': df['date'].max(),
                'span_days': (df['date'].max() - df['date'].min()).days
            },
            'amount_stats': {
                'min': df['amount'].min(),
                'max': df['amount'].max(),
                'mean': df['amount'].mean(),
                'median': df['amount'].median(),
                'negative_values': (df['amount'] < 0).sum()
            },
            'categories': {
                'unique_count': df['category'].nunique(),
                'most_common': df['category'].value_counts().head().to_dict()
            }
        }
        
        return quality_report