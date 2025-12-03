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

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# LMSP imports
from lmsp.python.challenges import ChallengeLoader, Challenge
from lmsp.python.validator import CodeValidator
from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile
from lmsp.ui.achievements import AchievementManager, achievement_manager

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
PROJECT_ROOT = WEB_DIR.parent.parent
CHALLENGES_DIR = PROJECT_ROOT / "challenges"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize LMSP systems
challenge_loader = ChallengeLoader(CHALLENGES_DIR)
code_validator = CodeValidator(timeout_seconds=5)

# Global state (in production, use proper session management)
_adaptive_engines: dict[str, AdaptiveEngine] = {}
_achievement_managers: dict[str, AchievementManager] = {}


def get_adaptive_engine(player_id: str) -> AdaptiveEngine:
    """Get or create an adaptive engine for a player."""
    if player_id not in _adaptive_engines:
        profile = LearnerProfile(player_id=player_id)
        _adaptive_engines[player_id] = AdaptiveEngine(profile)
    return _adaptive_engines[player_id]


def get_achievement_manager(player_id: str) -> AchievementManager:
    """Get or create an achievement manager for a player."""
    if player_id not in _achievement_managers:
        _achievement_managers[player_id] = AchievementManager()
    return _achievement_managers[player_id]


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
    try:
        challenge = challenge_loader.load(challenge_id)
        return templates.TemplateResponse(
            "challenge.html",
            {
                "request": request,
                "challenge": challenge,
                "challenge_id": challenge.id,
                "challenge_name": challenge.name,
                "challenge_description": challenge.description_brief,
                "skeleton_code": challenge.skeleton_code,
                "test_count": len(challenge.test_cases),
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")


@app.get("/api/gamepad/status")
async def gamepad_status():
    """Check gamepad connection status."""
    # This will be detected client-side via Gamepad API
    return JSONResponse({
        "connected": False,  # Will be updated by JS
        "message": "Check client-side Gamepad API"
    })


@app.get("/api/profile")
async def get_profile(request: Request, player_id: str = "default"):
    """Get player profile. Returns HTML for HTMX, JSON for API calls."""
    # Get adaptive engine for player
    engine = get_adaptive_engine(player_id)
    profile_data = engine.profile

    # Get achievements
    achievement_mgr = get_achievement_manager(player_id)
    achievement_stats = achievement_mgr.get_achievement_stats()

    profile = {
        "player_id": profile_data.player_id,
        "mastery_levels": profile_data.mastery_levels,
        "xp": achievement_stats["total_xp"],
        "level": len([m for m in profile_data.mastery_levels.values() if m >= 3]),
        "achievements_unlocked": achievement_stats["unlocked"],
        "achievements_total": achievement_stats["total"],
    }

    # If HTMX request, return HTML fragment
    if request.headers.get("HX-Request"):
        return HTMLResponse(f"""
        <div class="profile-card panel">
            <h3>📊 Player Progress</h3>
            <p><strong>Player:</strong> {profile['player_id']}</p>
            <p><strong>Level:</strong> {profile['level']}</p>
            <p><strong>XP:</strong> {profile['xp']}</p>
            <p><strong>Achievements:</strong> {profile['achievements_unlocked']}/{profile['achievements_total']}</p>
            <p class="text-muted">Keep playing to unlock more!</p>
        </div>
        """)
    return JSONResponse(profile)


@app.post("/api/code/submit")
async def submit_code(request: Request):
    """Submit code for validation."""
    data = await request.json()
    challenge_id = data.get("challenge_id")
    code = data.get("code", "")
    player_id = data.get("player_id", "default")

    if not challenge_id or not code:
        return JSONResponse({
            "success": False,
            "error": "challenge_id and code are required",
            "tests_passing": 0,
            "tests_total": 0,
        }, status_code=400)

    try:
        # Load challenge
        challenge = challenge_loader.load(challenge_id)

        # Validate code
        result = code_validator.validate(code, challenge.test_cases)

        # Update adaptive engine
        engine = get_adaptive_engine(player_id)
        engine.observe_attempt(
            concept=challenge_id,
            success=result.success,
            time_seconds=result.time_seconds,
        )

        # Check for achievements
        achievement_mgr = get_achievement_manager(player_id)
        unlocked = None

        if result.success:
            # Check for perfect score achievement
            unlocked = achievement_mgr.update_progress("perfectionist", 1)

        # Build response
        response_data = {
            "success": result.success,
            "tests_passing": result.tests_passing,
            "tests_total": result.tests_total,
            "time_seconds": result.time_seconds,
            "output": result.output,
        }

        if result.error:
            response_data["error"] = result.error

        if unlocked:
            response_data["achievement_unlocked"] = {
                "name": unlocked.name,
                "description": unlocked.description,
                "xp_reward": unlocked.xp_reward,
                "icon": unlocked.icon,
            }

        return JSONResponse(response_data)

    except FileNotFoundError:
        return JSONResponse({
            "success": False,
            "error": f"Challenge '{challenge_id}' not found",
            "tests_passing": 0,
            "tests_total": 0,
        }, status_code=404)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Validation error: {str(e)}",
            "tests_passing": 0,
            "tests_total": 0,
        }, status_code=500)


@app.get("/api/challenges")
async def list_challenges(request: Request, level: Optional[int] = None):
    """List available challenges. Returns HTML for HTMX, JSON for API calls."""
    # Load challenges from ChallengeLoader
    all_challenge_ids = challenge_loader.list_challenges()

    challenges = []
    for cid in all_challenge_ids:
        try:
            challenge = challenge_loader.load(cid)
            if level is None or challenge.level == level:
                challenges.append({
                    "id": challenge.id,
                    "name": challenge.name,
                    "level": challenge.level,
                    "points": challenge.points,
                })
        except Exception:
            continue  # Skip challenges that can't be loaded

    # If HTMX request, return HTML fragment
    if request.headers.get("HX-Request"):
        if not challenges:
            return HTMLResponse("""
            <div class="challenges-list panel">
                <h3>🚀 Select a Challenge</h3>
                <p class="text-muted">No challenges available yet. Check back soon!</p>
            </div>
            """)

        items = "\n".join([
            f'<div class="challenge-card" hx-get="/challenges/{c["id"]}" hx-target="#content" hx-swap="innerHTML">'
            f'<span class="level-badge">Lv.{c["level"]}</span>'
            f'<h4>{c["name"]}</h4>'
            f'<p class="text-muted">{c["points"]} points</p>'
            f'</div>'
            for c in challenges
        ])
        return HTMLResponse(f"""
        <div class="challenges-list panel">
            <h3>🚀 Select a Challenge</h3>
            <div class="challenge-grid">
                {items}
            </div>
        </div>
        """)
    return JSONResponse(challenges)


# Add new endpoints for achievements and gamepad
@app.get("/api/achievements")
async def list_achievements(player_id: str = "default"):
    """List player achievements with progress."""
    achievement_mgr = get_achievement_manager(player_id)
    stats = achievement_mgr.get_achievement_stats()
    unlocked = achievement_mgr.get_unlocked()
    in_progress = achievement_mgr.get_in_progress()

    return JSONResponse({
        "stats": stats,
        "unlocked": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "tier": a.tier.tier_name,
                "icon": a.icon,
                "xp_reward": a.xp_reward,
            }
            for a in unlocked
        ],
        "in_progress": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "progress": p.current_value,
                "required": a.required_value,
                "percent": p.progress_percent(a.required_value),
            }
            for a, p in in_progress
        ],
    })


@app.post("/api/emotional/record")
async def record_emotional_feedback(request: Request):
    """Record emotional feedback (RT/LT trigger values)."""
    data = await request.json()
    player_id = data.get("player_id", "default")
    trigger = data.get("trigger")  # "RT" or "LT"
    value = data.get("value", 0.0)  # 0.0-1.0
    context = data.get("context", "")

    engine = get_adaptive_engine(player_id)

    # Map trigger to emotional dimension
    if trigger == "RT":
        from lmsp.input.emotional import EmotionalDimension
        engine.observe_emotion(EmotionalDimension.ENJOYMENT, value, context)
    elif trigger == "LT":
        from lmsp.input.emotional import EmotionalDimension
        engine.observe_emotion(EmotionalDimension.FRUSTRATION, value, context)

    return JSONResponse({
        "success": True,
        "trigger": trigger,
        "value": value,
        "message": "Feedback recorded",
    })


@app.get("/api/recommendations")
async def get_recommendations(player_id: str = "default"):
    """Get adaptive learning recommendations for next challenge."""
    engine = get_adaptive_engine(player_id)
    recommendation = engine.recommend_next()

    return JSONResponse({
        "action": recommendation.action,
        "concept": recommendation.concept,
        "challenge_id": recommendation.challenge_id,
        "reason": recommendation.reason,
        "confidence": recommendation.confidence,
    })


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
