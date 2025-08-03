"""
Bill Analysis Module
Core analysis functionality for financial data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import calendar

class BillAnalyzer:
    """Main analyzer class for financial data analysis."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with financial data.
        
        Args:
            df: DataFrame containing financial transactions
        """
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['month'] = self.df['date'].dt.to_period('M')
        self.df['year'] = self.df['date'].dt.year
        self.df['day_of_week'] = self.df['date'].dt.day_name()
        self.df['week'] = self.df['date'].dt.to_period('W')
        
    def get_monthly_spending(self) -> pd.DataFrame:
        """Get monthly spending summary."""
        monthly = self.df.groupby('month').agg({
            'amount': ['sum', 'mean', 'count'],
            'category': 'nunique'
        }).round(2)
        
        monthly.columns = ['total_amount', 'avg_amount', 'transaction_count', 'category_count']
        monthly = monthly.reset_index()
        monthly['month'] = monthly['month'].astype(str)
        
        return monthly
    
    def get_category_summary(self) -> pd.DataFrame:
        """Get spending summary by category."""
        category_summary = self.df.groupby('category').agg({
            'amount': ['sum', 'mean', 'count', 'std']
        }).round(2)
        
        category_summary.columns = ['amount', 'avg_amount', 'count', 'std_amount']
        category_summary = category_summary.reset_index()
        
        # Calculate percentage
        total_amount = self.df['amount'].sum()
        category_summary['percentage'] = (category_summary['amount'] / total_amount * 100).round(1)
        
        # Sort by total amount
        category_summary = category_summary.sort_values('amount', ascending=False)
        
        return category_summary
    
    def get_weekly_patterns(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Analyze spending patterns by day of week."""
        if df is None:
            df = self.df
        else:
            # Make a copy and ensure required columns exist
            df = df.copy()
            if 'day_of_week' not in df.columns:
                df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
            
        # Define day order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        weekly_pattern = df.groupby('day_of_week').agg({
            'amount': ['mean', 'sum', 'count']
        }).round(2)
        
        weekly_pattern.columns = ['avg_amount', 'total_amount', 'transaction_count']
        weekly_pattern = weekly_pattern.reset_index()
        
        # Reorder by day of week
        weekly_pattern['day_order'] = weekly_pattern['day_of_week'].map(
            {day: i for i, day in enumerate(day_order)}
        )
        weekly_pattern = weekly_pattern.sort_values('day_order').drop('day_order', axis=1)
        
        return weekly_pattern
    
    def get_spending_trends(self) -> go.Figure:
        """Create spending trends visualization."""
        monthly_data = self.get_monthly_spending()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Monthly Total Spending', 'Monthly Transaction Count'),
            vertical_spacing=0.1
        )
        
        # Total spending trend
        fig.add_trace(
            go.Scatter(
                x=monthly_data['month'],
                y=monthly_data['total_amount'],
                mode='lines+markers',
                name='Total Spending',
                line=dict(color='#1f77b4', width=3)
            ),
            row=1, col=1
        )
        
        # Transaction count trend
        fig.add_trace(
            go.Scatter(
                x=monthly_data['month'],
                y=monthly_data['transaction_count'],
                mode='lines+markers',
                name='Transaction Count',
                line=dict(color='#ff7f0e', width=3)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='Spending Trends Over Time',
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Month", row=2, col=1)
        fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        
        return fig
    
    def get_category_trends(self) -> go.Figure:
        """Create category trends over time."""
        # Monthly spending by category
        category_monthly = self.df.groupby(['month', 'category'])['amount'].sum().reset_index()
        category_monthly['month'] = category_monthly['month'].astype(str)
        
        fig = px.line(
            category_monthly,
            x='month',
            y='amount',
            color='category',
            title='Category Spending Trends Over Time',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            height=500
        )
        
        return fig
    
    def compare_categories(self, categories: List[str]) -> go.Figure:
        """Compare selected categories."""
        filtered_df = self.df[self.df['category'].isin(categories)]
        
        # Monthly comparison
        comparison_data = filtered_df.groupby(['month', 'category'])['amount'].sum().reset_index()
        comparison_data['month'] = comparison_data['month'].astype(str)
        
        fig = px.bar(
            comparison_data,
            x='month',
            y='amount',
            color='category',
            title=f'Category Comparison: {", ".join(categories)}',
            barmode='group'
        )
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            height=500
        )
        
        return fig
    
    def get_seasonal_analysis(self) -> pd.DataFrame:
        """Analyze seasonal spending patterns."""
        # Add season column
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        self.df['season'] = self.df['date'].dt.month.map(get_season)
        
        seasonal_data = self.df.groupby('season').agg({
            'amount': ['mean', 'sum', 'count']
        }).round(2)
        
        seasonal_data.columns = ['avg_amount', 'total_amount', 'transaction_count']
        seasonal_data = seasonal_data.reset_index()
        
        # Order seasons
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        seasonal_data['season_order'] = seasonal_data['season'].map(
            {season: i for i, season in enumerate(season_order)}
        )
        seasonal_data = seasonal_data.sort_values('season_order').drop('season_order', axis=1)
        
        return seasonal_data
    
    def get_yearly_comparison(self) -> pd.DataFrame:
        """Compare spending across years."""
        if self.df['year'].nunique() < 2:
            return pd.DataFrame()
        
        yearly_monthly = self.df.groupby([self.df['date'].dt.year, self.df['date'].dt.month])['amount'].sum().reset_index()
        yearly_monthly['month'] = yearly_monthly['date'].apply(lambda x: calendar.month_abbr[x])
        yearly_monthly = yearly_monthly.rename(columns={'date': 'year'})
        
        return yearly_monthly
    
    def calculate_growth_rates(self) -> pd.DataFrame:
        """Calculate month-over-month and year-over-year growth rates."""
        monthly_data = self.get_monthly_spending()
        
        if len(monthly_data) < 2:
            return pd.DataFrame()
        
        # Convert month back to datetime for calculations
        monthly_data['month_date'] = pd.to_datetime(monthly_data['month'])
        monthly_data = monthly_data.sort_values('month_date')
        
        # Calculate month-over-month growth
        monthly_data['mom_growth'] = monthly_data['total_amount'].pct_change() * 100
        
        # Calculate year-over-year growth if we have enough data
        if len(monthly_data) >= 12:
            monthly_data['yoy_growth'] = monthly_data['total_amount'].pct_change(periods=12) * 100
        
        growth_summary = monthly_data[['month', 'total_amount', 'mom_growth']].copy()
        
        if 'yoy_growth' in monthly_data.columns:
            growth_summary['yoy_growth'] = monthly_data['yoy_growth']
        
        return growth_summary.dropna()
    
    def detect_anomalies(self) -> pd.DataFrame:
        """Detect unusual spending patterns."""
        # Calculate z-scores for amounts
        self.df['amount_zscore'] = np.abs(
            (self.df['amount'] - self.df['amount'].mean()) / self.df['amount'].std()
        )
        
        # Define anomalies as transactions with z-score > 2
        anomalies = self.df[self.df['amount_zscore'] > 2].copy()
        anomalies = anomalies.sort_values('amount_zscore', ascending=False)
        
        return anomalies[['date', 'description', 'amount', 'category', 'amount_zscore']]
    
    def get_top_merchants(self, n: int = 10) -> pd.DataFrame:
        """Get top merchants by spending."""
        merchant_spending = self.df.groupby('description').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        merchant_spending.columns = ['total_spent', 'transaction_count', 'avg_amount']
        merchant_spending = merchant_spending.reset_index()
        merchant_spending = merchant_spending.sort_values('total_spent', ascending=False)
        
        return merchant_spending.head(n)
    
    def calculate_savings_potential(self) -> Dict[str, float]:
        """Calculate potential savings by category."""
        category_stats = self.get_category_summary()
        
        # Assume 10-20% savings potential for discretionary categories
        discretionary_categories = ['Food', 'Entertainment', 'Shopping']
        
        savings_potential = {}
        total_potential = 0
        
        for _, row in category_stats.iterrows():
            category = row['category']
            amount = row['amount']
            
            if category in discretionary_categories:
                potential = amount * 0.15  # 15% potential savings
            else:
                potential = amount * 0.05  # 5% potential savings
            
            savings_potential[category] = round(potential, 2)
            total_potential += potential
        
        savings_potential['Total'] = round(total_potential, 2)
        return savings_potential
    
    def generate_report(self, report_type: str) -> pd.DataFrame:
        """Generate various types of reports."""
        if report_type == "Monthly Summary":
            return self.get_monthly_spending()
        elif report_type == "Category Analysis":
            return self.get_category_summary()
        elif report_type == "Yearly Report":
            yearly_data = self.df.groupby('year').agg({
                'amount': ['sum', 'mean', 'count'],
                'category': 'nunique'
            }).round(2)
            yearly_data.columns = ['total_amount', 'avg_amount', 'transaction_count', 'category_count']
            return yearly_data.reset_index()
        elif report_type == "Custom Analysis":
            # Comprehensive analysis
            summary_stats = {
                'Total Spending': [self.df['amount'].sum()],
                'Average Transaction': [self.df['amount'].mean()],
                'Transaction Count': [len(self.df)],
                'Date Range': [f"{self.df['date'].min().strftime('%Y-%m-%d')} to {self.df['date'].max().strftime('%Y-%m-%d')}"],
                'Top Category': [self.df.groupby('category')['amount'].sum().idxmax()],
                'Top Merchant': [self.df.groupby('description')['amount'].sum().idxmax()]
            }
            return pd.DataFrame(summary_stats)
        else:
            return pd.DataFrame()