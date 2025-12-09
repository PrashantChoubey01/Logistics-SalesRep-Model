#!/bin/bash
# Convenience script to activate the project virtual environment (venv_ai_model)
# Usage: source activate_dpw.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv_ai_model"

if [ ! -d "$VENV_PATH" ]; then
  echo "❌ Virtual environment not found at: $VENV_PATH"
  echo "   Create it first, e.g.: python3 -m venv venv_ai_model && source venv_ai_model/bin/activate && pip install -r requirements.txt"
  return 1 2>/dev/null || exit 1
fi

echo "📦 Activating virtual environment from: $VENV_PATH"
# shellcheck source=/dev/null
source "$VENV_PATH/bin/activate"

echo "✅ Virtual environment activated. Python: $(python3 --version 2>/dev/null || python --version)"
echo "   Current directory: $PROJECT_ROOT"

