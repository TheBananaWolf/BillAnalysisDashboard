# Project Structure

## Complete Bill Analysis System

```
BillAnalysis/
│
├── 🐳 Docker & Deployment
│   ├── Dockerfile                 # Docker container configuration
│   ├── docker-compose.yml         # Docker Compose setup
│   └── .env.example               # Environment variables template
│
├── 🚀 Quick Start Scripts
│   ├── run.py                     # Python quick start script
│   └── run.sh                     # Bash quick start script
│
├── 📱 Main Application
│   └── main.py                    # Streamlit web interface
│
├── 🔧 Source Code Modules
│   └── src/
│       ├── __init__.py            # Package initialization
│       ├── data_processor.py      # Data loading & preprocessing
│       ├── analyzer.py            # Financial analysis engine
│       ├── visualizer.py          # Charts & visualizations
│       ├── insights_generator.py  # AI insights & recommendations
│       └── notion_scraper.py      # Notion web scraping
│
├── 💾 Data Storage
│   ├── data/                      # User data storage
│   └── exports/                   # Export outputs
│
├── 📋 Configuration
│   ├── requirements.txt           # Python dependencies
│   └── .env.example              # Environment configuration
│
└── 📚 Documentation
    ├── README.md                  # Main documentation
    └── STRUCTURE.md               # This file
```

## Key Features by File

### 📱 **main.py** - Web Interface
- Streamlit-based dashboard
- Multi-page navigation
- Data upload interface
- Notion URL integration
- Interactive visualizations
- Export functionality

### 🔧 **src/data_processor.py** - Data Processing
- File format support (CSV, Excel, JSON)
- Notion URL data extraction
- Data cleaning and validation
- Automatic categorization
- Sample data generation

### 📊 **src/analyzer.py** - Analysis Engine
- Monthly/yearly spending analysis
- Category breakdowns
- Trend detection
- Anomaly identification
- Growth rate calculations
- Financial health metrics

### 📈 **src/visualizer.py** - Visualization
- Interactive Plotly charts
- Monthly spending trends
- Category distributions
- Daily patterns
- Heatmaps and radar charts
- Timeline visualizations

### 🧠 **src/insights_generator.py** - AI Insights
- Spending pattern analysis
- Personalized recommendations
- Savings opportunity detection
- Budget suggestions
- Financial health assessment

### 🌐 **src/notion_scraper.py** - Web Scraping
- Selenium-based web scraping
- Notion page data extraction
- Multiple fallback methods
- Data format standardization
- Error handling and recovery

## Data Flow

```
1. Data Input
   ├── File Upload (CSV/Excel/JSON)
   ├── Notion URL Scraping
   └── Sample Data Generation
   
2. Data Processing
   ├── Format Standardization
   ├── Data Cleaning
   ├── Validation
   └── Categorization
   
3. Analysis
   ├── Statistical Analysis
   ├── Trend Detection
   ├── Pattern Recognition
   └── Anomaly Detection
   
4. Visualization
   ├── Interactive Charts
   ├── Dashboards
   ├── Reports
   └── Exports
   
5. Insights
   ├── AI-Generated Insights
   ├── Recommendations
   ├── Budget Suggestions
   └── Health Metrics
```

## Technology Stack

- **Backend**: Python 3.11+
- **Web Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Web Scraping**: Selenium, BeautifulSoup, Requests
- **Containerization**: Docker, Docker Compose
- **Dependencies**: See requirements.txt

## Deployment Options

1. **Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```

2. **Local Python**
   ```bash
   python run.py
   # or
   ./run.sh
   ```

3. **Manual Setup**
   ```bash
   pip install -r requirements.txt
   streamlit run main.py
   ```