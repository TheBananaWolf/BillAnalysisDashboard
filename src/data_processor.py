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
                logger.warning("No data extracted from Notion page, creating sample data")
                df = self.create_sample_data()
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading from Notion URL: {e}")
            logger.info("Creating sample data as fallback")
            return self.create_sample_data()
    
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
        
        Args:
            descriptions: Series of transaction descriptions
            
        Returns:
            pd.Series: Categorized transactions
        """
        categories = []
        
        # Define category patterns based on user's actual Notion categories
        # User's categories: Food, Utilities, Grocery, Bank
        category_patterns = {
            'Food': [
                r'restaurant', r'cafe', r'coffee', r'food', r'pizza', r'burger',
                r'mcdonald', r'subway', r'starbucks', r'dining', r'lunch', r'dinner',
                r'breakfast', r'takeout', r'delivery', r'uber eats', r'doordash',
                r'grubhub', r'diner', r'bistro', r'kitchen', r'grill', r'bar', r'pub',
                r'beer', r'wine', r'alcohol', r'drink', r'beverage', r'soda', r'juice',
                r'tea', r'milk', r'water', r'ice', r'snack', r'bread', r'cake',
                r'mocha', r'latte', r'espresso', r'cappuccino',
                # Chinese terms  
                r'川菜', r'中餐', r'餐厅', r'饭店', r'咖啡', r'茶', r'酒', r'啤酒',
                r'食物', r'饮料', r'小吃', r'面包', r'蛋糕', r'奶茶', r'火锅', r'烧烤',
                # Specific items from user data
                r'fob', r'fob copy'
            ],
            'Grocery': [
                r'grocery', r'supermarket', r'walmart', r'target', r'costco',
                r'whole foods', r'safeway', r'kroger', r'publix', r'trader joe',
                r'market', r'mart', r'store', r'vegetables', r'fruits', r'meat',
                r'dairy', r'groceries', r'food store',
                # Specific items from user data
                r't and t', r'tnt'
            ],
            'Utilities': [
                r'electric', r'electricity', r'water', r'sewer', r'gas bill',
                r'internet', r'cable', r'phone', r'mobile', r'utility', r'bill',
                r'service', r'maintenance', r'repair',
                # Home & furniture items (user categorizes these as utilities)
                r'ikea', r'chair', r'desk', r'table', r'bed', r'sofa', r'furniture',
                r'home', r'house', r'apartment', r'decor', r'lamp', r'shelf',
                r'cabinet', r'dresser', r'mattress', r'pillow', r'blanket'
            ],
            'Bank': [
                r'bank', r'atm', r'fee', r'charge', r'interest', r'loan',
                r'credit card', r'insurance', r'investment', r'transfer', r'payment',
                r'paypower', r'ppp', r'financial', r'savings', r'credit', r'debt'
            ],
            # Additional categories for other transactions
            'Transportation': [
                r'gas', r'fuel', r'shell', r'exxon', r'chevron', r'bp',
                r'uber', r'lyft', r'taxi', r'metro', r'bus', r'train',
                r'parking', r'toll', r'car wash', r'auto'
            ],
            'Shopping': [
                r'amazon', r'ebay', r'mall', r'shop', r'retail',
                r'clothing', r'shoes', r'fashion', r'electronics', r'best buy',
                r'apple store', r'home depot', r'lowes'
            ],
            'Entertainment': [
                r'movie', r'theater', r'cinema', r'netflix', r'spotify',
                r'game', r'entertainment', r'music', r'concert', r'show',
                r'club'
            ]
        }
        
        for description in descriptions:
            description_lower = str(description).lower()
            category = 'Other'
            
            for cat, patterns in category_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, description_lower):
                        category = cat
                        break
                if category != 'Other':
                    break
            
            categories.append(category)
        
        return pd.Series(categories)
    
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