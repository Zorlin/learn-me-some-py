#!/bin/bash
# LMSP Development Server with Hot Reloading
# ==========================================
#
# Runs both:
# - Vite dev server (HMR for Vue.js) on port 5173
# - FastAPI (uvicorn --reload) on port 8000
#
# Frontend talks to API via Vite proxy at /api -> localhost:8000
#
# Usage:
#   ./dev.sh
#
# Then open http://localhost:5173 in your browser

set -e

cd "$(dirname "$0")"

# Check if virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Activating .venv..."
    source .venv/bin/activate
fi

# Run both servers concurrently
cd lmsp/web/frontend
exec npm run dev:all
