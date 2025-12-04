#!/bin/bash
# LMSP Development Server
# =======================
# Usage: ./dev.sh [--public]
#
# --public: Expose on 0.0.0.0 (accessible on network)
# Without flag: localhost only

set -e
cd "$(dirname "$0")"

HOST_FLAG=""
if [[ "$1" == "--public" ]]; then
    HOST_FLAG="--host 0.0.0.0"
    echo "🌐 Starting in PUBLIC mode (exposed on 0.0.0.0)"
else
    echo "🔒 Starting in LOCAL mode (localhost only)"
fi

# Trap to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $UVICORN_PID $VITE_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Activate venv (always use this project's venv)
source .venv/bin/activate

# Start uvicorn backend
echo "🐍 Starting backend on port 8000..."
uvicorn lmsp.web.app:app --reload --reload-include "*.toml" --reload-include "*.py" $HOST_FLAG --port 8000 &
UVICORN_PID=$!

# Start Vite frontend
echo "⚡ Starting frontend on port 5173..."
cd lmsp/web/frontend
npm run dev -- $HOST_FLAG &
VITE_PID=$!
cd - > /dev/null

echo ""
echo "✅ Dev servers running:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
if [[ -n "$HOST_FLAG" ]]; then
    echo "   (Also accessible on network interfaces)"
fi
echo ""
echo "Press Ctrl+C to stop"

# Wait for both processes
wait
