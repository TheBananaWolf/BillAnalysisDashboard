# 💰 Bill Analysis System

A comprehensive financial analysis application that helps you understand your spending patterns, identify trends, and generate insights from your bill/transaction data.

## ✨ Features

### 📊 Data Analysis
- **Spending Pattern Analysis**: Identify trends and patterns in your financial behavior
- **Category Breakdown**: Categorize and analyze expenses by type
- **Temporal Analysis**: Understand spending patterns by day, week, month, and season
- **Anomaly Detection**: Identify unusual transactions and spending spikes
- **Financial Health Assessment**: Get insights into your financial habits

### 📈 Visualizations
- Interactive charts and graphs using Plotly
- Monthly spending trends
- Category distribution (pie charts, treemaps)
- Daily spending patterns
- Spending velocity analysis
- Heatmaps and radar charts

### 🤖 AI-Powered Insights
- Automatic spending categorization
- Personalized financial recommendations
- Savings opportunity identification
- Budget suggestions based on historical data
- Financial health scoring

### 🌐 Data Sources
- **File Upload**: CSV, Excel, JSON files
- **Notion Integration**: Direct scraping from Notion pages
- **Sample Data**: Built-in demo data for testing

### 📱 Web Interface
- Clean, intuitive Streamlit-based UI
- Interactive dashboards
- Real-time data processing
- Export capabilities

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd BillAnalysis
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:8501`

### Option 2: Local Installation

1. **Install Python 3.11+**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome/Chromium** (for Notion scraping):
   - **Ubuntu/Debian**: `sudo apt-get install google-chrome-stable`
   - **macOS**: Download from Google Chrome website
   - **Windows**: Download from Google Chrome website

4. **Run the application**:
   ```bash
   streamlit run main.py
   ```

5. **Access the application**:
   Open your browser and go to `http://localhost:8501`

## 📋 Usage Guide

### 1. Data Upload

The application supports three data input methods:

#### File Upload
- Supported formats: CSV, Excel (.xlsx, .xls), JSON
- Required columns: `date`, `amount`, `description`
- Optional columns: `category`, `account`, `type`

#### Notion Page Scraping
1. Ensure your Notion page is publicly accessible
2. Create a table/database with transaction data
3. Include columns for Date, Amount, Description (minimum)
4. Copy the page URL and paste it in the application
5. Click "Scrape Data from Notion"

#### Sample Data
- Use built-in sample data to explore features
- Perfect for testing and demonstration

### 2. Data Format Requirements

Your data should include these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| date | Yes | Transaction date | 2024-01-15, 01/15/2024 |
| amount | Yes | Transaction amount | 25.50, 100.00 |
| description | Yes | Transaction description | "Starbucks Coffee", "Grocery Store" |
| category | No | Expense category | "Food & Dining", "Transportation" |
| account | No | Account name | "Main Checking", "Credit Card" |
| type | No | Transaction type | "Expense", "Income" |

### 3. Application Features

#### Overview Dashboard
- Total spending summary
- Key financial metrics
- Monthly trends
- Category distribution

#### Spending Analysis
- Detailed transaction analysis
- Filtering capabilities
- Top transactions
- Weekly patterns

#### Category Analysis
- Spending by category
- Category trends over time
- Category comparisons

#### Trends Analysis
- Monthly and yearly trends
- Seasonal patterns
- Growth rate analysis

#### AI Insights
- Automated financial insights
- Spending pattern analysis
- Savings recommendations
- Budget suggestions

#### Export & Reports
- Generate detailed reports
- Export data in various formats
- Custom analysis reports

## 🔧 Configuration

### Environment Variables

```bash
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Docker Configuration

The application uses Docker for easy deployment. The included `docker-compose.yml` provides:

- Automatic dependency installation
- Chrome/ChromeDriver setup for web scraping
- Volume mapping for data persistence
- Health checks

## 📁 Project Structure

```
BillAnalysis/
├── main.py                    # Main Streamlit application
├── src/                       # Source code modules
│   ├── __init__.py
│   ├── data_processor.py      # Data loading and processing
│   ├── analyzer.py            # Financial analysis engine
│   ├── visualizer.py          # Chart and graph generation
│   ├── insights_generator.py  # AI insights and recommendations
│   └── notion_scraper.py      # Notion web scraping
├── data/                      # Data storage directory
├── exports/                   # Export output directory
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
└── README.md                  # This file
```

## 🛠️ Technical Stack

- **Backend**: Python 3.11+
- **Web Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Web Scraping**: Selenium, BeautifulSoup, Requests
- **Containerization**: Docker, Docker Compose

## 🔐 Security & Privacy

- All data processing happens locally or in your container
- No data is sent to external services (except for Notion scraping)
- Notion scraping only accesses publicly shared pages
- Data files are stored locally in the `data/` directory

## 🐛 Troubleshooting

### Common Issues

1. **Notion Scraping Fails**:
   - Ensure the page is publicly accessible
   - Check that data is in a table format
   - Try exporting from Notion as CSV instead

2. **Chrome/ChromeDriver Issues**:
   - Make sure Chrome is installed
   - Update ChromeDriver if needed
   - Use Docker version for consistent environment

3. **Data Loading Errors**:
   - Check column names match requirements
   - Ensure date formats are recognizable
   - Verify amount columns contain numeric data

4. **Memory Issues with Large Files**:
   - Consider splitting large files
   - Use CSV format for better performance
   - Increase Docker memory limits if needed

### Getting Help

1. Check the troubleshooting section in the app
2. Review the data format requirements
3. Try the sample data to ensure the app works
4. Check Docker logs: `docker-compose logs`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Streamlit for the amazing web framework
- Plotly for interactive visualizations
- Pandas for data processing capabilities
- The open-source community for all the great libraries

---

**Happy Financial Analysis! 💰📊**# Test Auto-Deployment
