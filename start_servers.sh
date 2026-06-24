#!/bin/bash
# Start both API and Frontend servers (API on 5001, frontend on 5002)
# This script is idempotent: if a service is already running, it will not start a duplicate.
# Usage: ./start_servers.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

log() { printf "%s\n" "$*"; }

log "Starting SeaRates AI Servers..."
log ""

# Activate a virtual environment if present (prefer .venv, fall back to venv_ai_model)
if [ -d ".venv" ]; then
  log "Activating virtual environment (.venv)..."
  # shellcheck source=/dev/null
  source .venv/bin/activate
elif [ -d "venv_ai_model" ]; then
  log "Activating virtual environment (venv_ai_model)..."
  # shellcheck source=/dev/null
  source venv_ai_model/bin/activate
fi

ensure_api() {
  local PORT=5001
  local HEALTH_URL="http://localhost:${PORT}/health"

  if curl -s --max-time 2 "$HEALTH_URL" >/dev/null 2>&1; then
    log "API server already running on port ${PORT}"
    return
  fi

  log "Starting API server on port ${PORT}..."
  nohup python3 api_server.py > api_server.log 2>&1 &
  local PID=$!
  log "   API server started (PID: ${PID})"
  log "   Logs: api_server.log"

  # Wait up to 20 seconds for health
  for _ in {1..20}; do
    if curl -s --max-time 2 "$HEALTH_URL" >/dev/null 2>&1; then
      log "   API server is ready"
      return
    fi
    sleep 1
  done
  log "   API server may still be starting (health not reachable yet)"
}

ensure_frontend() {
  local PORT=5002
  local URL="http://localhost:${PORT}"

  if curl -s --max-time 2 "$URL" >/dev/null 2>&1; then
    log "Frontend already running on port ${PORT}"
    return
  fi

  log "Starting frontend server on port ${PORT}..."
  (
    cd frontend
    nohup python3 -m http.server "${PORT}" > ../frontend_server.log 2>&1 &
    echo $! > ../frontend_server.pid
  )
  local PID
  PID=$(cat frontend_server.pid 2>/dev/null || true)
  log "   Frontend server started (PID: ${PID:-unknown})"
  log "   Logs: frontend_server.log"

  # Wait up to 10 seconds
  for _ in {1..10}; do
    if curl -s --max-time 2 "$URL" >/dev/null 2>&1; then
      log "   Frontend server is ready"
      return
    fi
    sleep 1
  done
  log "   Frontend server may still be starting (not reachable yet)"
}

ensure_api
ensure_frontend

log ""
log "=========================================="
log "Servers are running."
log ""
log "Frontend UI: http://localhost:5002"
log "API Server:  http://localhost:5001"
log "API Docs:    http://localhost:5001/docs"
log ""
log "To stop servers:"
log "  pkill -f 'api_server.py'"
log "  pkill -f 'http.server 5002'"
log "=========================================="

