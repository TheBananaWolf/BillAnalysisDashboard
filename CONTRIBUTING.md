# Contributing to Bill Analysis Dashboard

Thank you for your interest in contributing to the Bill Analysis Dashboard! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- Git

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TheBananaWolf/BillAnalysisDashboard.git
   cd BillAnalysisDashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   # or
   streamlit run main.py
   ```

4. **Docker setup (optional):**
   ```bash
   docker-compose up --build
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add docstrings for all functions and classes
- Keep functions focused and modular

### Project Structure
```
BillAnalysisDashboard/
├── main.py                    # Main Streamlit application
├── src/                       # Source code modules
│   ├── data_processor.py      # Data loading and processing
│   ├── analyzer.py            # Financial analysis engine
│   ├── visualizer.py          # Charts and visualizations
│   ├── insights_generator.py  # AI insights and recommendations
│   └── notion_scraper.py      # Notion web scraping
├── Dockerfile & docker-compose.yml
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## 🐛 Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)
- Environment details (OS, Python version)

## ✨ Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists
- Describe the use case and benefits
- Provide examples of how it would work

## 🔧 Pull Request Process

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes:**
   - Write clear, documented code
   - Add tests if applicable
   - Update documentation

4. **Test your changes:**
   ```bash
   # Test locally
   python run.py
   
   # Test with Docker
   docker-compose up --build
   ```

5. **Commit your changes:**
   ```bash
   git commit -m "feat: add your feature description"
   ```

6. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

### Commit Message Format
Use conventional commits:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` formatting changes
- `refactor:` code refactoring
- `test:` adding tests
- `chore:` maintenance tasks

## 🧪 Testing

- Test with sample data and real Notion pages
- Verify Docker containerization works
- Check all visualization components
- Test different data formats (CSV, Excel, JSON)

## 📝 Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features

## 🤝 Areas for Contribution

### High Priority
- [ ] Additional data source integrations (Google Sheets, bank APIs)
- [ ] More sophisticated categorization algorithms
- [ ] Advanced budget tracking and alerts
- [ ] Mobile-responsive design improvements

### Medium Priority
- [ ] Export to more formats (PDF reports, Excel dashboards)
- [ ] Multi-currency support
- [ ] Batch processing for large datasets
- [ ] Performance optimizations

### Documentation & Testing
- [ ] Comprehensive test suite
- [ ] Video tutorials
- [ ] API documentation
- [ ] Deployment guides for various platforms

## 📞 Getting Help

- Open an issue for questions
- Check existing issues and documentation
- Review the code structure in STRUCTURE.md

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to the Bill Analysis Dashboard! 🎉