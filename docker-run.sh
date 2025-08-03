#!/bin/bash
# Quick Docker build and run script for Bill Analysis

echo "🐳 Building Bill Analysis Docker image..."
docker build -t bill-analysis:latest .

echo "🚀 Starting Bill Analysis container..."
docker run -d \
  --name bill-analysis-app \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/exports:/app/exports \
  -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
  -e STREAMLIT_SERVER_PORT=8501 \
  -e STREAMLIT_SERVER_HEADLESS=true \
  bill-analysis:latest

echo "✅ Container started! Access your app at: http://localhost:8501"

# Follow logs
echo "📋 Following container logs (Ctrl+C to exit)..."
docker logs -f bill-analysis-app