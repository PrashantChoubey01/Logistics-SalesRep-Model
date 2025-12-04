#!/bin/bash
# Quick start script for frontend development

echo "🚀 Starting SeaRates AI Frontend..."
echo ""

# Check if API server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  API server is not running on http://localhost:8000"
    echo "   Please start it first with: python api_server.py"
    echo ""
    read -p "Do you want to start the API server now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting API server in background..."
        python api_server.py &
        sleep 3
        echo "✅ API server started"
    else
        echo "❌ Cannot start frontend without API server"
        exit 1
    fi
fi

# Start frontend server
echo "📦 Starting frontend web server..."
cd frontend
python3 -m http.server 8080

