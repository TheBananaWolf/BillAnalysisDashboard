#!/usr/bin/env python3
"""
Bill Analysis System
Main application for analyzing personal spending patterns and financial habits.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logger = logging.getLogger(__name__)

# Import custom modules
from src.data_processor import DataProcessor
from src.analyzer import BillAnalyzer
from src.visualizer import Visualizer
from src.insights_generator import InsightsGenerator

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Bill Analysis Dashboard",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">💰 Bill Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.df = None
    
    # Sidebar
    st.sidebar.header("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Data Upload", "Overview", "Spending Analysis", "Category Analysis", "Trends", "Insights", "Export Reports", "🐛 Debug Info"]
    )
    
    if page == "Data Upload":
        show_data_upload()
    elif page == "Overview" and st.session_state.data_loaded:
        show_overview()
    elif page == "Spending Analysis" and st.session_state.data_loaded:
        show_spending_analysis()
    elif page == "Category Analysis" and st.session_state.data_loaded:
        show_category_analysis()
    elif page == "Trends" and st.session_state.data_loaded:
        show_trends()
    elif page == "Insights" and st.session_state.data_loaded:
        show_insights()
    elif page == "Export Reports" and st.session_state.data_loaded:
        show_export_reports()
    elif page == "🐛 Debug Info":
        show_debug_info()
    else:
        if not st.session_state.data_loaded:
            st.warning("Please upload your bill data first in the 'Data Upload' section.")
        else:
            show_overview()

def show_data_upload():
    """Data upload and processing page"""
    st.header("📁 Upload Your Bill Data")
    
    # Data source selection
    data_source = st.radio(
        "Choose your data source:",
        ["Upload File", "Notion Page URL", "Sample Data"],
        horizontal=True
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if data_source == "Upload File":
            st.subheader("📄 Upload File")
            uploaded_file = st.file_uploader(
                "Choose a file (CSV, Excel, or JSON)",
                type=['csv', 'xlsx', 'xls', 'json'],
                help="Upload your bill/transaction data in CSV, Excel, or JSON format"
            )
            
            if uploaded_file is not None:
                try:
                    processor = DataProcessor()
                    df = processor.load_data(uploaded_file)
                    
                    st.success(f"✅ Data loaded successfully! {len(df)} transactions found.")
                    
                    # Show data preview
                    _show_data_preview(df)
                    
                    # Store in session state
                    st.session_state.df = df
                    st.session_state.data_loaded = True
                    
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
        
        elif data_source == "Notion Page URL":
            st.subheader("🌐 Load from Notion")
            
            notion_url = st.text_input(
                "Enter your Notion page URL:",
                placeholder="https://notion.so/your-page-url",
                help="Paste the URL of your Notion page containing bill/transaction data"
            )
            
            if st.button("🔄 Scrape Data from Notion", type="primary"):
                if notion_url:
                    try:
                        with st.spinner("Scraping data from Notion... This may take a few moments."):
                            processor = DataProcessor()
                            df = processor.load_from_notion_url(notion_url)
                            
                            if not df.empty:
                                st.success(f"✅ Data scraped successfully! {len(df)} transactions found.")
                                
                                # Check data source and show appropriate message
                                data_source = df.get('_data_source', ['unknown']).iloc[0] if '_data_source' in df.columns else 'unknown'
                                is_sample = '_is_sample_data' in df.columns and df['_is_sample_data'].iloc[0]
                                
                                if data_source == 'notion' and not is_sample:
                                    st.success(f"✅ Successfully loaded {len(df)} REAL transactions from Notion!")
                                elif is_sample or data_source in ['sample', 'sample_fallback']:
                                    st.error(f"❌ Notion scraping failed - showing SAMPLE data instead!")
                                    st.warning("🔍 The data below is NOT your real Notion data. Use the '🐛 Debug Info' page to see why scraping failed.")
                                    
                                    # Add a clear sample data indicator
                                    st.markdown("""
                                    <div style="background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 4px solid #f44336;">
                                    <strong>⚠️ WARNING:</strong> This is fake sample data, not your real transactions!
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.info(f"ℹ️ Loaded {len(df)} transactions (source: {data_source})")
                                
                                # Remove the data source markers before storing
                                df_clean = df.copy()
                                for col in ['_data_source', '_is_sample_data']:
                                    if col in df_clean.columns:
                                        df_clean = df_clean.drop(col, axis=1)
                                df = df_clean
                                
                                # Show column information
                                st.info(f"📊 **Columns detected:** {', '.join(df.columns)}")
                                
                                # Show data preview
                                _show_data_preview(df)
                                
                                # Store in session state
                                st.session_state.df = df
                                st.session_state.data_loaded = True
                                
                                # Optionally save scraped data (don't fail if directory doesn't exist)
                                try:
                                    import os
                                    os.makedirs("data", exist_ok=True)
                                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"notion_bills_{timestamp}.csv"
                                    df.to_csv(f"data/{filename}", index=False)
                                    st.info(f"💾 Data saved to: data/{filename}")
                                except Exception as save_error:
                                    logger.warning(f"Could not save data file: {save_error}")
                                    # Don't show error to user, saving is optional
                                
                            else:
                                st.warning("❌ No data could be extracted from the Notion page.")
                                
                                # Show troubleshooting tips
                                with st.expander("🔧 Troubleshooting Tips"):
                                    st.markdown("""
                                    **Common issues and solutions:**
                                    
                                    1. **Page not accessible**: Make sure your Notion page is publicly shared
                                       - Go to your Notion page → Click "Share" → Toggle "Share to web"
                                    
                                    2. **No table found**: Ensure your data is in a table format
                                       - Use Notion's table/database block
                                       - Include column headers
                                    
                                    3. **Wrong data format**: Check your column names
                                       - Required: Date, Amount, Description
                                       - Optional: Category, Account, Type
                                    
                                    4. **Alternative approach**: Export from Notion and upload as CSV
                                       - In Notion: ··· menu → Export → CSV
                                       - Then use the "Upload File" option above
                                    """)
                                
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Error scraping Notion page: {error_msg}")
                        
                        # Provide specific guidance based on error type
                        if "duplicate column" in error_msg.lower():
                            st.info("🔧 **Column issue detected**: Your Notion table may have duplicate column names. Try renaming any duplicate columns in your Notion page.")
                        elif "timeout" in error_msg.lower():
                            st.info("⏱️ **Timeout issue**: The page is taking too long to load. Try refreshing your Notion page or check your internet connection.")
                        elif "not found" in error_msg.lower() or "404" in error_msg:
                            st.info("🔗 **URL issue**: The page URL may be incorrect or the page may not be publicly accessible.")
                        else:
                            st.info("💡 **General tip**: Make sure your Notion page is publicly accessible or try using the file upload option.")
                        
                        # Always offer the sample data option
                        if st.button("📝 Try Sample Data Instead"):
                            processor = DataProcessor()
                            df = processor.create_sample_data()
                            st.session_state.df = df
                            st.session_state.data_loaded = True
                            st.success("Sample data loaded! You can now explore the application features.")
                            st.experimental_rerun()
                            
                else:
                    st.warning("Please enter a Notion URL")
            
            # Information about Notion scraping
            st.info("""
            📝 **How to prepare your Notion page:**
            1. Make sure your page contains a table or database with transaction data
            2. Include columns for: Date, Amount, Description (required)
            3. Optional columns: Category, Account, Type
            4. Ensure the page is publicly accessible (shared with view permissions)
            """)
        
        elif data_source == "Sample Data":
            st.subheader("📝 Sample Data")
            st.info("Use sample data to explore the application features")
            
            if st.button("📊 Load Sample Data", type="primary"):
                processor = DataProcessor()
                df = processor.create_sample_data()
                st.session_state.df = df
                st.session_state.data_loaded = True
                st.success("Sample data loaded!")
                _show_data_preview(df)
                st.experimental_rerun()
    
    with col2:
        st.subheader("💡 Data Format Guide")
        st.markdown("""
        **Required columns:**
        - `date` - Transaction date
        - `amount` - Transaction amount
        - `description` - Transaction description
        
        **Optional columns:**
        - `category` - Expense category
        - `account` - Account name
        - `type` - Transaction type
        """)
        
        st.subheader("🔧 Troubleshooting")
        st.markdown("""
        **If Notion scraping fails:**
        - Check if the page is publicly accessible
        - Ensure data is in a table format
        - Try exporting from Notion as CSV and uploading
        
        **Supported file formats:**
        - CSV (.csv)
        - Excel (.xlsx, .xls)
        - JSON (.json)
        """)


def _show_data_preview(df: pd.DataFrame):
    """Show data preview and information."""
    # Show data preview
    st.subheader("📊 Data Preview")
    st.dataframe(df.head(10))
    
    # Data info
    st.subheader("ℹ️ Data Information")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"**Rows:** {len(df)}")
        st.info(f"**Columns:** {len(df.columns)}")
    with col_info2:
        st.info(f"**Date Range:** {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        st.info(f"**Total Amount:** ${df['amount'].sum():,.2f}")

def show_overview():
    """Overview dashboard page"""
    st.header("📊 Financial Overview")
    
    df = st.session_state.df
    analyzer = BillAnalyzer(df)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spent = df['amount'].sum()
        st.metric("Total Spent", f"${total_spent:,.2f}")
    
    with col2:
        avg_transaction = df['amount'].mean()
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")
    
    with col3:
        num_transactions = len(df)
        st.metric("Total Transactions", f"{num_transactions:,}")
    
    with col4:
        days_range = (df['date'].max() - df['date'].min()).days
        daily_avg = total_spent / max(days_range, 1)
        st.metric("Daily Average", f"${daily_avg:.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly spending
        monthly_data = analyzer.get_monthly_spending()
        fig = px.bar(monthly_data, x='month', y='total_amount', 
                    title="Monthly Spending")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category distribution
        category_data = analyzer.get_category_summary()
        fig = px.pie(category_data, values='amount', names='category',
                    title="Spending by Category")
        st.plotly_chart(fig, use_container_width=True)

def show_spending_analysis():
    """Detailed spending analysis page"""
    st.header("💳 Spending Analysis")
    
    df = st.session_state.df
    analyzer = BillAnalyzer(df)
    visualizer = Visualizer(df)
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min(),
            max_value=df['date'].max()
        )
    
    with col2:
        categories = st.multiselect(
            "Categories",
            options=df['category'].unique(),
            default=df['category'].unique()
        )
    
    with col3:
        amount_range = st.slider(
            "Amount Range",
            min_value=float(df['amount'].min()),
            max_value=float(df['amount'].max()),
            value=(float(df['amount'].min()), float(df['amount'].max()))
        )
    
    # Filter data
    filtered_df = df[
        (df['date'] >= pd.to_datetime(date_range[0])) &
        (df['date'] <= pd.to_datetime(date_range[1])) &
        (df['category'].isin(categories)) &
        (df['amount'] >= amount_range[0]) &
        (df['amount'] <= amount_range[1])
    ]
    
    # Analysis results
    st.subheader("📈 Analysis Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily spending trend
        daily_spending = visualizer.create_daily_spending_chart(filtered_df)
        st.plotly_chart(daily_spending, use_container_width=True)
        
        # Top transactions
        st.subheader("💰 Highest Transactions")
        top_transactions = filtered_df.nlargest(10, 'amount')[['date', 'description', 'amount', 'category']]
        st.dataframe(top_transactions)
    
    with col2:
        # Spending distribution
        spending_dist = visualizer.create_spending_distribution(filtered_df)
        st.plotly_chart(spending_dist, use_container_width=True)
        
        # Weekly patterns
        weekly_pattern = analyzer.get_weekly_patterns(filtered_df)
        fig = px.bar(weekly_pattern, x='day_of_week', y='avg_amount',
                    title="Average Spending by Day of Week")
        st.plotly_chart(fig, use_container_width=True)

def show_category_analysis():
    """Category-based analysis page"""
    st.header("🏷️ Category Analysis")
    
    df = st.session_state.df
    analyzer = BillAnalyzer(df)
    
    # Category summary
    category_summary = analyzer.get_category_summary()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Category Summary")
        st.dataframe(category_summary.style.format({
            'amount': '${:,.2f}',
            'avg_amount': '${:,.2f}',
            'percentage': '{:.1f}%'
        }))
    
    with col2:
        # Category trends over time
        fig = analyzer.get_category_trends()
        st.plotly_chart(fig, use_container_width=True)
    
    # Category comparison
    st.subheader("🔍 Category Comparison")
    
    selected_categories = st.multiselect(
        "Select categories to compare:",
        options=df['category'].unique(),
        default=list(df['category'].unique())[:5]
    )
    
    if selected_categories:
        category_comparison = analyzer.compare_categories(selected_categories)
        st.plotly_chart(category_comparison, use_container_width=True)

def show_trends():
    """Trends analysis page"""
    st.header("📈 Spending Trends")
    
    df = st.session_state.df
    analyzer = BillAnalyzer(df)
    
    # Trend analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly trends
        monthly_trends = analyzer.get_spending_trends()
        st.plotly_chart(monthly_trends, use_container_width=True)
        
        # Seasonal analysis
        seasonal_data = analyzer.get_seasonal_analysis()
        fig = px.bar(seasonal_data, x='season', y='avg_amount',
                    title="Average Spending by Season")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Yearly comparison
        yearly_data = analyzer.get_yearly_comparison()
        if len(yearly_data) > 1:
            fig = px.line(yearly_data, x='month', y='amount', color='year',
                         title="Year-over-Year Comparison")
            st.plotly_chart(fig, use_container_width=True)
        
        # Growth analysis
        growth_data = analyzer.calculate_growth_rates()
        if not growth_data.empty:
            st.subheader("📊 Growth Rates")
            st.dataframe(growth_data.style.format('{:.2f}%'))

def show_insights():
    """AI-generated insights page"""
    st.header("🧠 Financial Insights")
    
    df = st.session_state.df
    insights_gen = InsightsGenerator(df)
    
    # Generate insights
    insights = insights_gen.generate_all_insights()
    
    # Display insights
    for category, insight_list in insights.items():
        st.subheader(f"💡 {category.replace('_', ' ').title()}")
        for insight in insight_list:
            st.markdown(f"• {insight}")
        st.markdown("---")

def show_export_reports():
    """Export and reporting page"""
    st.header("📄 Export Reports")
    
    df = st.session_state.df
    analyzer = BillAnalyzer(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Generate Report")
        
        report_type = st.selectbox(
            "Report Type:",
            ["Monthly Summary", "Category Analysis", "Yearly Report", "Custom Analysis"]
        )
        
        if st.button("Generate Report"):
            report_data = analyzer.generate_report(report_type)
            
            # Convert to CSV
            csv_data = report_data.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV Report",
                data=csv_data,
                file_name=f"{report_type.lower().replace(' ', '_')}_report.csv",
                mime="text/csv"
            )
            
            st.success("Report generated successfully!")
    
    with col2:
        st.subheader("📈 Export Charts")
        
        chart_type = st.selectbox(
            "Chart Type:",
            ["Spending Trends", "Category Distribution", "Monthly Comparison"]
        )
        
        if st.button("Generate Chart"):
            # This would generate and save chart images
            st.info("Chart export feature would be implemented here")

def show_debug_info():
    """Debug information page to help troubleshoot cloud vs local issues"""
    st.header("🐛 Debug Information")
    
    # Environment Information
    st.subheader("🖥️ Environment Information")
    
    import platform
    import os
    import sys
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Information:**")
        st.write(f"• OS: {platform.system()} {platform.release()}")
        st.write(f"• Platform: {platform.platform()}")
        st.write(f"• Architecture: {platform.architecture()[0]}")
        st.write(f"• Python: {platform.python_version()}")
        st.write(f"• Streamlit: {st.__version__}")
    
    with col2:
        st.write("**Chrome Environment:**")
        chrome_bin = os.getenv('CHROME_BIN', 'Not set')
        chromedriver_path = os.getenv('CHROMEDRIVER_PATH', 'Not set')
        st.write(f"• CHROME_BIN: {chrome_bin}")
        st.write(f"• CHROMEDRIVER_PATH: {chromedriver_path}")
        
        if chrome_bin != 'Not set':
            st.write(f"• Chrome binary exists: {os.path.exists(chrome_bin)}")
        if chromedriver_path != 'Not set':
            st.write(f"• ChromeDriver exists: {os.path.exists(chromedriver_path)}")
    
    # Test Notion Scraping with Detailed Logs
    st.subheader("🧪 Test Notion Scraping")
    
    if st.button("🔍 Test Notion Scraper (Detailed Logs)"):
        test_url = "https://opposite-wallet-8b6.notion.site/Bill-242d20f0d6578090af3ec52595e2d828"
        
        with st.spinner("Testing Notion scraper..."):
            try:
                # Import and test the scraper
                from src.notion_scraper import NotionScraper
                
                # Capture logs in a string
                import io
                import logging
                
                # Create string buffer for logs
                log_capture_string = io.StringIO()
                log_handler = logging.StreamHandler(log_capture_string)
                log_handler.setLevel(logging.DEBUG)
                
                # Add handler to logger
                scraper_logger = logging.getLogger('src.notion_scraper')
                scraper_logger.addHandler(log_handler)
                scraper_logger.setLevel(logging.DEBUG)
                
                # Test the scraper
                scraper = NotionScraper()
                result = scraper.scrape_notion_page(test_url)
                
                # Get logs
                log_contents = log_capture_string.getvalue()
                
                # Remove handler
                scraper_logger.removeHandler(log_handler)
                
                # Display results
                st.success(f"✅ Scraper test completed! Found {len(result)} rows")
                
                if '_data_source' in result.columns:
                    data_source = result['_data_source'].iloc[0] if len(result) > 0 else 'unknown'
                    if data_source == 'notion':
                        st.success("🎉 Successfully scraped REAL data from Notion!")
                    else:
                        st.warning(f"⚠️ Scraper fell back to sample data (source: {data_source})")
                
                # Show detailed logs
                st.subheader("📋 Detailed Logs")
                st.text_area("Scraper Logs:", log_contents, height=400)
                
                # Show data preview
                if not result.empty:
                    st.subheader("📊 Scraped Data Preview")
                    if '_data_source' in result.columns:
                        result = result.drop('_data_source', axis=1)
                    st.dataframe(result.head(10))
                
            except Exception as e:
                st.error(f"❌ Error testing Notion scraper: {e}")
                import traceback
                st.text_area("Error Details:", traceback.format_exc(), height=200)
    
    # Data Source Comparison
    st.subheader("📊 Data Source Comparison")
    
    if st.button("📈 Compare Sample vs Notion Data"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Sample Data:**")
            from src.data_processor import DataProcessor
            processor = DataProcessor()
            sample_data = processor.create_sample_data(10)
            st.dataframe(sample_data.head())
            st.write(f"Rows: {len(sample_data)}")
        
        with col2:
            st.write("**Current Session Data:**")
            if st.session_state.data_loaded and st.session_state.df is not None:
                st.dataframe(st.session_state.df.head())
                st.write(f"Rows: {len(st.session_state.df)}")
            else:
                st.warning("No data loaded in current session")
    
    # Tips for Troubleshooting
    st.subheader("💡 Troubleshooting Tips")
    
    st.info("""
    **If you see different data between cloud and local:**
    
    1. **Check the "Test Notion Scraper" logs above** - this will show exactly what's happening
    2. **Look for Chrome/ChromeDriver errors** in the detailed logs
    3. **Compare data sources** - real Notion data vs sample data
    4. **Network issues** - cloud platforms may have firewall restrictions
    5. **Environment differences** - Chrome installation may differ between local and cloud
    
    **Common Cloud Issues:**
    - Chrome binary not found or not executable
    - ChromeDriver version incompatibility  
    - Network restrictions blocking Notion access
    - Memory/resource limitations
    - Missing dependencies
    """)


if __name__ == "__main__":
    main()