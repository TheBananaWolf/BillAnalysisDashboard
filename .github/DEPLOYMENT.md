# 🚀 Deployment Guide

This guide covers how to deploy your Bill Analysis application using GitHub Actions to various platforms.

## 🎯 Quick Setup

### 1. Enable GitHub Actions
- ✅ Actions are automatically enabled in your repository
- ✅ Workflows will run on every push to `main` branch
- ✅ Pull requests will trigger testing workflows

### 2. Choose Your Deployment Platform

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free & Easy)

**Best for**: Quick deployment, free hosting, automatic updates

#### Setup Steps:
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Connect your GitHub account
3. Select this repository: `{your-username}/BillAnalysis`
4. Set main file: `main.py`
5. Deploy! 🚀

#### GitHub Variables to Set:
```bash
STREAMLIT_SHARING_URL = "https://your-app-name.streamlit.app"
```

---

### Option 2: Railway (Recommended - Paid)

**Best for**: Production apps, custom domains, better performance

#### Setup Steps:
1. Go to [railway.app](https://railway.app/)
2. Connect your GitHub account
3. Import this repository
4. Railway will automatically detect the Dockerfile
5. Deploy! 🚀

#### GitHub Secrets to Set:
```bash
RAILWAY_TOKEN = "your-railway-token"
```

#### GitHub Variables to Set:
```bash
RAILWAY_PROJECT_ID = "your-project-id"
RAILWAY_URL = "https://your-app.railway.app"
```

---

### Option 3: Heroku

**Best for**: Established platform, lots of integrations

#### Setup Steps:
1. Create a Heroku account
2. Create a new app
3. Get your API key from Account Settings

#### GitHub Secrets to Set:
```bash
HEROKU_API_KEY = "your-heroku-api-key"
```

#### GitHub Variables to Set:
```bash
HEROKU_APP_NAME = "your-app-name"
HEROKU_EMAIL = "your-email@example.com"
HEROKU_URL = "https://your-app-name.herokuapp.com"
```

---

### Option 4: Docker Hub + Any Cloud Provider

**Best for**: Maximum flexibility, multi-cloud deployment

#### What GitHub Actions Does:
- ✅ Builds Docker image
- ✅ Pushes to GitHub Container Registry
- ✅ Creates multi-platform images (AMD64, ARM64)
- ✅ Tags with branch and commit info

#### Container Registry:
```bash
ghcr.io/{your-username}/billanalysis:latest
```

#### Deploy Anywhere:
```bash
docker run -p 8501:8501 ghcr.io/{your-username}/billanalysis:latest
```

---

## ⚙️ GitHub Repository Configuration

### 1. Set Repository Secrets
Go to: **Settings** → **Secrets and variables** → **Actions**

#### Required for Railway:
- `RAILWAY_TOKEN`: Your Railway API token

#### Required for Heroku:
- `HEROKU_API_KEY`: Your Heroku API key

### 2. Set Repository Variables
Go to: **Settings** → **Secrets and variables** → **Actions** → **Variables**

#### Optional Configuration:
- `STREAMLIT_SHARING_URL`: Your Streamlit Cloud app URL
- `RAILWAY_PROJECT_ID`: Your Railway project ID
- `RAILWAY_URL`: Your Railway app URL
- `HEROKU_APP_NAME`: Your Heroku app name
- `HEROKU_EMAIL`: Your Heroku account email
- `HEROKU_URL`: Your Heroku app URL
- `DOCS_DOMAIN`: Custom domain for documentation (optional)

---

## 🔧 Workflow Details

### CI/CD Pipeline (`ci-cd.yml`)
**Triggers**: Push to `main`, Pull Requests
**Actions**:
- 🧪 Run tests and linting
- 🐳 Build Docker image
- 📦 Push to container registry
- 🚀 Deploy to configured platforms
- 📊 Generate deployment summary

### Code Quality (`code-quality.yml`)
**Triggers**: Push, Pull Requests, Weekly schedule
**Actions**:
- 🎨 Code formatting (Black)
- 📋 Import sorting (isort)
- 🔍 Linting (flake8)
- 🔒 Security audit (bandit)
- 🛡️ Dependency vulnerability check

### Documentation (`docs.yml`)
**Triggers**: Push to `main`, Manual trigger
**Actions**:
- 📖 Generate API documentation
- 📝 Create project documentation
- 🌐 Deploy to GitHub Pages

### Streamlit Deploy (`streamlit-deploy.yml`)
**Triggers**: Push to `main`, Manual trigger
**Actions**:
- ✅ Validate Streamlit app
- 📋 Create deployment info
- 🎯 Prepare for Streamlit Cloud

---

## 📊 Monitoring and Logs

### GitHub Actions Logs
- View workflow runs in the **Actions** tab
- Check deployment status and logs
- Monitor build times and success rates

### Application Logs
- **Streamlit Cloud**: View logs in Streamlit dashboard
- **Railway**: Use Railway dashboard or CLI
- **Heroku**: Use Heroku dashboard or CLI
- **Docker**: Use `docker logs container-name`

---

## 🚨 Troubleshooting

### Common Issues:

#### 1. Build Fails
- Check Python dependencies in `requirements.txt`
- Verify Docker configuration
- Review GitHub Actions logs

#### 2. Deployment Fails
- Verify secrets and variables are set correctly
- Check platform-specific requirements
- Ensure repository is public (for free tiers)

#### 3. App Doesn't Start
- Check application logs
- Verify environment variables
- Test locally with Docker first

#### 4. Notion Scraping Issues
- Ensure Notion page is publicly accessible
- Check if page structure has changed
- Verify Chrome/ChromeDriver compatibility

---

## 🎉 Success!

Once deployed, your application will:
- ✅ Auto-deploy on every push to `main`
- ✅ Run comprehensive tests before deployment
- ✅ Generate documentation automatically
- ✅ Monitor code quality and security
- ✅ Update dependencies automatically

### Next Steps:
1. Choose your deployment platform
2. Set up the required secrets/variables
3. Push to `main` branch
4. Watch the magic happen! ✨

---

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs first
2. Review this deployment guide
3. Check platform-specific documentation
4. Create an issue in the repository

Happy deploying! 🚀