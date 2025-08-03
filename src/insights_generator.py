"""
Insights Generator Module
Generates AI-powered insights and recommendations for financial data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import calendar

class InsightsGenerator:
    """Generates insights and recommendations from financial data."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize insights generator with financial data.
        
        Args:
            df: DataFrame containing financial transactions
        """
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['month'] = self.df['date'].dt.to_period('M')
        self.df['day_of_week'] = self.df['date'].dt.day_name()
        self.df['hour'] = self.df['date'].dt.hour
        
    def generate_all_insights(self) -> Dict[str, List[str]]:
        """Generate comprehensive insights across all categories."""
        insights = {
            'spending_patterns': self.analyze_spending_patterns(),
            'category_insights': self.analyze_category_behavior(),
            'temporal_insights': self.analyze_temporal_patterns(),
            'anomaly_insights': self.detect_unusual_behavior(),
            'savings_opportunities': self.identify_savings_opportunities(),
            'financial_health': self.assess_financial_health()
        }
        
        return insights
    
    def analyze_spending_patterns(self) -> List[str]:
        """Analyze overall spending patterns."""
        insights = []
        
        # Total and average spending
        total_spending = self.df['amount'].sum()
        avg_transaction = self.df['amount'].mean()
        median_transaction = self.df['amount'].median()
        
        insights.append(f"Your total spending is ${total_spending:,.2f} across {len(self.df)} transactions.")
        insights.append(f"Your average transaction is ${avg_transaction:.2f}, with a median of ${median_transaction:.2f}.")
        
        # Transaction frequency
        days_span = (self.df['date'].max() - self.df['date'].min()).days
        if days_span > 0:
            avg_transactions_per_day = len(self.df) / days_span
            insights.append(f"You make approximately {avg_transactions_per_day:.1f} transactions per day.")
        
        # Spending distribution
        if avg_transaction > median_transaction * 1.5:
            insights.append("You have a few high-value transactions that significantly impact your average spending.")
        
        # Monthly spending trend
        monthly_spending = self.df.groupby('month')['amount'].sum()
        if len(monthly_spending) > 1:
            if monthly_spending.is_monotonic_increasing:
                insights.append("Your monthly spending shows a consistent upward trend.")
            elif monthly_spending.is_monotonic_decreasing:
                insights.append("Your monthly spending shows a consistent downward trend.")
            else:
                variance = monthly_spending.var()
                if variance > (monthly_spending.mean() * 0.3) ** 2:
                    insights.append("Your monthly spending varies significantly month to month.")
        
        return insights
    
    def analyze_category_behavior(self) -> List[str]:
        """Analyze spending behavior by category."""
        insights = []
        
        # Category distribution
        category_spending = self.df.groupby('category')['amount'].sum().sort_values(ascending=False)
        total_spending = category_spending.sum()
        
        top_category = category_spending.index[0]
        top_percentage = (category_spending.iloc[0] / total_spending) * 100
        
        insights.append(f"Your highest spending category is '{top_category}', accounting for {top_percentage:.1f}% of total expenses.")
        
        # Identify significant categories (>10% of spending)
        significant_categories = category_spending[category_spending / total_spending > 0.1]
        if len(significant_categories) > 1:
            insights.append(f"Your major spending categories are: {', '.join(significant_categories.index)}.")
        
        # Category consistency
        for category in category_spending.index[:3]:  # Top 3 categories
            category_data = self.df[self.df['category'] == category]['amount']
            cv = category_data.std() / category_data.mean()  # Coefficient of variation
            
            if cv < 0.5:
                insights.append(f"Your '{category}' spending is very consistent.")
            elif cv > 1.5:
                insights.append(f"Your '{category}' spending varies significantly between transactions.")
        
        # Category growth
        if len(self.df['month'].unique()) > 1:
            for category in category_spending.index[:3]:
                monthly_category = self.df[self.df['category'] == category].groupby('month')['amount'].sum()
                if len(monthly_category) > 1:
                    trend = np.polyfit(range(len(monthly_category)), monthly_category.values, 1)[0]
                    if trend > 0:
                        insights.append(f"Your '{category}' spending is trending upward over time.")
                    elif trend < -10:  # Significant downward trend
                        insights.append(f"Your '{category}' spending is decreasing over time.")
        
        return insights
    
    def analyze_temporal_patterns(self) -> List[str]:
        """Analyze temporal spending patterns."""
        insights = []
        
        # Day of week patterns
        daily_spending = self.df.groupby('day_of_week')['amount'].sum()
        max_day = daily_spending.idxmax()
        min_day = daily_spending.idxmin()
        
        insights.append(f"You spend the most on {max_day}s and the least on {min_day}s.")
        
        # Weekend vs weekday spending
        weekend_days = ['Saturday', 'Sunday']
        weekday_spending = daily_spending[~daily_spending.index.isin(weekend_days)].mean()
        weekend_spending = daily_spending[daily_spending.index.isin(weekend_days)].mean()
        
        if weekend_spending > weekday_spending * 1.2:
            insights.append("You tend to spend significantly more on weekends.")
        elif weekday_spending > weekend_spending * 1.2:
            insights.append("You spend more during weekdays than weekends.")
        
        # Monthly patterns
        if len(self.df['month'].unique()) >= 6:
            monthly_avg = self.df.groupby(self.df['date'].dt.month)['amount'].mean()
            peak_month = calendar.month_name[monthly_avg.idxmax()]
            low_month = calendar.month_name[monthly_avg.idxmin()]
            
            insights.append(f"Your highest spending month is typically {peak_month}, and lowest is {low_month}.")
        
        # Transaction timing
        if 'hour' in self.df.columns and not self.df['hour'].isna().all():
            hourly_transactions = self.df.groupby('hour')['amount'].count()
            peak_hour = hourly_transactions.idxmax()
            
            if 9 <= peak_hour <= 17:
                insights.append("Most of your transactions occur during business hours.")
            elif 18 <= peak_hour <= 22:
                insights.append("You tend to make most transactions in the evening.")
        
        return insights
    
    def detect_unusual_behavior(self) -> List[str]:
        """Detect anomalies and unusual spending behavior."""
        insights = []
        
        # Statistical outliers
        Q1 = self.df['amount'].quantile(0.25)
        Q3 = self.df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        outlier_threshold = Q3 + 1.5 * IQR
        
        outliers = self.df[self.df['amount'] > outlier_threshold]
        if len(outliers) > 0:
            insights.append(f"You have {len(outliers)} unusually large transactions (>${outlier_threshold:.2f}+).")
            
            # Most common outlier category
            if len(outliers) > 1:
                top_outlier_category = outliers['category'].mode().iloc[0]
                insights.append(f"Most large transactions are in the '{top_outlier_category}' category.")
        
        # Sudden spending spikes
        daily_spending = self.df.groupby(self.df['date'].dt.date)['amount'].sum()
        if len(daily_spending) > 7:
            rolling_avg = daily_spending.rolling(window=7).mean()
            spikes = daily_spending[daily_spending > rolling_avg * 2]
            
            if len(spikes) > 0:
                insights.append(f"You had {len(spikes)} days with spending significantly above your weekly average.")
        
        # Dormant periods
        date_range = pd.date_range(start=self.df['date'].min(), end=self.df['date'].max(), freq='D')
        spending_days = set(self.df['date'].dt.date)
        no_spending_days = len(date_range) - len(spending_days)
        
        if no_spending_days > len(date_range) * 0.3:
            insights.append(f"You had no recorded transactions on {no_spending_days} days, which is {no_spending_days/len(date_range)*100:.1f}% of the period.")
        
        return insights
    
    def identify_savings_opportunities(self) -> List[str]:
        """Identify potential areas for cost savings."""
        insights = []
        
        # High-frequency, small-amount categories (daily coffee, etc.)
        frequent_small = self.df[self.df['amount'] < 20].groupby('category').agg({
            'amount': ['sum', 'count', 'mean']
        })
        frequent_small.columns = ['total', 'count', 'avg']
        frequent_small = frequent_small[frequent_small['count'] >= 10]
        
        if len(frequent_small) > 0:
            for category in frequent_small.index:
                total = frequent_small.loc[category, 'total']
                count = frequent_small.loc[category, 'count']
                if total > 200:  # Significant total for small transactions
                    monthly_equivalent = total / (len(self.df['month'].unique()) or 1)
                    insights.append(f"Small '{category}' purchases add up to ${monthly_equivalent:.2f}/month - consider bulk buying or alternatives.")
        
        # Subscription-like patterns
        potential_subscriptions = self.df.groupby(['description', 'amount']).size()
        recurring = potential_subscriptions[potential_subscriptions >= 3]
        
        if len(recurring) > 0:
            insights.append(f"You have {len(recurring)} potentially recurring charges - review subscriptions for unused services.")
        
        # Category-specific savings recommendations
        category_totals = self.df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        for category, total in category_totals.head(3).items():
            monthly_avg = total / (len(self.df['month'].unique()) or 1)
            
            if category == 'Food' and monthly_avg > 300:
                insights.append("Consider meal planning and cooking at home to reduce food expenses.")
            elif category == 'Shopping' and monthly_avg > 400:
                insights.append("Implement a waiting period before non-essential purchases to reduce impulse buying.")
            elif category == 'Transportation' and monthly_avg > 200:
                insights.append("Consider carpooling, public transit, or combining trips to reduce transportation costs.")
            elif category == 'Utilities' and monthly_avg > 200:
                insights.append("Review utility bills and furniture purchases - consider energy efficiency and buying used items.")
            elif category == 'Grocery' and monthly_avg > 400:
                insights.append("Use grocery coupons, buy generic brands, and meal plan to reduce grocery expenses.")
            elif category == 'Bank' and monthly_avg > 100:
                insights.append("Review bank fees and consider switching to accounts with lower fees or better terms.")
        
        # Seasonal savings opportunities
        if len(self.df['month'].unique()) >= 6:
            monthly_spending = self.df.groupby(self.df['date'].dt.month)['amount'].sum()
            peak_months = monthly_spending[monthly_spending > monthly_spending.mean() * 1.3]
            
            if len(peak_months) > 0:
                peak_month_names = [calendar.month_name[month] for month in peak_months.index]
                insights.append(f"Your spending peaks in {', '.join(peak_month_names)} - budget extra for these months.")
        
        return insights
    
    def assess_financial_health(self) -> List[str]:
        """Assess overall financial health indicators."""
        insights = []
        
        # Spending consistency
        monthly_spending = self.df.groupby('month')['amount'].sum()
        if len(monthly_spending) > 1:
            cv = monthly_spending.std() / monthly_spending.mean()
            
            if cv < 0.2:
                insights.append("Your spending is very consistent month-to-month, which is excellent for budgeting.")
            elif cv > 0.5:
                insights.append("Your monthly spending varies significantly - consider creating a more stable budget.")
        
        # Diversification of spending
        category_diversity = len(self.df['category'].unique())
        if category_diversity < 4:
            insights.append("Your spending is concentrated in few categories - consider if this reflects your lifestyle goals.")
        elif category_diversity > 10:
            insights.append("You have diverse spending across many categories - ensure you're tracking all expenses effectively.")
        
        # Transaction size distribution
        small_transactions = (self.df['amount'] < 25).mean() * 100
        large_transactions = (self.df['amount'] > 200).mean() * 100
        
        if small_transactions > 60:
            insights.append(f"{small_transactions:.0f}% of your transactions are under $25 - small purchases add up quickly.")
        
        if large_transactions > 20:
            insights.append(f"{large_transactions:.0f}% of your transactions are over $200 - ensure large purchases align with your budget.")
        
        # Spending velocity (rate of spending increase/decrease)
        if len(monthly_spending) > 2:
            recent_trend = monthly_spending.tail(3).mean() - monthly_spending.head(3).mean()
            if recent_trend > monthly_spending.mean() * 0.2:
                insights.append("Your spending has increased significantly in recent months.")
            elif recent_trend < -monthly_spending.mean() * 0.2:
                insights.append("Your spending has decreased significantly in recent months - great progress!")
        
        return insights
    
    def generate_personalized_recommendations(self) -> List[str]:
        """Generate personalized recommendations based on spending behavior."""
        recommendations = []
        
        # Analyze spending behavior
        total_spending = self.df['amount'].sum()
        avg_monthly = total_spending / (len(self.df['month'].unique()) or 1)
        
        # Budget recommendations
        recommendations.append(f"Based on your average monthly spending of ${avg_monthly:.2f}, consider setting up category budgets.")
        
        # Emergency fund recommendation
        emergency_fund_target = avg_monthly * 3
        recommendations.append(f"Aim to save ${emergency_fund_target:.2f} (3 months of expenses) for emergencies.")
        
        # Saving goals
        potential_savings = total_spending * 0.1  # 10% savings target
        monthly_savings_target = potential_savings / 12
        recommendations.append(f"Try to save ${monthly_savings_target:.2f} per month (10% of spending) for financial goals.")
        
        return recommendations
    
    def generate_budget_suggestions(self) -> Dict[str, float]:
        """Generate budget suggestions based on historical spending."""
        category_spending = self.df.groupby('category')['amount'].sum()
        monthly_spending = category_spending / (len(self.df['month'].unique()) or 1)
        
        # Add 10% buffer to historical averages
        budget_suggestions = (monthly_spending * 1.1).round(2).to_dict()
        
        return budget_suggestions