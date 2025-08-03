# 🌐 Environment Setup Guide

The Bill Analysis application now automatically detects and optimizes for different deployment environments.

## 🔍 **Environment Detection**

The application automatically detects:
- **🌐 Streamlit Cloud**: Uses cached Chrome driver with Chromium
- **🐳 Docker**: Uses system Chrome binaries and drivers
- **🖥️ Local**: Uses webdriver-manager for automatic setup

## 🌐 **Streamlit Cloud Setup**

### **Requirements**
Make sure your `requirements.txt` includes:
```txt
streamlit>=1.20.0
selenium>=4.0.0
webdriver-manager>=3.8.0
```

### **Deployment Steps**
1. **Connect Repository**:
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Connect your GitHub account
   - Select repository: `TheBananaWolf/BillAnalysisDashboard`
   - Set main file: `main.py`
   - Set Python version: `3.11`

2. **Environment Variables** (Optional):
   - Set `STREAMLIT_SHARING_URL` to your app URL for better detection

3. **Deploy**:
   - Click "Deploy!"
   - Wait 3-5 minutes for initial deployment
   - Auto-deploys on every push to main branch

### **Optimizations Applied**
- ✅ `@st.cache_resource` for driver caching
- ✅ `ChromeType.CHROMIUM` for cloud compatibility
- ✅ Optimized Chrome options for cloud resources
- ✅ Automatic ChromeDriver management

## 🐳 **Docker Setup**

### **Environment Variables**
Your Dockerfile already sets these:
```dockerfile
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### **Installation**
Chrome/Chromium installed via:
```dockerfile
RUN apt-get install chromium chromium-driver
```

### **Running**
```bash
# Build and run
docker-compose up --build -d

# Or manually
docker build -t bill-analysis .
docker run -d -p 8501:8501 bill-analysis
```

### **Optimizations Applied**
- ✅ Uses system Chrome binaries
- ✅ No driver downloads needed
- ✅ Optimized for container resources
- ✅ Fast startup time

## 🖥️ **Local Development**

### **Prerequisites**
Install Chrome or Chromium:

**macOS:**
```bash
brew install google-chrome
# or
brew install chromium
```

**Ubuntu/Debian:**
```bash
sudo apt-get install google-chrome-stable
# or
sudo apt-get install chromium-browser
```

**Windows:**
- Download and install Google Chrome
- Or download Chromium

### **Running**
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run main.py
```

### **Optimizations Applied**
- ✅ Automatic ChromeDriver download
- ✅ webdriver-manager handles versions
- ✅ Fallback to system Chrome if needed
- ✅ No manual configuration required

## 🧪 **Testing Your Environment**

Run the environment test script:
```bash
python test_environment.py
```

This will:
- Detect your current environment
- Test Chrome WebDriver setup
- Show specific recommendations
- Validate all dependencies

## 🔧 **Troubleshooting**

### **Streamlit Cloud Issues**
1. **Driver fails to start**:
   - Check if `webdriver-manager` is in requirements.txt
   - Verify Python version is 3.11
   - Check Streamlit Cloud resource limits

2. **Import errors**:
   - Ensure all Selenium dependencies are included
   - Check requirements.txt format

### **Docker Issues**
1. **Chrome not found**:
   - Verify Dockerfile installs `chromium chromium-driver`
   - Check environment variables are set
   - Ensure base image supports Chrome

2. **Permission errors**:
   - Add `--no-sandbox` flag (already included)
   - Check container user permissions

### **Local Issues**
1. **Chrome not found**:
   - Install Google Chrome or Chromium
   - Ensure Chrome is in system PATH
   - Try manual webdriver-manager install

2. **Version conflicts**:
   - Update Chrome to latest version
   - Clear webdriver-manager cache: `~/.wdm/`

## 📊 **Environment Comparison**

| Feature | Streamlit Cloud | Docker | Local |
|---------|----------------|---------|-------|
| **Setup Time** | ~3 minutes | ~30 seconds | ~10 seconds |
| **Driver Management** | Automatic (cached) | System binaries | Automatic download |
| **Resource Usage** | Optimized for cloud | Container-optimized | Full resources |
| **Debugging** | Limited logs | Full logs | Full access |
| **Update Method** | Git push | Docker rebuild | Code changes |

## 🎯 **Recommended Workflow**

1. **Development**: Use local environment for fast iteration
2. **Testing**: Use Docker for production-like testing
3. **Production**: Deploy to Streamlit Cloud for public access

## 🚀 **Quick Start**

**For Streamlit Cloud:**
```bash
# Just push to GitHub and connect repository!
git push origin main
```

**For Docker:**
```bash
docker-compose up --build -d
```

**For Local:**
```bash
streamlit run main.py
```

All environments will automatically optimize themselves for the best Chrome WebDriver experience! 🎉