#!/bin/bash
# Stop and cleanup Bill Analysis Docker containers

echo "🛑 Stopping Bill Analysis container..."
docker stop bill-analysis-app 2>/dev/null || echo "Container not running"

echo "🗑️ Removing Bill Analysis container..."
docker rm bill-analysis-app 2>/dev/null || echo "Container not found"

echo "📦 Removing Bill Analysis image (optional)..."
read -p "Remove Docker image? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rmi bill-analysis:latest 2>/dev/null || echo "Image not found"
    echo "✅ Image removed"
else
    echo "📦 Image kept for future use"
fi

echo "🧹 Cleaning up unused Docker resources..."
docker system prune -f

echo "✅ Cleanup complete!"