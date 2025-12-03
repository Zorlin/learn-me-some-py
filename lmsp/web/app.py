"""
LMSP Web UI - FastAPI + HTMX
=============================

Gorgeous OLED-black dark theme web interface for Learn Me Some Py.

Features:
- OLED-black (#000000) dark theme
- Gamepad API support for controller input
- HTMX for smooth interactions
- Beautiful, responsive design

Usage:
    uvicorn lmsp.web.app:app --reload
    # Or: python -m lmsp.web
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create FastAPI app
app = FastAPI(
    title="LMSP Web",
    description="Learn Me Some Py - The game that teaches you to build it",
    version="0.1.0",
)

# Setup paths
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main page with OLED-black theme."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "LMSP - Learn Me Some Py",
            "player_id": "default",  # TODO: Get from session
        }
    )


@app.get("/challenges/{challenge_id}", response_class=HTMLResponse)
async def get_challenge(request: Request, challenge_id: str):
    """Load a specific challenge."""
    # TODO: Load actual challenge from ChallengeLoader
    return templates.TemplateResponse(
        "challenge.html",
        {
            "request": request,
            "challenge_id": challenge_id,
            "challenge_name": challenge_id.replace("_", " ").title(),
            "challenge_description": "Challenge description here",
        }
    )


@app.get("/api/gamepad/status")
async def gamepad_status():
    """Check gamepad connection status."""
    # This will be detected client-side via Gamepad API
    return JSONResponse({
        "connected": False,  # Will be updated by JS
        "message": "Check client-side Gamepad API"
    })


@app.get("/api/profile")
async def get_profile():
    """Get player profile."""
    # TODO: Load actual profile from LearnerProfile
    return JSONResponse({
        "player_id": "default",
        "mastery_levels": {},
        "xp": 0,
        "level": 1,
    })


@app.post("/api/code/submit")
async def submit_code(request: Request):
    """Submit code for validation."""
    data = await request.json()
    challenge_id = data.get("challenge_id")
    code = data.get("code", "")

    # TODO: Validate code with CodeValidator
    return JSONResponse({
        "success": True,
        "tests_passing": 0,
        "tests_total": 0,
        "message": "Validation not yet implemented"
    })


@app.get("/api/challenges")
async def list_challenges():
    """List available challenges."""
    # TODO: Load from ChallengeLoader
    return JSONResponse([
        {"id": "hello_world", "name": "Hello World", "level": 1},
        {"id": "variables", "name": "Variables", "level": 2},
    ])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


# Self-teaching note:
#
# This file demonstrates:
# - FastAPI web framework (Level 6: Web development)
# - Async/await for async endpoints (Level 5-6)
# - Path operations and routing (Level 5+)
# - Jinja2 templates for HTML rendering (Level 5+)
# - Static file serving (Level 4+)
# - JSON API endpoints (Level 5+)
#
# Prerequisites:
# - Level 4: Functions, dictionaries, file paths
# - Level 5: Classes, async/await basics
# - Level 6: Web frameworks, HTTP concepts
#
# FastAPI is used by major companies:
# - Netflix, Uber, Microsoft
# - Fast, modern, type-safe Python web framework
