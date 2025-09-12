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
# Removed data cleanup functionality

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
    
    # Data cleanup functionality has been removed for better data persistence
    
    # Sidebar
    st.sidebar.header("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Data Upload", "Data Preview", "Overview", "Spending Analysis", "Category Analysis", "Category Calculator", "Trends", "Insights", "Export Reports"]
    )
    
    if page == "Data Upload":
        show_data_upload()
    elif page == "Data Preview" and st.session_state.data_loaded:
        show_data_preview_page()
    elif page == "Overview" and st.session_state.data_loaded:
        show_overview()
    elif page == "Spending Analysis" and st.session_state.data_loaded:
        show_spending_analysis()
    elif page == "Category Analysis" and st.session_state.data_loaded:
        show_category_analysis()
    elif page == "Category Calculator" and st.session_state.data_loaded:
        show_category_calculator()
    elif page == "Trends" and st.session_state.data_loaded:
        show_trends()
    elif page == "Insights" and st.session_state.data_loaded:
        show_insights()
    elif page == "Export Reports" and st.session_state.data_loaded:
        show_export_reports()
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
                        # Show progress steps to user for better experience
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        progress_bar.progress(20)
                        
                        processor = DataProcessor()
                        
                        status_text.text("🌐 Loading Notion page...")
                        progress_bar.progress(50)
                        
                        df = processor.load_from_notion_url(notion_url)
                        
                        status_text.text("📊 Processing and categorizing transactions...")
                        progress_bar.progress(90)
                        
                        # Small delay to show completion
                        import time
                        # time.sleep(0.3)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Scraping completed successfully!")
                        
                        # Clean up progress indicators after a brief moment
                        # time.sleep(0.5)
                        progress_bar.empty()
                        status_text.empty()
                        
                        if not df.empty:
                            st.success(f"✅ Data scraped successfully! {len(df)} transactions found.")
                            
                            # Check data source and show appropriate message
                            data_source = df.get('_data_source', ['unknown']).iloc[0] if '_data_source' in df.columns else 'unknown'
                            is_sample = '_is_sample_data' in df.columns and df['_is_sample_data'].iloc[0]
                            
                            if data_source == 'notion' and not is_sample:
                                st.success(f"✅ Successfully loaded {len(df)} REAL transactions from Notion!")
                            elif is_sample or data_source in ['sample', 'sample_fallback']:
                                st.error(f"❌ Notion scraping failed - showing SAMPLE data instead!")
                                st.warning("🔍 The data below is NOT your real Notion data. Check the browser console or logs for scraping errors.")
                                
                                # Environment-specific guidance
                                from src.notion_scraper import NotionScraper
                                temp_scraper = NotionScraper()
                                env = temp_scraper._detect_environment()
                                
                                if env == 'streamlit_cloud':
                                    st.info("🌐 **Streamlit Cloud detected**: Chrome setup optimized for cloud environment. Check debug logs for specific issues.")
                                elif env == 'docker':
                                    st.info("🐳 **Docker environment detected**: Verify CHROME_BIN and CHROMEDRIVER_PATH are set correctly.")
                                else:
                                    st.info("🖥️ **Local environment detected**: Ensure Chrome/Chromium is installed on your system.")
                                
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
                            # _show_data_preview(df)
                            
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
                                st.caption("💾 Data files are now persisted for better analysis")
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
                # _show_data_preview(df)
                # st.experimental_rerun()
    
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
    """Show paginated data preview and information."""
    # Data info section (quick overview)
    st.subheader("ℹ️ Data Information")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("Total Records", f"{len(df):,}")
        st.metric("Columns", len(df.columns))
    with col_info2:
        st.metric("Date Range", f"{(df['date'].max() - df['date'].min()).days} days")
        st.metric("Categories", df['category'].nunique())
    with col_info3:
        st.metric("Total Amount", f"${df['amount'].sum():,.2f}")
        st.metric("Avg Amount", f"${df['amount'].mean():.2f}")
    
    # Paginated data preview
    st.subheader("📊 Data Preview")
    
    # Pagination settings
    records_per_page = 20
    total_records = len(df)
    total_pages = (total_records - 1) // records_per_page + 1 if total_records > 0 else 1
    
    # Page selection
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        current_page = st.selectbox(
            "Select Page:",
            options=list(range(1, total_pages + 1)),
            format_func=lambda x: f"Page {x} of {total_pages}",
            key="data_preview_page"
        )
    
    # Calculate start and end indices
    start_idx = (current_page - 1) * records_per_page
    end_idx = min(start_idx + records_per_page, total_records)
    
    # Show current page data
    if total_records > 0:
        current_page_df = df.iloc[start_idx:end_idx].copy()
        
        # Format currency columns for better display
        if 'amount' in current_page_df.columns:
            current_page_df['amount'] = current_page_df['amount'].apply(lambda x: f"${x:.2f}")
        
        # Show the data
        st.dataframe(
            current_page_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Show pagination info
        st.caption(f"Showing records {start_idx + 1}-{end_idx} of {total_records}")
        
        # Quick filter options
        with st.expander("🔍 Quick Filters"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Show Recent Transactions"):
                    # Show most recent 20 transactions
                    recent_df = df.nlargest(20, 'date')
                    st.dataframe(recent_df, use_container_width=True, hide_index=True)
            
            with col2:
                if st.button("Show Largest Amounts"):
                    # Show 20 largest transactions
                    largest_df = df.nlargest(20, 'amount')
                    largest_df['amount'] = largest_df['amount'].apply(lambda x: f"${x:.2f}")
                    st.dataframe(largest_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No data to display")

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def _get_overview_data(df_hash: str, df_dict: dict) -> tuple:
    """Cached function to compute overview data."""
    # Reconstruct DataFrame from dictionary (for caching)
    df = pd.DataFrame(df_dict)
    df['date'] = pd.to_datetime(df['date'])
    
    analyzer = BillAnalyzer(df)
    
    # Get all the data we need
    monthly_data = analyzer.get_monthly_spending()
    category_data = analyzer.get_category_summary()
    weekly_patterns = analyzer.get_weekly_patterns()
    
    return monthly_data, category_data, weekly_patterns

def show_overview():
    """Overview dashboard page"""
    st.header("📊 Financial Overview")
    
    df = st.session_state.df
    
    # Create a hash of the DataFrame for caching
    df_hash = str(hash(pd.util.hash_pandas_object(df).sum()))
    df_dict = df.to_dict('records')
    
    # Get cached data
    monthly_data, category_data, weekly_patterns = _get_overview_data(df_hash, df_dict)
    
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
        # Monthly spending (using cached data)
        fig = px.bar(monthly_data, x='month', y='total_amount', 
                    title="Monthly Spending")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category distribution (using cached data)
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

def show_category_calculator():
    """Advanced Category Calculator with comprehensive analysis tools"""
    st.header("🧮 Category Calculator")
    st.markdown("**Comprehensive category spending analysis and calculation tools**")
    
    df = st.session_state.df
    analyzer = BillAnalyzer(df)
    
    # Create tabs for different calculation modes
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Basic Calculator", 
        "📈 Advanced Metrics", 
        "⚖️ Period Comparison", 
        "🔮 Predictions"
    ])
    
    with tab1:
        st.subheader("📊 Basic Category Calculator")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Category selection - ensure all categories are strings
            unique_categories = df['category'].dropna().astype(str).unique().tolist()
            all_categories = sorted(unique_categories)
            selected_categories = st.multiselect(
                "Select categories to calculate:",
                options=all_categories,
                default=all_categories[:5],
                help="Choose one or more categories to analyze"
            )
            
            # Date range selection
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            date_range = st.date_input(
                "Select date range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter transactions by date range"
            )
        
        with col2:
            # Amount filters
            min_amount = float(df['amount'].min())
            max_amount = float(df['amount'].max())
            
            amount_range = st.slider(
                "Amount range ($):",
                min_value=min_amount,
                max_value=max_amount,
                value=(min_amount, max_amount),
                step=0.01,
                help="Filter transactions by amount"
            )
            
            # Calculation mode
            calc_mode = st.selectbox(
                "Calculation mode:",
                ["Total Sum", "Average", "Count", "Median", "Standard Deviation"],
                help="Choose how to calculate the selected categories"
            )
        
        # Perform calculations
        if selected_categories and len(date_range) == 2:
            # Filter data
            start_date, end_date = date_range
            filtered_df = df[
                (df['category'].isin(selected_categories)) &
                (df['date'].dt.date >= start_date) &
                (df['date'].dt.date <= end_date) &
                (df['amount'] >= amount_range[0]) &
                (df['amount'] <= amount_range[1])
            ]
            
            if not filtered_df.empty:
                st.subheader("📋 Calculation Results")
                
                # Calculate metrics for each category
                results = []
                for category in selected_categories:
                    cat_data = filtered_df[filtered_df['category'] == category]
                    if not cat_data.empty:
                        if calc_mode == "Total Sum":
                            value = cat_data['amount'].sum()
                        elif calc_mode == "Average":
                            value = cat_data['amount'].mean()
                        elif calc_mode == "Count":
                            value = len(cat_data)
                        elif calc_mode == "Median":
                            value = cat_data['amount'].median()
                        elif calc_mode == "Standard Deviation":
                            value = cat_data['amount'].std()
                        
                        results.append({
                            'Category': category,
                            calc_mode: round(value, 2) if calc_mode != "Count" else int(value),
                            'Transactions': len(cat_data),
                            'Date Range': f"{cat_data['date'].min().strftime('%Y-%m-%d')} to {cat_data['date'].max().strftime('%Y-%m-%d')}"
                        })
                
                if results:
                    results_df = pd.DataFrame(results)
                    
                    # Display results table
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_value = sum([r[calc_mode] for r in results])
                        st.metric("Total", f"{total_value:,.2f}" if calc_mode != "Count" else f"{total_value:,}")
                    
                    with col2:
                        avg_value = total_value / len(results) if results else 0
                        st.metric("Average", f"{avg_value:,.2f}" if calc_mode != "Count" else f"{avg_value:,.0f}")
                    
                    with col3:
                        total_transactions = sum([r['Transactions'] for r in results])
                        st.metric("Total Transactions", f"{total_transactions:,}")
                    
                    with col4:
                        days_span = (end_date - start_date).days + 1
                        st.metric("Days Analyzed", f"{days_span:,}")
                    
                    # Visualization
                    if len(results) > 1:
                        fig = px.bar(
                            results_df, 
                            x='Category', 
                            y=calc_mode,
                            title=f"{calc_mode} by Category",
                            color=calc_mode,
                            color_continuous_scale='viridis'
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data found for the selected criteria.")
    
    with tab2:
        st.subheader("📈 Advanced Category Metrics")
        
        # Category selection for advanced metrics
        selected_cats_advanced = st.multiselect(
            "Select categories for advanced analysis:",
            options=all_categories,
            default=all_categories[:3],
            key="advanced_cats"
        )
        
        # Date range for advanced analysis
        adv_date_range = st.date_input(
            "Analysis date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="advanced_dates"
        )
        
        if selected_cats_advanced and len(adv_date_range) == 2:
            # Get comprehensive metrics
            start_dt = pd.to_datetime(adv_date_range[0])
            end_dt = pd.to_datetime(adv_date_range[1])
            
            metrics = analyzer.calculate_category_metrics(
                selected_categories=selected_cats_advanced,
                date_range=(start_dt, end_dt)
            )
            
            if 'error' not in metrics:
                # Display summary
                st.subheader("📊 Summary Overview")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Spending", f"${metrics['summary']['total_spending']:,.2f}")
                with col2:
                    st.metric("Total Transactions", f"{metrics['summary']['total_transactions']:,}")
                with col3:
                    st.metric("Categories", f"{metrics['summary']['categories_count']}")
                with col4:
                    st.metric("Analysis Days", f"{metrics['summary']['date_range']['days']}")
                
                # Detailed category statistics
                st.subheader("📋 Detailed Category Statistics")
                category_stats = metrics['category_stats']
                
                # Format the dataframe for better display
                display_stats = category_stats.copy()
                for col in ['total', 'avg', 'std', 'min', 'max']:
                    if col in display_stats.columns:
                        display_stats[col] = display_stats[col].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(display_stats, use_container_width=True)
                
                # Monthly trends visualization
                if not metrics['monthly_trends'].empty:
                    st.subheader("📈 Monthly Trends")
                    fig = px.line(
                        metrics['monthly_trends'],
                        x='month',
                        y='amount',
                        color='category',
                        title="Monthly Spending Trends by Category",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Weekly patterns
                if not metrics['weekly_patterns'].empty:
                    st.subheader("📅 Weekly Spending Patterns")
                    fig = px.bar(
                        metrics['weekly_patterns'],
                        x='day_of_week',
                        y='amount',
                        color='category',
                        title="Average Daily Spending by Category",
                        barmode='group'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(metrics['error'])
    
    with tab3:
        st.subheader("⚖️ Period Comparison")
        
        # Category selection for comparison
        comparison_category = st.selectbox(
            "Select category to compare:",
            options=all_categories,
            key="comparison_category"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Period 1:**")
            # Calculate safe default period 1 dates
            period1_end = min(min_date + pd.Timedelta(days=30), max_date)
            period1_dates = st.date_input(
                "First period:",
                value=(min_date, period1_end),
                min_value=min_date,
                max_value=max_date,
                key="period1"
            )
        
        with col2:
            st.write("**Period 2:**")
            # Calculate safe default period 2 dates
            period2_start = max(max_date - pd.Timedelta(days=30), min_date)
            period2_dates = st.date_input(
                "Second period:",
                value=(period2_start, max_date),
                min_value=min_date,
                max_value=max_date,
                key="period2"
            )
        
        if len(period1_dates) == 2 and len(period2_dates) == 2:
            # Perform comparison
            period1_dt = (pd.to_datetime(period1_dates[0]), pd.to_datetime(period1_dates[1]))
            period2_dt = (pd.to_datetime(period2_dates[0]), pd.to_datetime(period2_dates[1]))
            
            comparison = analyzer.compare_category_periods(
                comparison_category, period1_dt, period2_dt
            )
            
            st.subheader(f"📊 Comparison Results for {comparison_category}")
            
            # Display comparison metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Spending Change",
                    f"{comparison['changes']['total_change_pct']:+.1f}%",
                    delta=f"${comparison['period2']['total'] - comparison['period1']['total']:+,.2f}"
                )
            
            with col2:
                st.metric(
                    "Transaction Count Change",
                    f"{comparison['changes']['count_change_pct']:+.1f}%",
                    delta=f"{comparison['period2']['count'] - comparison['period1']['count']:+d}"
                )
            
            with col3:
                st.metric(
                    "Average Amount Change",
                    f"{comparison['changes']['avg_change_pct']:+.1f}%",
                    delta=f"${comparison['period2']['avg'] - comparison['period1']['avg']:+,.2f}"
                )
            
            # Detailed comparison table
            comparison_data = {
                'Metric': ['Total Spending', 'Transaction Count', 'Average Amount', 'Period Length (days)'],
                'Period 1': [
                    f"${comparison['period1']['total']:,.2f}",
                    comparison['period1']['count'],
                    f"${comparison['period1']['avg']:,.2f}",
                    comparison['period1']['days']
                ],
                'Period 2': [
                    f"${comparison['period2']['total']:,.2f}",
                    comparison['period2']['count'],
                    f"${comparison['period2']['avg']:,.2f}",
                    comparison['period2']['days']
                ]
            }
            
            st.subheader("📋 Detailed Comparison")
            st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
    
    with tab4:
        st.subheader("🔮 Category Spending Predictions")
        
        # Category selection for predictions
        prediction_category = st.selectbox(
            "Select category for prediction:",
            options=all_categories,
            key="prediction_category"
        )
        
        months_ahead = st.slider(
            "Months to predict:",
            min_value=1,
            max_value=12,
            value=3,
            help="Number of months ahead to predict"
        )
        
        if st.button("Generate Prediction", type="primary"):
            prediction = analyzer.get_category_predictions(prediction_category, months_ahead)
            
            if 'error' not in prediction:
                st.subheader(f"📈 Predictions for {prediction_category}")
                
                # Display prediction metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Historical Average", f"${prediction['historical_avg']:,.2f}")
                with col2:
                    trend_direction = "📈" if prediction['trend'] > 0 else "📉" if prediction['trend'] < 0 else "➡️"
                    st.metric("Monthly Trend", f"{trend_direction} ${prediction['trend']:+,.2f}")
                with col3:
                    total_predicted = sum([p['predicted_amount'] for p in prediction['predictions']])
                    st.metric(f"Total {months_ahead}M Predicted", f"${total_predicted:,.2f}")
                
                # Predictions table
                st.subheader("📅 Monthly Predictions")
                pred_df = pd.DataFrame(prediction['predictions'])
                pred_df['predicted_amount'] = pred_df['predicted_amount'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(pred_df, use_container_width=True)
                
                # Visualization
                pred_viz_df = pd.DataFrame(prediction['predictions'])
                fig = px.line(
                    pred_viz_df,
                    x='month',
                    y='predicted_amount',
                    title=f"Predicted Spending for {prediction_category}",
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Predicted Amount ($)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Disclaimer
                st.info("📝 **Note**: Predictions are based on historical trends and should be used as estimates only.")
            else:
                st.error(prediction['error'])

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

def show_data_preview_page():
    """Dedicated Data Preview page with advanced pagination and filtering"""
    st.header("📊 Data Preview")
    
    df = st.session_state.df.copy()
    
    # Data overview metrics
    st.subheader("📈 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Date Range", f"{(df['date'].max() - df['date'].min()).days} days")
    with col3:
        st.metric("Total Amount", f"${df['amount'].sum():,.2f}")
    with col4:
        st.metric("Categories", df['category'].nunique())
    
    # Advanced filtering options
    st.subheader("🔍 Filter Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Date range filter
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        date_range = st.date_input(
            "Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="preview_date_range"
        )
    
    with col2:
        # Category filter - ensure all categories are strings before sorting
        unique_categories = df['category'].dropna().astype(str).unique().tolist()
        all_categories = ['All'] + sorted(unique_categories)
        selected_category = st.selectbox(
            "Category:",
            options=all_categories,
            key="preview_category"
        )
    
    with col3:
        # Amount range filter
        min_amount = float(df['amount'].min())
        max_amount = float(df['amount'].max())
        amount_range = st.slider(
            "Amount Range ($):",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount),
            step=0.01,
            key="preview_amount_range"
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= start_date) & 
            (filtered_df['date'].dt.date <= end_date)
        ]
    
    # Category filter
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    # Amount filter
    filtered_df = filtered_df[
        (filtered_df['amount'] >= amount_range[0]) & 
        (filtered_df['amount'] <= amount_range[1])
    ]
    
    # Show filter results
    if len(filtered_df) != len(df):
        st.info(f"📊 Showing {len(filtered_df):,} records (filtered from {len(df):,} total)")
    
    # Search functionality
    st.subheader("🔍 Search in Description")
    search_term = st.text_input(
        "Search descriptions:",
        placeholder="Enter keywords to search in transaction descriptions...",
        key="preview_search"
    )
    
    if search_term:
        search_mask = filtered_df['description'].str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[search_mask]
        st.info(f"🔍 Found {len(filtered_df):,} records matching '{search_term}'")
    
    # Sorting options
    col1, col2 = st.columns(2)
    with col1:
        sort_column = st.selectbox(
            "Sort by:",
            options=['date', 'amount', 'category', 'description'],
            index=0,
            key="preview_sort_column"
        )
    
    with col2:
        sort_order = st.radio(
            "Order:",
            options=['Newest First', 'Oldest First'] if sort_column == 'date' 
                   else ['Highest First', 'Lowest First'] if sort_column == 'amount'
                   else ['A to Z', 'Z to A'],
            horizontal=True,
            key="preview_sort_order"
        )
    
    # Apply sorting
    ascending = sort_order in ['Oldest First', 'Lowest First', 'A to Z']
    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)
    
    # Pagination
    st.subheader("📄 Data Table")
    
    if len(filtered_df) > 0:
        # Pagination settings
        records_per_page = 20
        total_records = len(filtered_df)
        total_pages = (total_records - 1) // records_per_page + 1 if total_records > 0 else 1
        
        # Page navigation
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⬅️ First", disabled=(st.session_state.get('preview_page', 1) <= 1)):
                st.session_state.preview_page = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ Prev", disabled=(st.session_state.get('preview_page', 1) <= 1)):
                st.session_state.preview_page = max(1, st.session_state.get('preview_page', 1) - 1)
                st.rerun()
        
        with col3:
            # Initialize page in session state if not exists
            if 'preview_page' not in st.session_state:
                st.session_state.preview_page = 1
            
            current_page = st.selectbox(
                "Page:",
                options=list(range(1, total_pages + 1)),
                index=st.session_state.preview_page - 1,
                format_func=lambda x: f"Page {x} of {total_pages}",
                key="preview_page_select"
            )
            
            if current_page != st.session_state.preview_page:
                st.session_state.preview_page = current_page
                st.rerun()
        
        with col4:
            if st.button("▶️ Next", disabled=(st.session_state.get('preview_page', 1) >= total_pages)):
                st.session_state.preview_page = min(total_pages, st.session_state.get('preview_page', 1) + 1)
                st.rerun()
        
        with col5:
            if st.button("➡️ Last", disabled=(st.session_state.get('preview_page', 1) >= total_pages)):
                st.session_state.preview_page = total_pages
                st.rerun()
        
        # Calculate pagination
        current_page = st.session_state.get('preview_page', 1)
        start_idx = (current_page - 1) * records_per_page
        end_idx = min(start_idx + records_per_page, total_records)
        
        # Show current page data
        page_df = filtered_df.iloc[start_idx:end_idx].copy()
        
        # Format data for display
        display_df = page_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
        
        # Display the table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": st.column_config.TextColumn("Date", width="small"),
                "amount": st.column_config.TextColumn("Amount", width="small"),
                "category": st.column_config.TextColumn("Category", width="medium"),
                "description": st.column_config.TextColumn("Description", width="large"),
            }
        )
        
        # Pagination info
        st.caption(f"📄 Showing records {start_idx + 1}-{end_idx} of {total_records:,} | Page {current_page} of {total_pages}")
        
        # Quick stats for current page
        if len(page_df) > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Page Total", f"${page_df['amount'].sum():,.2f}")
            with col2:
                st.metric("Page Average", f"${page_df['amount'].mean():.2f}")
            with col3:
                st.metric("Records on Page", len(page_df))
    
    else:
        st.warning("❌ No records match your current filters.")
        st.info("💡 Try adjusting your filters or search terms to see more data.")
    
    # Export current view
    st.subheader("💾 Export Current View")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Filtered Data as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"bill_analysis_filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Copy Current Page"):
            page_csv = page_df.to_csv(index=False)
            st.code(page_csv, language="csv")
            st.caption("Copy the CSV data above to paste into Excel or other applications")


if __name__ == "__main__":
    main()