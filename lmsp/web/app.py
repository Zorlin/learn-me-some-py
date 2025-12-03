"""
LMSP Web API - FastAPI + Vue.js SPA
====================================

Pure JSON API backend with Vue.js SPA frontend.

Features:
- JSON API endpoints for game data
- Static file serving for Vue.js build
- Achievement and progress tracking
- Emotional feedback recording
- Adaptive learning recommendations

Usage:
    uvicorn lmsp.web.app:app --reload
    # Or: python -m lmsp.web
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# LMSP imports
from lmsp.python.challenges import ChallengeLoader, Challenge
from lmsp.python.validator import CodeValidator, PytestValidator
from lmsp.python.concepts import ConceptDAG
from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile
from lmsp.ui.achievements import AchievementManager
from lmsp.web.database import get_database, LMSPDatabase
from datetime import datetime, timedelta

# Create FastAPI app
app = FastAPI(
    title="LMSP API",
    description="Learn Me Some Py - JSON API for Vue.js frontend",
    version="0.1.0",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup paths
WEB_DIR = Path(__file__).parent
STATIC_DIR = WEB_DIR / "static"
DIST_DIR = STATIC_DIR / "dist"
PROJECT_ROOT = WEB_DIR.parent.parent
CHALLENGES_DIR = PROJECT_ROOT / "challenges"
CONCEPTS_DIR = PROJECT_ROOT / "concepts"

# Initialize LMSP systems
challenge_loader = ChallengeLoader(CHALLENGES_DIR)
code_validator = CodeValidator(timeout_seconds=5)

# Initialize concept DAG (skill tree)
concept_dag = ConceptDAG(CONCEPTS_DIR)
concept_dag.load_all()

# Global state (adaptive engines and achievement managers are session-based)
_adaptive_engines: dict[str, AdaptiveEngine] = {}
_achievement_managers: dict[str, AchievementManager] = {}


def get_player_completions(player_id: str) -> dict:
    """Get completion data for a player from database."""
    db = get_database()
    completions = db.get_completions(player_id)
    # Convert to the format expected by existing code
    return {
        cid: {
            "count": c.count,
            "first_completed": c.first_completed,
            "last_completed": c.last_completed,
            "times": c.times,
        }
        for cid, c in completions.items()
    }


def get_player_xp(player_id: str) -> int:
    """Get total XP for a player from database."""
    db = get_database()
    return db.get_player_xp(player_id)


def calculate_xp_reward(
    challenge: Challenge,
    player_id: str,
    time_seconds: float,
    is_spaced_repetition_prompted: bool = False
) -> tuple[int, str]:
    """
    Calculate XP reward for completing a challenge (WoW-style).

    Returns:
        (xp_earned, reason_string)

    XP Rules:
    - First completion: Full points
    - Repeat (not prompted): 25% of points
    - Spaced repetition prompted: 150% of points (encourages practice!)
    - Speed bonus: +10% if completed in under 60 seconds
    """
    base_xp = challenge.points
    completions = get_player_completions(player_id)

    is_first_completion = challenge.id not in completions

    if is_first_completion:
        xp = base_xp
        reason = f"First completion: +{xp} XP"
    elif is_spaced_repetition_prompted:
        xp = int(base_xp * 1.5)
        reason = f"Spaced repetition bonus: +{xp} XP (150%)"
    else:
        xp = max(1, int(base_xp * 0.25))  # At least 1 XP
        reason = f"Repeat completion: +{xp} XP (25%)"

    # Speed bonus for quick solves
    if time_seconds < 60 and base_xp >= 10:
        speed_bonus = max(1, int(xp * 0.1))
        xp += speed_bonus
        reason += f" + Speed bonus: +{speed_bonus} XP"

    return xp, reason


def record_challenge_completion(
    player_id: str,
    challenge_id: str,
    time_seconds: float,
    xp_earned: int
):
    """Record a challenge completion to database."""
    db = get_database()

    # Record completion
    db.record_completion(player_id, challenge_id, time_seconds)

    # Add XP
    db.add_player_xp(player_id, xp_earned)


def find_concept_for_challenge(challenge_id: str) -> Optional[str]:
    """Find the concept that this challenge belongs to."""
    for concept_id, concept in concept_dag.concepts.items():
        if (concept.challenge_starter == challenge_id or
            concept.challenge_intermediate == challenge_id or
            concept.challenge_mastery == challenge_id):
            return concept_id
    return None


def get_mastery_hint(concept_id: str, current_mastery: int) -> str:
    """
    Get a 60-140 char hint for the next mastery stage.

    Mastery levels:
    0 -> 1: Complete the starter challenge
    1 -> 2: Complete intermediate or do starter faster
    2 -> 3: Complete mastery challenge or speedrun intermediate
    3 -> 4: Complete all challenges with speed bonuses
    """
    concept = concept_dag.concepts.get(concept_id)
    if not concept:
        return "Complete challenges to increase mastery."

    name = concept.name

    if current_mastery == 0:
        if concept.challenge_starter:
            return f"Complete '{concept.challenge_starter}' to begin learning {name}."
        return f"Start with a {name} challenge to unlock this concept."

    elif current_mastery == 1:
        if concept.challenge_intermediate:
            return f"Try the intermediate challenge or speedrun the starter for {name}."
        return f"Practice {name} more to solidify your understanding."

    elif current_mastery == 2:
        if concept.challenge_mastery:
            return f"Ready for mastery? Complete '{concept.challenge_mastery}' or speedrun previous challenges."
        return f"Speed up your {name} solutions for bonus XP and mastery."

    elif current_mastery == 3:
        return f"Complete all {name} challenges with speed bonuses to achieve full mastery!"

    else:  # mastery == 4
        return f"You've mastered {name}! Return for spaced repetition bonuses."


import math


def calculate_retention_score(
    completion_count: int,
    last_completed: str,
    best_time: float,
    expected_time: float = 60.0,
    half_life_days: float = 7.0
) -> dict:
    """
    Calculate spaced repetition retention score.

    Uses an exponential decay model where:
    - Starts at 100% immediately after completion
    - Decays based on time since last completion
    - Decay rate slows with more completions (mastery)
    - Speed bonus for fast completions
    - TRUE MASTERY: Once AI determines you've mastered it, locks at 100% forever (purple)

    Mastery criteria (AI confidence):
    - 5+ successful completions (proven consistency)
    - Performance grade A or better (you're fast)
    - This proves you truly understand it, not just memorized

    Returns dict with:
        - retention: 0-100 percentage
        - needs_review: bool
        - days_since: days since last completion
        - performance_grade: S/A/B/C/D/F based on speed
        - mastered: bool - true mastery achieved, no more decay
    """
    from datetime import datetime

    # Parse last completion time
    try:
        last_dt = datetime.fromisoformat(last_completed)
        days_since = (datetime.now() - last_dt).total_seconds() / 86400
    except (ValueError, TypeError):
        days_since = 999  # If no valid date, assume very old

    # Performance grade based on best time
    if best_time:
        ratio = best_time / expected_time
        if ratio <= 0.5:
            grade = 'S'  # Speedrun!
        elif ratio <= 0.75:
            grade = 'A'
        elif ratio <= 1.0:
            grade = 'B'
        elif ratio <= 1.5:
            grade = 'C'
        elif ratio <= 2.0:
            grade = 'D'
        else:
            grade = 'F'
    else:
        grade = '-'

    # Mastery factor: how well you know this (affects decay rate)
    mastery_factor = min(3.0, 1.0 + (completion_count - 1) * 0.5)

    # TRUE MASTERY CHECK: AI confidence that you've genuinely learned this
    # Criteria: 5+ completions with grade A or better = you truly know it
    is_mastered = (
        completion_count >= 5 and
        grade in ('S', 'A')
    )

    if is_mastered:
        # Mastered! Locked at 100% forever (purple)
        retention = 100.0
    else:
        # Standard spaced repetition decay
        adjusted_half_life = half_life_days * mastery_factor
        retention = 100 * math.exp(-days_since * math.log(2) / adjusted_half_life)

        # Speed bonus: If completed faster than expected, boost retention
        if best_time and best_time < expected_time:
            speed_ratio = best_time / expected_time
            speed_bonus = (1 - speed_ratio) * 10  # Up to 10% bonus
            retention = min(100, retention + speed_bonus)

    return {
        "retention": round(retention, 1),
        "needs_review": not is_mastered and retention < 50,
        "days_since": round(days_since, 1),
        "performance_grade": grade,
        "completion_count": completion_count,
        "mastery_factor": round(mastery_factor, 2),
        "mastered": is_mastered,
    }


def get_adaptive_engine(player_id: str) -> AdaptiveEngine:
    """Get or create an adaptive engine for a player, loading mastery from database."""
    if player_id not in _adaptive_engines:
        profile = LearnerProfile(player_id=player_id)

        # Load mastery levels from database
        db = get_database()
        stored_mastery = db.get_mastery_levels(player_id)
        for concept_id, mastery_level in stored_mastery.items():
            profile.mastery_levels[concept_id] = mastery_level

        _adaptive_engines[player_id] = AdaptiveEngine(profile)
    return _adaptive_engines[player_id]


def save_mastery_to_database(player_id: str, concept_id: str, mastery_level: float):
    """Save mastery level to database for persistence."""
    db = get_database()
    db.set_mastery_level(player_id, concept_id, mastery_level)


def get_achievement_manager(player_id: str) -> AchievementManager:
    """Get or create an achievement manager for a player."""
    if player_id not in _achievement_managers:
        _achievement_managers[player_id] = AchievementManager()
    return _achievement_managers[player_id]


# ============================================================================
# API Routes - Pure JSON
# ============================================================================


@app.get("/api/profile")
async def get_profile(player_id: str = "default"):
    """Get player profile data."""
    engine = get_adaptive_engine(player_id)
    profile_data = engine.profile

    achievement_mgr = get_achievement_manager(player_id)
    achievement_stats = achievement_mgr.get_achievement_stats()
    completions = get_player_completions(player_id)

    # XP is now tracked directly, not from achievements
    total_xp = get_player_xp(player_id)

    # Calculate level from XP (100 XP per level, with increasing requirements)
    # Level 1: 0-99 XP, Level 2: 100-249 XP, Level 3: 250-499 XP, etc.
    def calculate_level(xp: int) -> int:
        level = 1
        threshold = 100
        while xp >= threshold:
            level += 1
            threshold += level * 100
        return level

    player_level = calculate_level(total_xp)

    return JSONResponse({
        "player_id": profile_data.player_id,
        "mastery_levels": profile_data.mastery_levels,
        "xp": total_xp,
        "level": player_level,
        "challenges_completed": len(completions),
        "achievements_unlocked": achievement_stats["unlocked"],
        "achievements_total": achievement_stats["total"],
    })


@app.get("/api/challenges")
async def list_challenges(level: Optional[int] = None, player_id: str = "default"):
    """List available challenges with progress data."""
    all_challenge_ids = challenge_loader.list_challenges()

    # Get player's completion data
    db = get_database()
    completions = db.get_completions(player_id)

    challenges = []
    for cid in all_challenge_ids:
        try:
            challenge = challenge_loader.load(cid)
            if level is None or challenge.level == level:
                challenge_data = {
                    "id": challenge.id,
                    "name": challenge.name,
                    "level": challenge.level,
                    "points": challenge.points,
                }

                # Add progress data if challenge has been completed
                if cid in completions:
                    comp = completions[cid]
                    progress = calculate_retention_score(
                        completion_count=comp.count,
                        last_completed=comp.last_completed,
                        best_time=comp.best_time,
                        expected_time=60.0 * (1 + challenge.level * 0.5),  # Scale by level
                    )
                    challenge_data["progress"] = progress
                else:
                    challenge_data["progress"] = None

                challenges.append(challenge_data)
        except Exception:
            continue

    return JSONResponse(challenges)


@app.get("/api/challenges/progress")
async def get_all_challenge_progress(player_id: str = "default"):
    """Get progress/retention data for all challenges."""
    db = get_database()
    completions = db.get_completions(player_id)

    progress_data = {}
    for challenge_id, comp in completions.items():
        try:
            challenge = challenge_loader.load(challenge_id)
            expected_time = 60.0 * (1 + challenge.level * 0.5)
        except FileNotFoundError:
            expected_time = 60.0

        progress_data[challenge_id] = calculate_retention_score(
            completion_count=comp.count,
            last_completed=comp.last_completed,
            best_time=comp.best_time,
            expected_time=expected_time,
        )

    return JSONResponse(progress_data)


@app.get("/api/challenges/{challenge_id}")
async def get_challenge(challenge_id: str):
    """Get a specific challenge."""
    try:
        challenge = challenge_loader.load(challenge_id)
        return JSONResponse({
            "id": challenge.id,
            "name": challenge.name,
            "level": challenge.level,
            "points": challenge.points,
            "description_brief": challenge.description_brief,
            "description_detailed": challenge.description_detailed,
            "skeleton_code": challenge.skeleton_code,
            "hints": challenge.hints,
            "test_count": len(challenge.test_cases),
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")


@app.post("/api/code/submit")
async def submit_code(request: Request):
    """Submit code for validation with XP and mastery tracking."""
    data = await request.json()
    challenge_id = data.get("challenge_id")
    code = data.get("code", "")
    player_id = data.get("player_id", "default")
    is_spaced_repetition = data.get("is_spaced_repetition", False)

    if not challenge_id or not code:
        return JSONResponse({
            "success": False,
            "error": "challenge_id and code are required",
            "tests_passing": 0,
            "tests_total": 0,
        }, status_code=400)

    try:
        challenge = challenge_loader.load(challenge_id)

        # Use the appropriate validator based on challenge config
        if challenge.validation_type == "pytest" and challenge.test_file:
            pytest_validator = PytestValidator(CHALLENGES_DIR, timeout_seconds=30)
            result = pytest_validator.validate(code, challenge.id, challenge.test_file)
        else:
            result = code_validator.validate(code, challenge.test_cases)

        engine = get_adaptive_engine(player_id)
        achievement_mgr = get_achievement_manager(player_id)

        response_data = {
            "success": result.success,
            "tests_passing": result.tests_passing,
            "tests_total": result.tests_total,
            "time_seconds": result.time_seconds,
            "output": result.output,
        }

        if result.error:
            response_data["error"] = result.error

        if result.success:
            # Calculate XP reward (WoW-style)
            xp_earned, xp_reason = calculate_xp_reward(
                challenge, player_id, result.time_seconds, is_spaced_repetition
            )

            # Record completion
            record_challenge_completion(
                player_id, challenge_id, result.time_seconds, xp_earned
            )

            # Find associated concept and update mastery
            concept_id = find_concept_for_challenge(challenge_id)
            mastery_info = None

            if concept_id:
                # Observe attempt for adaptive engine
                engine.observe_attempt(
                    concept=concept_id,
                    success=True,
                    time_seconds=result.time_seconds,
                )

                # Get updated mastery level
                new_mastery = engine.profile.mastery_levels.get(concept_id, 0)
                mastery_hint = get_mastery_hint(concept_id, int(new_mastery))

                # Save mastery to database for persistence
                save_mastery_to_database(player_id, concept_id, new_mastery)

                concept = concept_dag.concepts.get(concept_id)
                mastery_info = {
                    "concept_id": concept_id,
                    "concept_name": concept.name if concept else concept_id,
                    "mastery_level": new_mastery,
                    "mastery_percent": int(new_mastery * 25),
                    "next_hint": mastery_hint,
                }
            else:
                # No concept found, still record for adaptive engine
                engine.observe_attempt(
                    concept=challenge_id,
                    success=True,
                    time_seconds=result.time_seconds,
                )

            # Add XP and mastery to response
            response_data["xp_earned"] = xp_earned
            response_data["xp_reason"] = xp_reason
            response_data["total_xp"] = get_player_xp(player_id)

            if mastery_info:
                response_data["mastery"] = mastery_info

            # Check for achievements
            unlocked = achievement_mgr.update_progress("perfectionist", 1)
            if unlocked:
                response_data["achievement_unlocked"] = {
                    "name": unlocked.name,
                    "description": unlocked.description,
                    "xp_reward": unlocked.xp_reward,
                    "icon": unlocked.icon,
                }

                # Add achievement XP
                response_data["xp_earned"] += unlocked.xp_reward
                response_data["total_xp"] = get_player_xp(player_id) + unlocked.xp_reward
        else:
            # Record failed attempt for adaptive engine
            concept_id = find_concept_for_challenge(challenge_id)
            engine.observe_attempt(
                concept=concept_id or challenge_id,
                success=False,
                time_seconds=result.time_seconds,
            )

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
                "icon": a.icon,
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
    enjoyment = data.get("enjoyment", 0.0)
    frustration = data.get("frustration", 0.0)
    context = data.get("context", "")

    engine = get_adaptive_engine(player_id)

    from lmsp.input.emotional import EmotionalDimension
    if enjoyment > 0:
        engine.observe_emotion(EmotionalDimension.ENJOYMENT, enjoyment, context)
    if frustration > 0:
        engine.observe_emotion(EmotionalDimension.FRUSTRATION, frustration, context)

    return JSONResponse({
        "success": True,
        "enjoyment": enjoyment,
        "frustration": frustration,
        "message": "Feedback recorded",
    })


@app.get("/api/recommendations")
async def get_recommendations(player_id: str = "default"):
    """Get adaptive learning recommendations with actual challenge lookup."""
    engine = get_adaptive_engine(player_id)
    recommendation = engine.recommend_next()

    challenge_id = recommendation.challenge_id
    concept_id = recommendation.concept
    concept_name = None

    # If we have a concept, find its starter challenge
    if concept_id and concept_id in concept_dag.concepts:
        concept = concept_dag.concepts[concept_id]
        concept_name = concept.name
        challenge_id = concept.challenge_starter

    # If still no challenge, find an appropriate one for a new player
    if not challenge_id:
        mastery = engine.profile.mastery_levels

        # Find level 0 concepts the player hasn't mastered
        for cid, concept in concept_dag.concepts.items():
            if concept.level == 0:
                # Skip if player has mastery >= 1 (they've done at least one challenge)
                if mastery.get(cid, 0) >= 1:
                    continue
                # Skip if no starter challenge defined
                if not concept.challenge_starter:
                    continue
                # Check the challenge actually exists
                try:
                    challenge_loader.load(concept.challenge_starter)
                    challenge_id = concept.challenge_starter
                    concept_id = cid
                    concept_name = concept.name
                    break
                except FileNotFoundError:
                    continue

        # If all level 0 complete, try level 1
        if not challenge_id:
            for cid, concept in concept_dag.concepts.items():
                if concept.level == 1 and mastery.get(cid, 0) < 1:
                    if concept.challenge_starter:
                        try:
                            challenge_loader.load(concept.challenge_starter)
                            challenge_id = concept.challenge_starter
                            concept_id = cid
                            concept_name = concept.name
                            break
                        except FileNotFoundError:
                            continue

    # Fallback: just get hello_world as the absolute default
    if not challenge_id:
        try:
            challenge_loader.load("hello_world")
            challenge_id = "hello_world"
            concept_name = "Print Function"
        except FileNotFoundError:
            pass

    return JSONResponse({
        "action": recommendation.action,
        "concept": concept_name or concept_id,
        "challenge_id": challenge_id,
        "reason": recommendation.reason if recommendation.concept else "Start your Python journey!",
        "confidence": recommendation.confidence,
    })


@app.get("/api/skill-tree")
async def get_skill_tree(player_id: str = "default"):
    """Get skill tree data with mastery levels for visualization."""
    engine = get_adaptive_engine(player_id)
    mastery_levels = engine.profile.mastery_levels

    # Build nodes for each concept
    nodes = []
    edges = []

    for concept_id, concept in concept_dag.concepts.items():
        # Get mastery level (0-4) for this concept
        mastery = mastery_levels.get(concept_id, 0)

        # Calculate position hints based on level and prerequisites
        # X position: spread concepts at same level horizontally
        # Y position: based on level (0 at top, higher levels below)
        level_concepts = [c for c in concept_dag.concepts.values() if c.level == concept.level]
        x_index = level_concepts.index(concept) if concept in level_concepts else 0

        # Get mastery hint for progression
        mastery_hint = get_mastery_hint(concept_id, int(mastery))

        nodes.append({
            "id": concept_id,
            "name": concept.name,
            "level": concept.level,
            "mastery": mastery,
            "mastery_percent": mastery * 25,  # 0-100 scale
            "mastery_hint": mastery_hint,  # 60-140 char hint for next stage
            "description": concept.description_brief,
            "prerequisites": concept.prerequisites,
            "unlocks": concept_dag.get_unlocks(concept_id),
            "challenges": {
                "starter": concept.challenge_starter,
                "intermediate": concept.challenge_intermediate,
                "mastery": concept.challenge_mastery,
            },
            # Position hints for layout (frontend can adjust)
            "position": {
                "x": x_index * 200,
                "y": concept.level * 150,
            },
            # State for visualization
            "state": "mastered" if mastery >= 4 else "learning" if mastery > 0 else "locked" if concept.prerequisites and not all(mastery_levels.get(p, 0) >= 2 for p in concept.prerequisites) else "available",
        })

        # Create edges from prerequisites to this concept
        for prereq in concept.prerequisites:
            edges.append({
                "from": prereq,
                "to": concept_id,
            })

    # Get counts for summary
    mastered_count = len([n for n in nodes if n["state"] == "mastered"])
    learning_count = len([n for n in nodes if n["state"] == "learning"])
    available_count = len([n for n in nodes if n["state"] == "available"])
    locked_count = len([n for n in nodes if n["state"] == "locked"])

    return JSONResponse({
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "total": len(nodes),
            "mastered": mastered_count,
            "learning": learning_count,
            "available": available_count,
            "locked": locked_count,
        },
        "levels": {
            level: len([n for n in nodes if n["level"] == level])
            for level in range(7)  # Levels 0-6
        },
    })


@app.get("/api/concepts/{concept_id}")
async def get_concept(concept_id: str, player_id: str = "default"):
    """Get detailed info about a specific concept."""
    concept = concept_dag.get_concept(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept '{concept_id}' not found")

    engine = get_adaptive_engine(player_id)
    mastery = engine.profile.mastery_levels.get(concept_id, 0)

    return JSONResponse({
        "id": concept.id,
        "name": concept.name,
        "level": concept.level,
        "mastery": mastery,
        "mastery_percent": mastery * 25,
        "description_brief": concept.description_brief,
        "description_detailed": concept.description_detailed,
        "prerequisites": concept.prerequisites,
        "unlocks": concept_dag.get_unlocks(concept_id),
        "all_prerequisites": concept_dag.get_all_prerequisites(concept_id),
        "all_unlocks": concept_dag.get_all_unlocks(concept_id),
        "challenges": {
            "starter": concept.challenge_starter,
            "intermediate": concept.challenge_intermediate,
            "mastery": concept.challenge_mastery,
        },
        "gamepad_tutorial": concept.gamepad_tutorial,
        "gotchas": concept.gotchas,
        "fun_type": concept.fun_type,
        "fun_description": concept.fun_description,
    })


# ============================================================================
# Security & Authentication API
# ============================================================================


@app.get("/api/auth/status")
async def get_auth_status(player_id: str = "default"):
    """Check if player has security enabled and what methods are available."""
    db = get_database()
    player = db.get_or_create_player(player_id)

    return JSONResponse({
        "player_id": player_id,
        "has_password": db.has_password(player_id),
        "has_gamepad_combo": bool(player.gamepad_combo),
        "needs_auth": db.has_password(player_id) or bool(player.gamepad_combo),
    })


@app.post("/api/auth/set-password")
async def set_password(request: Request):
    """Set or update player password."""
    data = await request.json()
    player_id = data.get("player_id", "default")
    password = data.get("password", "")
    current_password = data.get("current_password")

    if not password:
        return JSONResponse({
            "success": False,
            "error": "Password is required",
        }, status_code=400)

    if len(password) < 4:
        return JSONResponse({
            "success": False,
            "error": "Password must be at least 4 characters",
        }, status_code=400)

    db = get_database()

    # If already has password, require current password to change
    if db.has_password(player_id):
        if not current_password:
            return JSONResponse({
                "success": False,
                "error": "Current password required to change password",
            }, status_code=401)
        if not db.verify_password(player_id, current_password):
            return JSONResponse({
                "success": False,
                "error": "Current password is incorrect",
            }, status_code=401)

    db.set_password(player_id, password)

    return JSONResponse({
        "success": True,
        "message": "Password set successfully",
    })


@app.post("/api/auth/verify-password")
async def verify_password(request: Request):
    """Verify player password for login."""
    data = await request.json()
    player_id = data.get("player_id", "default")
    password = data.get("password", "")

    db = get_database()

    if not db.has_password(player_id):
        return JSONResponse({
            "success": True,
            "message": "No password required",
            "session_id": None,
        })

    if db.verify_password(player_id, password):
        session_id = db.create_session(player_id, auth_method="password")
        return JSONResponse({
            "success": True,
            "message": "Password verified",
            "session_id": session_id,
        })
    else:
        return JSONResponse({
            "success": False,
            "error": "Invalid password",
        }, status_code=401)


@app.post("/api/auth/remove-password")
async def remove_password(request: Request):
    """Remove password protection (requires current password)."""
    data = await request.json()
    player_id = data.get("player_id", "default")
    password = data.get("password", "")

    db = get_database()

    if not db.has_password(player_id):
        return JSONResponse({
            "success": True,
            "message": "No password to remove",
        })

    if not db.verify_password(player_id, password):
        return JSONResponse({
            "success": False,
            "error": "Invalid password",
        }, status_code=401)

    db.remove_password(player_id)

    return JSONResponse({
        "success": True,
        "message": "Password removed",
    })


@app.post("/api/auth/set-gamepad-combo")
async def set_gamepad_combo(request: Request):
    """
    Set custom gamepad combo unlock sequence.

    Example combos:
    - ["A", "B", "A", "A", "L3+R3"]  (classic A-B-A-A then hold sticks)
    - ["X", "Y", "X", "Y", "L3+R3"]  (X-Y pattern)
    - ["UP", "UP", "DOWN", "DOWN", "L3+R3"]  (Konami-style)

    The last element should be "L3+R3" for the hold confirmation.
    """
    data = await request.json()
    player_id = data.get("player_id", "default")
    combo = data.get("combo", [])
    password = data.get("password")  # Required if password is set

    if not combo or len(combo) < 2:
        return JSONResponse({
            "success": False,
            "error": "Combo must have at least 2 elements",
        }, status_code=400)

    # Validate combo elements
    valid_buttons = {"A", "B", "X", "Y", "L", "R", "UP", "DOWN", "LEFT", "RIGHT", "L3+R3", "L1", "R1", "L2", "R2"}
    for btn in combo:
        if btn not in valid_buttons:
            return JSONResponse({
                "success": False,
                "error": f"Invalid button '{btn}'. Valid: {', '.join(sorted(valid_buttons))}",
            }, status_code=400)

    db = get_database()

    # If password is set, require it to change combo
    if db.has_password(player_id):
        if not password:
            return JSONResponse({
                "success": False,
                "error": "Password required to set gamepad combo",
            }, status_code=401)
        if not db.verify_password(player_id, password):
            return JSONResponse({
                "success": False,
                "error": "Invalid password",
            }, status_code=401)

    db.set_gamepad_combo(player_id, combo)

    return JSONResponse({
        "success": True,
        "message": f"Gamepad combo set: {' → '.join(combo)}",
        "combo": combo,
    })


@app.get("/api/auth/get-gamepad-combo")
async def get_gamepad_combo(player_id: str = "default"):
    """Get current gamepad combo (without revealing full sequence for security)."""
    db = get_database()
    combo = db.get_gamepad_combo(player_id)

    if not combo:
        return JSONResponse({
            "has_combo": False,
            "combo_length": 0,
            "hint": None,
        })

    return JSONResponse({
        "has_combo": True,
        "combo_length": len(combo),
        "hint": f"Starts with {combo[0]}, ends with {combo[-1]}",
    })


@app.post("/api/auth/verify-gamepad-combo")
async def verify_gamepad_combo(request: Request):
    """Verify gamepad combo for unlock."""
    data = await request.json()
    player_id = data.get("player_id", "default")
    combo = data.get("combo", [])

    db = get_database()
    stored_combo = db.get_gamepad_combo(player_id)

    if not stored_combo:
        return JSONResponse({
            "success": True,
            "message": "No gamepad combo required",
            "session_id": None,
        })

    if combo == stored_combo:
        session_id = db.create_session(player_id, auth_method="gamepad")
        return JSONResponse({
            "success": True,
            "message": "Combo verified!",
            "session_id": session_id,
        })
    else:
        return JSONResponse({
            "success": False,
            "error": "Invalid combo",
        }, status_code=401)


@app.post("/api/auth/remove-gamepad-combo")
async def remove_gamepad_combo(request: Request):
    """Remove gamepad combo (requires password if set)."""
    data = await request.json()
    player_id = data.get("player_id", "default")
    password = data.get("password")

    db = get_database()

    if db.has_password(player_id):
        if not password:
            return JSONResponse({
                "success": False,
                "error": "Password required to remove gamepad combo",
            }, status_code=401)
        if not db.verify_password(player_id, password):
            return JSONResponse({
                "success": False,
                "error": "Invalid password",
            }, status_code=401)

    db.set_gamepad_combo(player_id, [])

    return JSONResponse({
        "success": True,
        "message": "Gamepad combo removed",
    })


@app.get("/api/auth/session/{session_id}")
async def verify_session(session_id: str):
    """Verify a session is valid."""
    db = get_database()
    player_id = db.verify_session(session_id)

    if player_id:
        return JSONResponse({
            "valid": True,
            "player_id": player_id,
        })
    else:
        return JSONResponse({
            "valid": False,
        }, status_code=401)


@app.post("/api/auth/logout")
async def logout(request: Request):
    """End a session."""
    data = await request.json()
    session_id = data.get("session_id")

    if session_id:
        db = get_database()
        db.delete_session(session_id)

    return JSONResponse({
        "success": True,
        "message": "Logged out",
    })


# ============================================================================
# Static File Serving - Vue.js SPA
# ============================================================================


# Mount static assets (CSS, JS, images from Vue build)
if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve Vue.js SPA - all non-API routes serve index.html."""
    # Serve index.html for SPA routing
    index_path = DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")

    # Fallback for development (when frontend hasn't been built)
    return JSONResponse({
        "error": "Frontend not built",
        "message": "Run 'npm run build' in lmsp/web/frontend/ first",
        "api_available": True,
    }, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


# Self-teaching note:
#
# This file demonstrates:
# - FastAPI web framework (Level 6: Web development)
# - Async/await for async endpoints (Level 5-6)
# - Path operations and routing (Level 5+)
# - JSON API design (Level 5+)
# - SPA serving pattern (Level 6+)
# - CORS middleware for development (Level 6+)
#
# Key architectural decisions:
# - Pure JSON API (no HTMX, no server-side HTML)
# - Vue.js handles all UI rendering
# - Catch-all route for SPA client-side routing
# - CORS enabled for local development
