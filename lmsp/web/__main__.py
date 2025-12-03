"""
Run LMSP Web UI

Usage:
    python -m lmsp.web
"""

import uvicorn
from lmsp.web.app import app

if __name__ == "__main__":
    print("Starting LMSP Web UI...")
    print("Open http://localhost:8000 in your browser")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True  # Auto-reload on code changes during development
    )
