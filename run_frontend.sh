#!/bin/bash
# Simple script to run the frontend

echo "🚀 Starting SeaRates AI Frontend..."
echo ""

# Check if virtual environment exists
if [ -d "venv_ai_model" ]; then
    echo "📦 Activating virtual environment..."
    source venv_ai_model/bin/activate
fi

# Check if API server is running
echo "🔍 Checking API server..."
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ API server is running on http://localhost:5001"
else
    echo "⚠️  API server is NOT running on http://localhost:5001"
    echo ""
    echo "Please start the API server first in another terminal:"
    echo "  source venv_ai_model/bin/activate"
    echo "  python api_server.py"
    echo ""
    read -p "Press Enter to continue anyway (frontend will not work without API server)..."
fi

# Start frontend server
echo ""
echo "📦 Starting frontend web server on http://localhost:8080"
echo "   Open this URL in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
python3 -m http.server 8080

