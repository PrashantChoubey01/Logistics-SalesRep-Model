#!/bin/bash
# Start both API and Frontend servers (API on 5001, frontend on 5002)
# This script is idempotent: if a service is already running, it will not start a duplicate.
# Usage: ./start_servers.sh
#
# Features:
# - Auto-creates virtual environment if not present
# - Auto-installs all dependencies
# - Starts API server on port 5001
# - Starts Frontend server on port 5002

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Virtual environment name
VENV_NAME="venv_ai_model"
PYTHON_VERSION="python3"

log() { printf "%s\n" "$*"; }
log_info() { printf "ℹ️  %s\n" "$*"; }
log_success() { printf "✅ %s\n" "$*"; }
log_warning() { printf "⚠️  %s\n" "$*"; }
log_error() { printf "❌ %s\n" "$*"; }

# Check if Python is available
check_python() {
  if ! command -v $PYTHON_VERSION &> /dev/null; then
    log_error "Python3 is not installed. Please install Python 3.10+ first."
    exit 1
  fi
  
  local py_version
  py_version=$($PYTHON_VERSION --version 2>&1 | cut -d' ' -f2)
  log_info "Python version: $py_version"
}

# Create virtual environment if it doesn't exist
setup_venv() {
  if [ -d "$VENV_NAME" ]; then
    log_success "Virtual environment '$VENV_NAME' already exists"
  else
    log_info "Creating virtual environment '$VENV_NAME'..."
    $PYTHON_VERSION -m venv "$VENV_NAME"
    log_success "Virtual environment created"
  fi
  
  # Activate virtual environment
  log_info "Activating virtual environment..."
  # shellcheck source=/dev/null
  source "$VENV_NAME/bin/activate"
  log_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
  log_info "Checking dependencies..."
  
  # Upgrade pip first
  pip install --upgrade pip --quiet
  
  # Check if key packages are installed
  if python -c "import langgraph, fastapi, sentence_transformers" 2>/dev/null; then
    log_success "All dependencies already installed"
  else
    log_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt --quiet
    log_success "Dependencies installed successfully"
  fi
}

# Create necessary directories
setup_directories() {
  mkdir -p data/threads data/embeddings logs
  log_success "Required directories created"
}

# Check if port embeddings exist, create if not
setup_embeddings() {
  if [ -f "data/embeddings/port_embeddings.pkl" ]; then
    log_success "Port embeddings already exist"
  else
    log_info "Creating port embeddings (first-time setup)..."
    python scripts/create_port_embeddings.py
    log_success "Port embeddings created"
  fi
}

# Check environment variables
check_env() {
  if [ -f ".env" ]; then
    log_success "Environment file (.env) found"
    # Source .env file for environment variables
    set -a
    # shellcheck source=/dev/null
    source .env 2>/dev/null || true
    set +a
  else
    log_warning "No .env file found. Copy .env.example to .env and configure your API keys."
  fi
  
  # Check for required environment variables
  if [ -z "${DATABRICKS_TOKEN:-}" ]; then
    log_warning "DATABRICKS_TOKEN not set. LLM features may not work."
  fi
}

ensure_api() {
  local PORT=5001
  local HEALTH_URL="http://localhost:${PORT}/health"

  if curl -s --max-time 2 "$HEALTH_URL" >/dev/null 2>&1; then
    log_success "API server already running on port ${PORT}"
    return
  fi

  log_info "Starting API server on port ${PORT}..."
  nohup python api_server.py > logs/api_server.log 2>&1 &
  local PID=$!
  log_info "API server started (PID: ${PID})"
  log_info "Logs: logs/api_server.log"

  # Wait up to 30 seconds for health
  for i in {1..30}; do
    if curl -s --max-time 2 "$HEALTH_URL" >/dev/null 2>&1; then
      log_success "API server is ready"
      return
    fi
    printf "."
    sleep 1
  done
  echo ""
  log_warning "API server may still be starting (health not reachable yet)"
}

ensure_frontend() {
  local PORT=5002
  local URL="http://localhost:${PORT}"

  if curl -s --max-time 2 "$URL" >/dev/null 2>&1; then
    log_success "Frontend already running on port ${PORT}"
    return
  fi

  log_info "Starting frontend server on port ${PORT}..."
  (
    cd frontend
    nohup python -m http.server "${PORT}" > ../logs/frontend_server.log 2>&1 &
    echo $! > ../logs/frontend_server.pid
  )
  local PID
  PID=$(cat logs/frontend_server.pid 2>/dev/null || true)
  log_info "Frontend server started (PID: ${PID:-unknown})"
  log_info "Logs: logs/frontend_server.log"

  # Wait up to 10 seconds
  for _ in {1..10}; do
    if curl -s --max-time 2 "$URL" >/dev/null 2>&1; then
      log_success "Frontend server is ready"
      return
    fi
    sleep 1
  done
  log_warning "Frontend server may still be starting (not reachable yet)"
}

# Main execution
main() {
  log ""
  log "=========================================="
  log "🚀 DP World × SeaRates AI - Server Setup"
  log "=========================================="
  log ""
  
  # Step 1: Check Python
  check_python
  
  # Step 2: Setup virtual environment
  setup_venv
  
  # Step 3: Install dependencies
  install_dependencies
  
  # Step 4: Create directories
  setup_directories
  
  # Step 5: Check environment
  check_env
  
  # Step 6: Setup embeddings (if needed)
  setup_embeddings
  
  log ""
  log "=========================================="
  log "🔄 Starting Servers..."
  log "=========================================="
  log ""
  
  # Step 7: Start servers
  ensure_api
  ensure_frontend
  
  log ""
  log "=========================================="
  log_success "Setup Complete!"
  log ""
  log "🌐 Frontend UI: http://localhost:5002"
  log "🔌 API Server:  http://localhost:5001"
  log "📚 API Docs:    http://localhost:5001/docs"
  log ""
  log "To stop servers:"
  log "  pkill -f 'api_server.py'"
  log "  pkill -f 'http.server 5002'"
  log "=========================================="
}

main "$@"
