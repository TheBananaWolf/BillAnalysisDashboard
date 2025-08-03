"""
Visualization Module
Creates charts and visualizations for financial data.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
import calendar

class Visualizer:
    """Creates various visualizations for financial data analysis."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize visualizer with financial data.
        
        Args:
            df: DataFrame containing financial transactions
        """
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Color palette
        self.colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def create_daily_spending_chart(self, df: Optional[pd.DataFrame] = None) -> go.Figure:
        """Create daily spending trend chart."""
        if df is None:
            df = self.df
        
        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
        daily_spending.columns = ['date', 'amount']
        
        # Determine appropriate moving averages based on data size
        num_days = len(daily_spending)
        
        fig = go.Figure()
        
        # Daily spending (always show as both markers and lines for better visibility)
        fig.add_trace(go.Scatter(
            x=daily_spending['date'],
            y=daily_spending['amount'],
            mode='lines+markers',
            name='Daily Spending',
            marker=dict(size=8, color='#1f77b4'),
            line=dict(color='#1f77b4', width=3)
        ))
        
        # Add moving averages only if we have enough data
        if num_days >= 3:
            # Use smaller window for limited data
            window_size = min(3, num_days)
            daily_spending['ma_short'] = daily_spending['amount'].rolling(window=window_size, center=True).mean()
            
            fig.add_trace(go.Scatter(
                x=daily_spending['date'],
                y=daily_spending['ma_short'],
                mode='lines',
                name=f'{window_size}-Day Average',
                line=dict(color='orange', width=2, dash='dash')
            ))
        
        # Add 7-day moving average only if we have enough data
        if num_days >= 7:
            daily_spending['ma_7'] = daily_spending['amount'].rolling(window=7, center=True).mean()
            fig.add_trace(go.Scatter(
                x=daily_spending['date'],
                y=daily_spending['ma_7'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='green', width=2)
            ))
        
        # Add 30-day moving average only if we have enough data
        if num_days >= 30:
            daily_spending['ma_30'] = daily_spending['amount'].rolling(window=30, center=True).mean()
            fig.add_trace(go.Scatter(
                x=daily_spending['date'],
                y=daily_spending['ma_30'],
                mode='lines',
                name='30-Day Average',
                line=dict(color='red', width=2)
            ))
        
        # Update layout with adaptive title
        title = f'Daily Spending Trend ({num_days} days)'
        if num_days < 7:
            title += ' - Limited Data'
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            height=400,
            hovermode='x unified',
            showlegend=True
        )
        
        # Add annotation for small datasets
        if num_days < 7:
            fig.add_annotation(
                text=f"Note: Only {num_days} days of data available.<br>Add more data for meaningful trends.",
                xref="paper", yref="paper",
                x=0.5, y=0.95, 
                showarrow=False,
                font=dict(size=10, color="gray"),
                align="center"
            )
        
        return fig
    
    def create_spending_distribution(self, df: Optional[pd.DataFrame] = None) -> go.Figure:
        """Create spending amount distribution chart."""
        if df is None:
            df = self.df
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Spending Distribution', 'Box Plot by Category'),
            vertical_spacing=0.15
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(
                x=df['amount'],
                nbinsx=50,
                name='Distribution',
                marker_color='skyblue'
            ),
            row=1, col=1
        )
        
        # Box plot by category
        for i, category in enumerate(df['category'].unique()):
            category_data = df[df['category'] == category]['amount']
            fig.add_trace(
                go.Box(
                    y=category_data,
                    name=category,
                    marker_color=self.colors[i % len(self.colors)]
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title='Spending Amount Analysis',
            height=700,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Amount ($)", row=2, col=1)
        
        return fig
    
    def create_category_heatmap(self) -> go.Figure:
        """Create heatmap of spending by category and month."""
        # Create month-category matrix
        heatmap_data = self.df.groupby([
            self.df['date'].dt.to_period('M'),
            'category'
        ])['amount'].sum().unstack(fill_value=0)
        
        # Convert period index to string
        heatmap_data.index = heatmap_data.index.astype(str)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Blues',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Spending Heatmap: Category vs Month',
            xaxis_title='Category',
            yaxis_title='Month',
            height=500
        )
        
        return fig
    
    def create_spending_sunburst(self) -> go.Figure:
        """Create sunburst chart for hierarchical spending view."""
        # Create hierarchical data
        category_monthly = self.df.groupby(['category', self.df['date'].dt.to_period('M')])['amount'].sum().reset_index()
        category_monthly['month'] = category_monthly['date'].astype(str)
        
        # Create sunburst data
        sunburst_data = []
        
        # Add category level
        for category in self.df['category'].unique():
            total_amount = self.df[self.df['category'] == category]['amount'].sum()
            sunburst_data.append({
                'ids': category,
                'labels': category,
                'parents': '',
                'values': total_amount
            })
        
        # Add month level within categories
        for _, row in category_monthly.iterrows():
            sunburst_data.append({
                'ids': f"{row['category']}-{row['month']}",
                'labels': row['month'],
                'parents': row['category'],
                'values': row['amount']
            })
        
        sunburst_df = pd.DataFrame(sunburst_data)
        
        fig = go.Figure(go.Sunburst(
            ids=sunburst_df['ids'],
            labels=sunburst_df['labels'],
            parents=sunburst_df['parents'],
            values=sunburst_df['values'],
            branchvalues="total"
        ))
        
        fig.update_layout(
            title="Spending Hierarchy: Categories and Months",
            height=600
        )
        
        return fig
    
    def create_weekly_pattern_radar(self) -> go.Figure:
        """Create radar chart for weekly spending patterns."""
        # Calculate average spending by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_avg = self.df.groupby(self.df['date'].dt.day_name())['amount'].mean()
        
        # Reorder by day of week
        weekly_avg = weekly_avg.reindex(day_order)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=weekly_avg.values,
            theta=day_order,
            fill='toself',
            name='Average Spending',
            line_color='rgba(31, 119, 180, 0.8)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, weekly_avg.max() * 1.1]
                )
            ),
            title="Weekly Spending Pattern",
            height=500
        )
        
        return fig
    
    def create_transaction_timeline(self, category: Optional[str] = None, top_n: int = 50) -> go.Figure:
        """Create timeline of transactions."""
        if category:
            df_filtered = self.df[self.df['category'] == category]
            title = f"Transaction Timeline - {category}"
        else:
            # Show top N transactions
            df_filtered = self.df.nlargest(top_n, 'amount')
            title = f"Top {top_n} Transactions Timeline"
        
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=df_filtered['amount'],
            mode='markers',
            marker=dict(
                size=8,
                color=df_filtered['amount'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Amount ($)")
            ),
            text=df_filtered['description'],
            hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Amount: $%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            height=500,
            hovermode='closest'
        )
        
        return fig
    
    def create_monthly_comparison_bar(self) -> go.Figure:
        """Create monthly comparison bar chart."""
        monthly_data = self.df.groupby(self.df['date'].dt.to_period('M')).agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        monthly_data.columns = ['total_amount', 'transaction_count', 'avg_amount']
        monthly_data.index = monthly_data.index.astype(str)
        monthly_data = monthly_data.reset_index()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Total Spending', 'Transaction Count'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Total spending
        fig.add_trace(
            go.Bar(
                x=monthly_data['date'],
                y=monthly_data['total_amount'],
                name='Total Spending',
                marker_color='steelblue'
            ),
            row=1, col=1
        )
        
        # Transaction count
        fig.add_trace(
            go.Bar(
                x=monthly_data['date'],
                y=monthly_data['transaction_count'],
                name='Transaction Count',
                marker_color='orange'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title='Monthly Spending Comparison',
            height=400,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Month", row=1, col=1)
        fig.update_xaxes(title_text="Month", row=1, col=2)
        fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        
        return fig
    
    def create_category_treemap(self) -> go.Figure:
        """Create treemap for category spending."""
        category_data = self.df.groupby('category')['amount'].sum().reset_index()
        category_data = category_data.sort_values('amount', ascending=False)
        
        fig = go.Figure(go.Treemap(
            labels=category_data['category'],
            values=category_data['amount'],
            parents=[""] * len(category_data),
            textinfo="label+value",
            texttemplate="<b>%{label}</b><br>$%{value:,.0f}",
            hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percentParent}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Spending by Category (Treemap)",
            height=500
        )
        
        return fig
    
    def create_spending_velocity_chart(self) -> go.Figure:
        """Create spending velocity chart (cumulative spending over time)."""
        daily_spending = self.df.groupby(self.df['date'].dt.date)['amount'].sum().reset_index()
        daily_spending.columns = ['date', 'daily_amount']
        daily_spending['cumulative_amount'] = daily_spending['daily_amount'].cumsum()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Spending', 'Cumulative Spending'),
            vertical_spacing=0.1
        )
        
        # Daily spending
        fig.add_trace(
            go.Scatter(
                x=daily_spending['date'],
                y=daily_spending['daily_amount'],
                mode='lines',
                name='Daily Spending',
                line=dict(color='lightblue', width=1),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # Cumulative spending
        fig.add_trace(
            go.Scatter(
                x=daily_spending['date'],
                y=daily_spending['cumulative_amount'],
                mode='lines',
                name='Cumulative Spending',
                line=dict(color='darkblue', width=3)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='Spending Velocity Analysis',
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Daily Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Amount ($)", row=2, col=1)
        
        return fig
    
    def create_budget_vs_actual_chart(self, budget_dict: Dict[str, float]) -> go.Figure:
        """
        Create budget vs actual spending comparison.
        
        Args:
            budget_dict: Dictionary with category budgets
        """
        category_spending = self.df.groupby('category')['amount'].sum()
        
        comparison_data = []
        for category in category_spending.index:
            budget = budget_dict.get(category, 0)
            actual = category_spending[category]
            comparison_data.append({
                'category': category,
                'budget': budget,
                'actual': actual,
                'variance': actual - budget,
                'variance_pct': ((actual - budget) / budget * 100) if budget > 0 else 0
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        fig = go.Figure()
        
        # Budget bars
        fig.add_trace(go.Bar(
            x=comparison_df['category'],
            y=comparison_df['budget'],
            name='Budget',
            marker_color='lightgreen',
            opacity=0.7
        ))
        
        # Actual bars
        fig.add_trace(go.Bar(
            x=comparison_df['category'],
            y=comparison_df['actual'],
            name='Actual',
            marker_color='crimson',
            opacity=0.7
        ))
        
        fig.update_layout(
            title='Budget vs Actual Spending by Category',
            xaxis_title='Category',
            yaxis_title='Amount ($)',
            barmode='group',
            height=500
        )
        
        return fig