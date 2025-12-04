#!/bin/bash
# Simple script to run the API server

echo "🚀 Starting SeaRates AI API Server..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv_ai_model" ]; then
    echo "📦 Activating virtual environment..."
    source venv_ai_model/bin/activate
fi

# Check Python version
echo "🐍 Python version:"
python3 --version
echo ""

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if python3 -c "import fastapi" 2>/dev/null; then
    echo "✅ FastAPI is installed"
else
    echo "❌ FastAPI is not installed"
    echo "   Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting API server on http://localhost:5001"
echo "   Health check: http://localhost:5001/health"
echo "   API docs: http://localhost:5001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 api_server.py

