#!/bin/bash
# Docker entrypoint script for Logistics AI Bot

set -e

echo "Starting Logistics AI Bot..."
echo ""

# Check if required environment variables are set
if [ -z "$DATABRICKS_TOKEN" ]; then
    echo "ERROR: DATABRICKS_TOKEN environment variable is not set!"
    echo ""
    echo "Please run the container with:"
    echo "  docker run -e DATABRICKS_TOKEN=your_token_here ..."
    echo ""
    exit 1
fi

# Set default values for optional variables
export DATABRICKS_BASE_URL="${DATABRICKS_BASE_URL:-https://adb-2252852771922438.18.azuredatabricks.net/serving-endpoints/}"
export MODEL_ENDPOINT_ID="${MODEL_ENDPOINT_ID:-databricks-claude-sonnet-4-6}"
export API_PORT="${API_PORT:-5001}"
export FRONTEND_PORT="${FRONTEND_PORT:-5002}"

echo "Configuration loaded:"
echo "   - API Port: $API_PORT"
echo "   - Frontend Port: $FRONTEND_PORT"
echo "   - Model Endpoint: $MODEL_ENDPOINT_ID"
echo ""

# Start API server in background
echo "Starting API server on port $API_PORT..."
python3 api_server.py > /app/logs/api_server.log 2>&1 &
API_PID=$!
echo "   API server started (PID: $API_PID)"

# Wait for API to be ready
echo "   Waiting for API server to be ready..."
for i in {1..30}; do
    if curl -s --max-time 2 "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
        echo "   API server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   API server health check timeout (may still be starting)"
    fi
    sleep 1
done

# Start frontend server in background
echo ""
echo "Starting frontend server on port $FRONTEND_PORT..."
cd /app/frontend
python3 -m http.server $FRONTEND_PORT > /app/logs/frontend_server.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend server started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
echo "   Waiting for frontend server to be ready..."
for i in {1..10}; do
    if curl -s --max-time 2 "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
        echo "   Frontend server is ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "   Frontend server health check timeout (may still be starting)"
    fi
    sleep 1
done

echo ""
echo "=========================================="
echo "Logistics AI Bot is running."
echo ""
echo "Frontend UI: http://localhost:$FRONTEND_PORT"
echo "API Server:  http://localhost:$API_PORT"
echo "API Docs:    http://localhost:$API_PORT/docs"
echo ""
echo "Logs:"
echo "   - API:      /app/logs/api_server.log"
echo "   - Frontend: /app/logs/frontend_server.log"
echo "=========================================="
echo ""

# Function to handle shutdown
shutdown() {
    echo ""
    echo "Shutting down servers..."
    kill $API_PID $FRONTEND_PID 2>/dev/null || true
    wait $API_PID $FRONTEND_PID 2>/dev/null || true
    echo "Servers stopped"
    exit 0
}

# Trap signals for graceful shutdown
trap shutdown SIGTERM SIGINT

# Keep container running and tail logs
tail -f /app/logs/api_server.log /app/logs/frontend_server.log &
wait
