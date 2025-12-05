#!/bin/bash
# Start both API and Frontend servers

echo "🚀 Starting SeaRates AI Servers..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv_ai_model" ]; then
    echo "📦 Activating virtual environment..."
    source venv_ai_model/bin/activate
fi

# Check if API server is already running
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ API server already running on port 5001"
else
    echo "🔌 Starting API server on port 5001..."
    python3 api_server.py > api_server.log 2>&1 &
    API_PID=$!
    echo "   API server started (PID: $API_PID)"
    echo "   Logs: api_server.log"
    sleep 3
    
    # Verify it started
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo "   ✅ API server is ready"
    else
        echo "   ⚠️  API server may still be starting..."
    fi
fi

# Check if frontend is already running on 5002
if curl -s http://localhost:5002 > /dev/null 2>&1; then
    echo "✅ Frontend already running on port 5002"
else
    echo "🌐 Starting frontend server on port 5002..."
    cd frontend
    python3 -m http.server 5002 > ../frontend_server.log 2>&1 &
    FRONTEND_PID=$!
    echo "   Frontend server started (PID: $FRONTEND_PID)"
    echo "   Logs: frontend_server.log"
    cd ..
    sleep 2
    
    # Verify it started
    if curl -s http://localhost:5002 > /dev/null 2>&1; then
        echo "   ✅ Frontend server is ready"
    else
        echo "   ⚠️  Frontend server may still be starting..."
    fi
fi

echo ""
echo "=========================================="
echo "✅ Servers are running!"
echo ""
echo "🌐 Frontend UI: http://localhost:5002"
echo "🔌 API Server:  http://localhost:5001"
echo "📚 API Docs:     http://localhost:5001/docs"
echo ""
echo "To stop servers:"
echo "  pkill -f 'api_server.py'"
echo "  pkill -f 'http.server 5002'"
echo "=========================================="

