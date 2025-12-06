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
import subprocess
import sys

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# LMSP imports
from lmsp.python.challenges import ChallengeLoader, Challenge
from lmsp.python.validator import CodeValidator, PytestValidator
from lmsp.python.concepts import ConceptDAG
from lmsp.python.concept_lessons import get_lesson_loader, ConceptLesson
from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile
from lmsp.adaptive.director import Director, DirectorObservation, get_director
from lmsp.ui.achievements import AchievementManager
from lmsp.web.database import get_database, LMSPDatabase
from datetime import datetime, timedelta


def capture_player_stdout(code: str, timeout: int = 5) -> str:
    """Run player code directly and capture its stdout.

    This runs the code in a subprocess to safely capture any print() output.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "[Code timed out]"
    except Exception as e:
        return f"[Error capturing output: {e}]"


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


def get_current_player(
    x_session_id: Optional[str] = Header(None),
    x_player_id: Optional[str] = Header(None),
) -> str:
    """
    Extract player_id from request headers.

    Priority:
    1. X-Session-ID header -> validate session -> get player_id from DB
    2. X-Player-ID header -> use directly (for profiles without passwords)
    3. Return "default" as fallback

    This is more secure than URL params since:
    - Session tokens are cryptographically random
    - Headers aren't logged in URLs
    - Can't be shared accidentally via copy/paste URL
    """
    db = get_database()

    # Try session-based auth first (most secure)
    if x_session_id:
        player_id = db.verify_session(x_session_id)
        if player_id:
            return player_id

    # Fall back to player_id header (for passwordless profiles)
    if x_player_id:
        return x_player_id

    # Default fallback
    return "default"


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
    xp_earned: int,
    xp_reason: str
):
    """Record a challenge completion to database."""
    db = get_database()

    # Record completion
    db.record_completion(player_id, challenge_id, time_seconds)

    # Add XP
    db.add_player_xp(player_id, xp_earned)

    # Record XP event for history tracking
    db.record_xp_event(
        player_id=player_id,
        xp_amount=xp_earned,
        reason=xp_reason,
        challenge_id=challenge_id,
        solve_time=time_seconds
    )


def find_concept_for_challenge(challenge_id: str) -> Optional[str]:
    """Find the concept that this challenge belongs to."""
    for concept_id, concept in concept_dag.concepts.items():
        if (concept.challenge_starter == challenge_id or
            concept.challenge_intermediate == challenge_id or
            concept.challenge_mastery == challenge_id):
            return concept_id
    return None


def find_challenges_for_concept(concept_id: str) -> list[str]:
    """Find all challenges that teach a specific concept."""
    challenges = []

    # First check if there's a concept with this exact ID
    concept = concept_dag.concepts.get(concept_id)
    if concept:
        if concept.challenge_starter:
            challenges.append(concept.challenge_starter)
        if concept.challenge_intermediate:
            challenges.append(concept.challenge_intermediate)
        if concept.challenge_mastery:
            challenges.append(concept.challenge_mastery)

    # If no concept found or no challenges, try finding challenges by name match
    # The Director tracks by challenge_id, so we might need to return that directly
    if not challenges:
        # Check if this is actually a challenge_id
        try:
            challenge = challenge_loader.load(concept_id)
            if challenge:
                challenges.append(concept_id)
        except FileNotFoundError:
            pass

    return challenges


def get_suggested_lessons_for_challenge(challenge_id: str) -> list[dict]:
    """
    Get concept lessons relevant when a player is struggling with a challenge.

    Returns the lesson for this challenge's concept AND all its prerequisites,
    ordered from most basic (prerequisites first) to the target concept.

    Uses multiple strategies to find relevant concepts:
    1. Direct DAG mapping (challenge_starter/intermediate/mastery)
    2. Name/ID matching (e.g., 'personal_greeting' -> 'variables')
    3. Level-based matching (same level concepts)
    """
    loader = get_lesson_loader()
    suggestions = []
    seen_ids = set()

    # Strategy 1: Find concept via DAG mapping
    concept_id = find_concept_for_challenge(challenge_id)

    # Strategy 2: Try to find concept by matching challenge keywords to concept IDs
    if not concept_id:
        # Load the challenge to get its description and level
        try:
            challenge = challenge_loader.load(challenge_id)
            challenge_level = challenge.level

            # Build a list of keywords from challenge name, id, and description
            keywords = set()
            keywords.update(challenge_id.lower().replace('_', ' ').split())
            keywords.update(challenge.name.lower().replace('_', ' ').split())

            # Common concept keywords to look for (values must be actual concept IDs!)
            concept_keywords = {
                'greeting': ['strings', 'variables', 'print_function'],
                'hello': ['print_function', 'strings'],
                'math': ['basic_operators', 'numbers', 'types'],
                'temperature': ['basic_operators', 'variables', 'types'],
                'converter': ['basic_operators', 'types', 'type_conversion'],
                'calculator': ['basic_operators', 'numbers'],
                'list': ['lists'],
                'dict': ['dictionaries'],
                'loop': ['for_loops', 'while_loops', 'for_loops_basics'],
                'function': ['functions', 'def_return'],
                'class': ['classes'],
                # String operations
                'name': ['strings', 'variables', 'len_function'],
                'length': ['strings', 'len_function'],
                'len': ['strings', 'len_function'],
                'string': ['strings', 'string_methods'],
                'format': ['strings', 'string_methods'],
                'print': ['print_function', 'strings'],
                # Input operations
                'input': ['input_function', 'variables'],
                'guess': ['input_function', 'if_else', 'while_loops'],
                'number': ['numbers', 'types', 'type_conversion'],
            }

            # Find matching concepts
            potential_concepts = set()
            for keyword in keywords:
                if keyword in concept_keywords:
                    potential_concepts.update(concept_keywords[keyword])

            # Also try direct concept ID match (e.g., 'variables' challenge -> 'variables' concept)
            all_lessons = loader.get_all()
            lesson_ids = {l.id for l in all_lessons}

            for keyword in keywords:
                if keyword in lesson_ids:
                    potential_concepts.add(keyword)

            # Filter to concepts at or below the challenge level
            valid_concepts = []
            for pc in potential_concepts:
                lesson = loader.get(pc)
                if lesson and lesson.level <= challenge_level + 1:  # Allow one level higher
                    valid_concepts.append((lesson.level, pc))

            # Sort by level (lowest first) and pick the most relevant
            if valid_concepts:
                valid_concepts.sort()
                concept_id = valid_concepts[-1][1]  # Pick highest relevant level

        except FileNotFoundError:
            pass

    # Strategy 3: If still no concept, find concepts at the same level
    if not concept_id:
        try:
            challenge = challenge_loader.load(challenge_id)
            all_lessons = loader.get_all()
            level_lessons = [l for l in all_lessons if l.level == challenge.level]
            if level_lessons:
                # Return first few concepts at this level
                for lesson in level_lessons[:3]:
                    suggestions.append({
                        "id": lesson.id,
                        "name": lesson.name,
                        "level": lesson.level,
                        "category": lesson.category,
                        "time_to_read": lesson.time_to_read,
                        "has_try_it": lesson.try_it is not None,
                        "depth": 0,
                    })
                return suggestions
        except FileNotFoundError:
            return []

    if not concept_id:
        return []

    # Get the main concept lesson
    main_lesson = loader.get(concept_id)
    if not main_lesson:
        return []

    # Recursively collect prerequisites (depth-first, then reverse for breadth-first order)
    def collect_prerequisites(lesson_id: str, depth: int = 0):
        if lesson_id in seen_ids or depth > 5:  # Prevent cycles and limit depth
            return []
        seen_ids.add(lesson_id)

        lesson = loader.get(lesson_id)
        if not lesson:
            return []

        result = []
        # First collect prerequisites of this lesson
        for prereq_id in lesson.prerequisites:
            result.extend(collect_prerequisites(prereq_id, depth + 1))

        # Then add this lesson
        result.append({
            "id": lesson.id,
            "name": lesson.name,
            "level": lesson.level,
            "category": lesson.category,
            "time_to_read": lesson.time_to_read,
            "has_try_it": lesson.try_it is not None,
            "depth": depth,  # 0 = main concept, higher = more foundational
        })

        return result

    # Collect all lessons starting from main concept
    suggestions = collect_prerequisites(concept_id)

    # Reverse so prerequisites come first (foundational → target)
    suggestions.reverse()

    return suggestions


def get_mastery_hint(concept_id: str, current_mastery: int, is_lesson: bool = False) -> str:
    """
    Get a 60-140 char hint for the next mastery stage.

    For concept lessons (is_lesson=True):
    - The lesson IS the content, no challenge needed to start

    For old-style concepts:
    - Mastery levels tied to challenge completion
    """
    # For concept lessons - the lesson IS the content
    if is_lesson:
        loader = get_lesson_loader()
        lesson = loader.get(concept_id)
        name = lesson.name if lesson else concept_id

        if current_mastery == 0:
            if lesson and lesson.try_it:
                return f"Read the lesson and try the interactive exercise!"
            return f"Read this lesson to learn about {name}."
        elif current_mastery == 1:
            return f"Good start! Practice more to solidify your understanding of {name}."
        elif current_mastery == 2:
            return f"Getting stronger! Keep practicing {name} concepts."
        elif current_mastery == 3:
            return f"Almost there! One more review to master {name}."
        else:  # mastery == 4
            return f"You've mastered {name}! Return for spaced repetition bonuses."

    # Old-style concept (from concept_dag with challenge associations)
    concept = concept_dag.concepts.get(concept_id)
    if not concept:
        return "Keep practicing to increase mastery."

    name = concept.name

    if current_mastery == 0:
        if concept.challenge_starter:
            return f"Complete '{concept.challenge_starter}' to begin learning {name}."
        return f"Complete related challenges to learn {name}."

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
async def get_profile(player_id: str = Depends(get_current_player)):
    """Get player profile data."""
    db = get_database()
    engine = get_adaptive_engine(player_id)
    profile_data = engine.profile

    # Get player data including display_name
    player_data = db.get_or_create_player(player_id)

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
        "display_name": player_data.display_name,
        "mastery_levels": profile_data.mastery_levels,
        "xp": total_xp,
        "level": player_level,
        "challenges_completed": len(completions),
        "achievements_unlocked": achievement_stats["unlocked"],
        "achievements_total": achievement_stats["total"],
    })


@app.post("/api/profile/display-name")
async def set_display_name(request: Request):
    """Set player's display name."""
    data = await request.json()
    player_id = data.get("player_id", "default")
    display_name = data.get("display_name", "").strip()

    if not display_name:
        return JSONResponse({"error": "Display name cannot be empty"}, status_code=400)

    if len(display_name) > 50:
        return JSONResponse({"error": "Display name too long (max 50 chars)"}, status_code=400)

    db = get_database()
    db.set_display_name(player_id, display_name)

    return JSONResponse({"success": True, "display_name": display_name})


@app.get("/api/challenges")
async def list_challenges(level: Optional[int] = None, player_id: str = Depends(get_current_player)):
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
                    "challenge_mode": challenge.challenge_mode,
                    "is_multi_stage": len(challenge.stages) > 0,
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
async def get_all_challenge_progress(player_id: str = Depends(get_current_player)):
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
async def get_challenge(challenge_id: str, player_id: str = Depends(get_current_player)):
    """Get a specific challenge and record access."""
    try:
        challenge = challenge_loader.load(challenge_id)

        # Record that this player accessed this challenge
        db = get_database()
        db.record_lesson_access(player_id, challenge_id, "challenge")

        # Build stages data if this is a multi-stage challenge
        stages_data = []
        for stage in challenge.stages:
            stages_data.append({
                "stage_number": stage.stage_number,
                "name": stage.name,
                "description": stage.description,
                "skeleton_code": stage.skeleton_code,
                "test_count": len(stage.test_cases),
                "hints": stage.hints,
            })

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
            # New fields for time attack and multi-stage
            "challenge_mode": challenge.challenge_mode,
            "time_limit_seconds": challenge.time_limit_seconds,
            "speed_run_target": challenge.speed_run_target,
            "stages": stages_data if stages_data else None,
            "is_multi_stage": len(stages_data) > 0,
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")


@app.get("/api/lesson-access/{lesson_id}")
async def get_lesson_access(lesson_id: str, player_id: str = Depends(get_current_player), since: Optional[str] = None):
    """
    Get the most recent access time for a lesson/challenge.

    Query params:
    - player_id: Player to check (default: "default")
    - since: Only return access after this ISO timestamp

    Returns: {lesson_id, lesson_type, accessed_at} or null if not accessed
    """
    db = get_database()
    access = db.get_lesson_access(player_id, lesson_id, since)
    return JSONResponse({"access": access})


@app.get("/api/lesson-access")
async def get_all_lesson_access(player_id: str = Depends(get_current_player), since: Optional[str] = None):
    """
    Get all lesson access records for a player.

    Query params:
    - player_id: Player to check (default: "default")
    - since: Only return access after this ISO timestamp

    Returns: {accesses: [{lesson_id, lesson_type, accessed_at}, ...]}
    """
    db = get_database()
    accesses = db.get_all_lesson_access(player_id, since)
    return JSONResponse({"accesses": accesses})


@app.get("/api/observations")
async def get_observations(
    player_id: str = Depends(get_current_player),
    since: Optional[str] = None,
    challenge_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get recent Director observations (attempts) for a player.

    Real-time feedback for the interview timer - see successes AND failures as they happen.

    Query params:
    - player_id: Player to check (default: "default")
    - since: Only return observations after this ISO timestamp
    - challenge_id: Only return observations for this specific challenge
    - limit: Max observations to return (default: 50)

    Returns: {observations: [{challenge_id, success, error, tests_passing, tests_total,
                              time_seconds, attempt_number, timestamp}, ...]}
    """
    db = get_database()
    observations = db.load_director_observations(
        player_id,
        limit=min(limit, 100),
        since=since,
        challenge_id=challenge_id
    )
    return JSONResponse({"observations": observations})


@app.post("/api/code/run")
async def run_code(request: Request):
    """
    Quick code execution - returns stdout immediately without running tests.

    Use this for instant console output while tests are still running.
    """
    data = await request.json()
    code = data.get("code", "")

    if not code:
        return JSONResponse({"stdout": ""})

    stdout = capture_player_stdout(code)
    return JSONResponse({"stdout": stdout})


@app.post("/api/code/submit")
async def submit_code(request: Request, player_id: str = Depends(get_current_player)):
    """Submit code for validation with XP and mastery tracking.

    Accepts either challenge_id (for challenges) or lesson_id (for concept try_it).
    Both use the same validation logic: pytest if configured, legacy otherwise.
    """
    data = await request.json()
    challenge_id = data.get("challenge_id")
    lesson_id = data.get("lesson_id")  # For concept try_it exercises
    code = data.get("code", "")
    is_spaced_repetition = data.get("is_spaced_repetition", False)
    current_stage = data.get("stage", None)  # For multi-stage challenges
    solve_time = data.get("solve_time", None)  # Wall-clock coding time from frontend

    if not code:
        return JSONResponse({
            "success": False,
            "error": "code is required",
            "tests_passing": 0,
            "tests_total": 0,
        }, status_code=400)

    if not challenge_id and not lesson_id:
        return JSONResponse({
            "success": False,
            "error": "challenge_id or lesson_id is required",
            "tests_passing": 0,
            "tests_total": 0,
        }, status_code=400)

    # Handle concept lesson validation (with XP tracking, same as challenges)
    if lesson_id:
        loader = get_lesson_loader()
        lesson = loader.get(lesson_id)
        if not lesson:
            return JSONResponse({
                "success": False,
                "error": f"Lesson '{lesson_id}' not found",
                "tests_passing": 0,
                "tests_total": 0,
            }, status_code=404)

        # Use pytest validation - REQUIRED for all concepts
        if lesson.validation_type == "pytest" and lesson.test_file:
            pytest_validator = PytestValidator(CONCEPTS_DIR, timeout_seconds=30)
            result = pytest_validator.validate(code, lesson_id, lesson.test_file)
        else:
            # Concept missing pytest validation - return error
            return JSONResponse({
                "success": False,
                "error": f"Concept '{lesson_id}' missing pytest validation. Add [validation] section with type='pytest' and test_file.",
                "tests_passing": 0,
                "tests_total": 0,
            }, status_code=500)

        # Capture player's print() output by running their code directly
        player_stdout = capture_player_stdout(code)

        response_data = {
            "success": result.success,
            "tests_passing": result.tests_passing,
            "tests_total": result.tests_total,
            "output": result.output,
            "stdout": player_stdout,  # User print() output, captured directly
            "error": result.error,
            "test_results": [
                {
                    "name": tr.test_name,
                    "passed": tr.passed,
                    "expected": tr.expected,
                    "actual": tr.actual,
                    "error": tr.error,
                }
                for tr in result.test_results
            ],
        }

        # Award XP on success (concepts award XP based on level)
        if result.success:
            db = get_database()
            lesson_key = f"concept:{lesson_id}"

            # Check if already completed
            completions = get_player_completions(player_id)
            already_completed = lesson_key in completions

            # XP based on level: Level 0 = 10 XP, Level 1 = 15 XP, etc.
            base_xp = 10 + (lesson.level * 5)

            if already_completed:
                # Repeat completion: reduced XP
                xp_earned = max(2, base_xp // 5)
                xp_reason = f"Concept review: {lesson.name} (+{xp_earned} XP)"
            else:
                xp_earned = base_xp
                xp_reason = f"Concept mastered: {lesson.name} (+{xp_earned} XP)"

            # Record completion and award XP
            db.record_completion(player_id, lesson_key, 0)  # No solve time tracked for concepts yet
            db.add_player_xp(player_id, xp_earned)
            db.record_xp_event(
                player_id=player_id,
                xp_amount=xp_earned,
                reason=xp_reason,
                challenge_id=lesson_key,
                solve_time=0
            )

            # Update mastery tracking (was missing!)
            engine = get_adaptive_engine(player_id)
            engine.observe_attempt(
                concept=lesson_id,  # Use plain lesson_id for mastery (no prefix)
                success=True,
                time_seconds=0,  # Concept lessons don't track solve time yet
            )
            new_mastery = engine.profile.mastery_levels.get(lesson_id, 0)
            save_mastery_to_database(player_id, lesson_id, new_mastery)

            response_data["xp_earned"] = xp_earned
            response_data["xp_reason"] = xp_reason
            response_data["total_xp"] = get_player_xp(player_id)
            response_data["mastery_level"] = new_mastery
            response_data["mastery_percent"] = int(new_mastery * 25)

        return JSONResponse(response_data)

    # Handle challenge validation (full path with XP/mastery tracking)
    try:
        challenge = challenge_loader.load(challenge_id)
        is_multi_stage = len(challenge.stages) > 0
        total_stages = len(challenge.stages) if is_multi_stage else 0

        # Use the appropriate validator based on challenge config
        if challenge.validation_type == "pytest" and challenge.test_file:
            pytest_validator = PytestValidator(CHALLENGES_DIR, timeout_seconds=30)

            # For multi-stage challenges, filter tests by current stage
            test_pattern = None
            if is_multi_stage and current_stage is not None:
                test_pattern = f"test_stage{current_stage}"

            result = pytest_validator.validate(
                code, challenge.id, challenge.test_file, test_pattern
            )
        else:
            result = code_validator.validate(code, challenge.test_cases)

        # Capture player's print() output by running their code directly
        player_stdout = capture_player_stdout(code)

        engine = get_adaptive_engine(player_id)
        achievement_mgr = get_achievement_manager(player_id)

        # Use frontend's wall-clock time if provided, else fall back to test execution time
        actual_solve_time = solve_time if solve_time is not None else result.time_seconds

        response_data = {
            "success": result.success,
            "tests_passing": result.tests_passing,
            "tests_total": result.tests_total,
            "time_seconds": actual_solve_time,  # Return the actual solve time, not test execution time
            "output": result.output,
            "stdout": player_stdout,  # User print() output, captured directly
        }

        # Add multi-stage information
        if is_multi_stage:
            response_data["is_multi_stage"] = True
            response_data["total_stages"] = total_stages
            response_data["current_stage"] = current_stage

            if result.success and current_stage is not None:
                # Stage passed - check if there's a next stage
                if current_stage < total_stages:
                    response_data["stage_complete"] = True
                    response_data["next_stage"] = current_stage + 1
                    response_data["challenge_complete"] = False

                    # Get next stage info
                    next_stage_data = challenge.stages[current_stage]  # 0-indexed
                    response_data["next_stage_info"] = {
                        "stage_number": next_stage_data.stage_number,
                        "name": next_stage_data.name,
                        "description": next_stage_data.description,
                    }
                else:
                    # Final stage complete - whole challenge done
                    response_data["stage_complete"] = True
                    response_data["challenge_complete"] = True
            else:
                response_data["stage_complete"] = False
                response_data["challenge_complete"] = False

        if result.error:
            response_data["error"] = result.error

        if result.success:
            # XP logic for multi-stage challenges:
            # - Award proportional XP on first completion of each stage
            # - No XP for repeating a stage before challenge is fully complete
            # - After challenge complete, spaced repetition bonuses apply
            db = get_database()

            if is_multi_stage and current_stage is not None:
                # Check if this stage was already completed
                stage_key = f"{challenge_id}_stage{current_stage}"
                stage_completions = db.get_completions(player_id)
                stage_already_done = stage_key in stage_completions

                if stage_already_done:
                    # Already completed this stage - no XP until challenge is fully done
                    xp_earned = 0
                    xp_reason = f"Stage {current_stage}/{total_stages} already completed - finish challenge for repeat XP"
                else:
                    # First time completing this stage - award proportional XP
                    stage_xp = challenge.points // total_stages
                    xp_earned = stage_xp
                    xp_reason = f"Stage {current_stage}/{total_stages} complete: +{xp_earned} XP"

                    # Record stage completion
                    db.record_completion(player_id, stage_key, actual_solve_time)
                    db.add_player_xp(player_id, xp_earned)
                    db.record_xp_event(
                        player_id=player_id,
                        xp_amount=xp_earned,
                        reason=xp_reason,
                        challenge_id=stage_key,
                        solve_time=actual_solve_time
                    )

                # If this was the final stage, also record overall challenge completion
                if current_stage == total_stages:
                    record_challenge_completion(
                        player_id, challenge_id, actual_solve_time, 0,
                        f"Challenge complete (XP already awarded per stage)"
                    )
            else:
                # Non-multi-stage challenge - use standard XP logic
                xp_earned, xp_reason = calculate_xp_reward(
                    challenge, player_id, actual_solve_time, is_spaced_repetition
                )
                record_challenge_completion(
                    player_id, challenge_id, actual_solve_time, xp_earned, xp_reason
                )

            # Find associated concept and update mastery
            concept_id = find_concept_for_challenge(challenge_id)
            mastery_info = None

            if concept_id:
                # Observe attempt for adaptive engine
                engine.observe_attempt(
                    concept=concept_id,
                    success=True,
                    time_seconds=actual_solve_time,
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
                    time_seconds=actual_solve_time,
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
                time_seconds=actual_solve_time,
            )

        # ====================================================================
        # THE DIRECTOR - Observe this attempt for adaptive intervention
        # ====================================================================
        director = get_director(player_id, db=get_database())

        # Count attempt number for this challenge
        recent_obs = [o for o in director._observations
                      if o.challenge_id == challenge_id]
        attempt_number = len(recent_obs) + 1

        # Get concepts taught by this challenge for mastery tracking
        challenge_concept = find_concept_for_challenge(challenge_id)
        concepts_learned = [challenge_concept] if challenge_concept else []

        director.observe(DirectorObservation(
            player_id=player_id,
            challenge_id=challenge_id,
            code=code,
            success=result.success,
            error=result.error,
            output=result.output,
            tests_passing=result.tests_passing,
            tests_total=result.tests_total,
            time_seconds=actual_solve_time,
            attempt_number=attempt_number,
            concepts=concepts_learned,
        ))

        # Check if Director wants to intervene
        if director.should_intervene() and not result.success:
            intervention = director.get_intervention()
            if intervention:
                response_data["director_intervention"] = {
                    "type": intervention.type,
                    "content": intervention.content,
                    "reason": intervention.reason,
                    "confidence": intervention.confidence,
                }
                # If Director generated a new challenge, include it
                if intervention.generated_challenge:
                    response_data["director_generated_challenge"] = intervention.generated_challenge

                # Build unified suggestions list: struggles + concepts
                suggestions = []

                # Add the detected struggle as first item
                suggestions.append({
                    "item_type": "struggle",
                    "id": f"struggle_{intervention.type}",
                    "name": intervention.reason,
                    "content": intervention.content,
                    "category": "Detected Issue",
                    "level": 0,
                    "time_to_read": 0,
                    "has_try_it": False,
                })

                # Add concept lessons
                concept_lessons = get_suggested_lessons_for_challenge(challenge_id)
                for lesson in concept_lessons:
                    lesson["item_type"] = "concept"
                    suggestions.append(lesson)

                response_data["director_intervention"]["suggested_lessons"] = suggestions

        # Even without a full intervention, suggest lessons after multiple failures
        elif not result.success:
            # Count recent failures for this challenge
            recent_failures = sum(
                1 for o in director._observations[-10:]
                if o.challenge_id == challenge_id and not o.success
            )
            # After 2+ failures, suggest reviewing the concept
            if recent_failures >= 2:
                suggested_lessons = get_suggested_lessons_for_challenge(challenge_id)
                if suggested_lessons:
                    # Tag each as a concept
                    for lesson in suggested_lessons:
                        lesson["item_type"] = "concept"
                    response_data["suggested_lessons"] = suggested_lessons
                    response_data["suggestion_reason"] = "review_after_failures"

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


@app.post("/api/code/run")
async def run_code(request: Request):
    """Run Python code and return output (for concept Try It exercises)."""
    import subprocess
    import tempfile

    data = await request.json()
    code = data.get("code", "")

    if not code.strip():
        return JSONResponse({
            "output": "",
            "error": "No code to run",
        })

    try:
        # Write code to temp file and run it
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ['python3', temp_path],
                capture_output=True,
                text=True,
                timeout=5,  # 5 second timeout
            )

            output = result.stdout
            error = result.stderr if result.returncode != 0 else None

            return JSONResponse({
                "output": output,
                "error": error,
            })
        finally:
            import os
            os.unlink(temp_path)

    except subprocess.TimeoutExpired:
        return JSONResponse({
            "output": "",
            "error": "Code execution timed out (5 second limit)",
        })
    except Exception as e:
        return JSONResponse({
            "output": "",
            "error": str(e),
        })


@app.get("/api/achievements")
async def list_achievements(player_id: str = Depends(get_current_player)):
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


@app.get("/api/xp/history")
async def get_xp_history(
    player_id: str = Depends(get_current_player),
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    period: Optional[str] = None
):
    """
    Get XP history for graphing.

    Query params:
    - start_time: ISO datetime string to filter from
    - end_time: ISO datetime string to filter to
    - period: 'hour', 'day', 'week', 'month', 'year' for aggregated data
    """
    db = get_database()

    if period:
        # Return aggregated stats by period
        stats = db.get_xp_stats_by_period(player_id, period)
        return JSONResponse({
            "aggregated": True,
            "period": period,
            "data": stats,
            "total_xp": sum(s["total_xp"] for s in stats),
            "total_events": sum(s["event_count"] for s in stats),
        })
    else:
        # Return raw XP events
        events = db.get_xp_history(player_id, start_time, end_time)

        # Calculate cumulative XP for line chart
        cumulative = 0
        for event in events:
            cumulative += event["xp_amount"]
            event["cumulative_xp"] = cumulative

        return JSONResponse({
            "aggregated": False,
            "data": events,
            "total_xp": cumulative,
            "total_events": len(events),
        })


@app.post("/api/emotional/record")
async def record_emotional_feedback(
    request: Request,
    player_id: str = Depends(get_current_player)
):
    """
    Record emotional feedback (RT/LT trigger values).

    Body:
        enjoyment: Satisfaction rating 0.0-1.0
        frustration: Frustration rating 0.0-1.0
        challenge_id: Optional challenge ID
        stage: Optional stage number
        context: Context string
        interacted: True if user actually interacted with sliders/triggers
                   If false and both values are 0, treat as "skipped"
    """
    data = await request.json()
    enjoyment = data.get("enjoyment", 0.0)
    frustration = data.get("frustration", 0.0)
    challenge_id = data.get("challenge_id")
    stage = data.get("stage")
    context = data.get("context", "")
    interacted = data.get("interacted", True)

    # Detect "skipped" - 0%/0% always means skip (neutral = no opinion = skip)
    # There's no meaningful "deliberately neutral" rating - it's just a skip
    skipped = (enjoyment == 0 and frustration == 0)

    # Store to database
    db = get_database()
    db.record_emotional_feedback(
        player_id=player_id,
        enjoyment=enjoyment,
        frustration=frustration,
        challenge_id=challenge_id,
        stage=stage,
        context=context,
        skipped=skipped
    )

    # Also feed to adaptive engine (for in-memory recommendations)
    engine = get_adaptive_engine(player_id)
    from lmsp.input.emotional import EmotionalDimension
    if enjoyment > 0:
        engine.observe_emotion(EmotionalDimension.ENJOYMENT, enjoyment, context)
    if frustration > 0:
        engine.observe_emotion(EmotionalDimension.FRUSTRATION, frustration, context)

    # Feed to The Director for intervention decisions
    director = get_director(player_id, db=get_database())
    director.observe_emotion(enjoyment, frustration)

    # Calculate mastery adjustment if we have challenge data
    mastery_factor = None
    if challenge_id and not skipped:
        mastery_factor = db.calculate_mastery_from_satisfaction(player_id, challenge_id)

    return JSONResponse({
        "success": True,
        "enjoyment": enjoyment,
        "frustration": frustration,
        "skipped": skipped,
        "mastery_factor": mastery_factor,
        "message": "Feedback recorded" if not skipped else "Rating skipped",
    })


@app.get("/api/recommendations")
async def get_recommendations(player_id: str = Depends(get_current_player)):
    """
    Get adaptive learning recommendations powered by The Director.

    Uses flow state optimization to recommend challenges that:
    - Match current skill level (not too easy, not too hard)
    - Build on momentum when player is doing well
    - Ease off when player is struggling
    - Avoid frustrating concepts temporarily
    - Resurface mastered concepts at the right time
    """
    engine = get_adaptive_engine(player_id)
    director = get_director(player_id, db=get_database())
    db = get_database()

    # Get Director's flow-optimized context
    flow = director.get_flow_recommendation()
    mastery = engine.profile.mastery_levels

    # Get player's completions to filter out already-done challenges
    completions = db.get_completions(player_id)

    # Collect all available items (challenges AND concept lessons)
    available_items = []

    # 1. Load challenges directly from challenge_loader
    for challenge_id in challenge_loader.list_challenges():
        try:
            challenge = challenge_loader.load(challenge_id)

            # Check if this challenge has been completed
            is_completed = challenge_id in completions
            needs_review = False

            if is_completed:
                # Calculate retention to see if it needs review
                comp = completions[challenge_id]
                retention = calculate_retention_score(
                    completion_count=comp.count,
                    last_completed=comp.last_completed,
                    best_time=comp.best_time,
                    expected_time=60.0 * (1 + challenge.level * 0.5),
                )
                needs_review = retention.get("needs_review", False)

            available_items.append({
                "id": challenge_id,
                "type": "challenge",
                "concept_id": challenge_id,  # Use challenge ID as concept for mastery tracking
                "concept_name": challenge.name,
                "level": challenge.level,
                "concepts": [challenge_id],
                "mastery": mastery.get(challenge_id, 0),
                "is_completed": is_completed,
                "needs_review": needs_review,
            })
        except Exception:
            continue

    # 2. Load concept lessons
    lesson_loader = get_lesson_loader()
    for lesson in lesson_loader.get_all():
        try:
            lesson_id = lesson.id
            lesson_key = f"concept:{lesson_id}"  # Must match key used when recording completion

            # Check if lesson has been completed (use concept completions from db)
            is_completed = lesson_key in completions
            needs_review = False

            if is_completed:
                comp = completions[lesson_key]
                retention = calculate_retention_score(
                    completion_count=comp.count,
                    last_completed=comp.last_completed,
                    best_time=comp.best_time,
                    expected_time=30.0 * (1 + lesson.level * 0.3),  # Lessons are quicker
                )
                needs_review = retention.get("needs_review", False)

            available_items.append({
                "id": lesson_id,
                "type": "concept",
                "concept_id": lesson_id,
                "concept_name": lesson.name,
                "level": lesson.level,
                "concepts": [lesson_id],
                "mastery": mastery.get(lesson_id, 0),
                "is_completed": is_completed,
                "needs_review": needs_review,
            })
        except Exception:
            continue

    # Score each item for flow state fit
    scored_items = []
    for ch in available_items:
        # Skip completed challenges unless they need review (spaced repetition)
        if ch["is_completed"] and not ch["needs_review"]:
            continue

        # Skip if player has fully mastered (mastery >= 3)
        # Exception: allow replaying CHALLENGES in easy_win mode for confidence boost
        # But NEVER re-recommend concept lessons - they're read-once content
        if ch["mastery"] >= 3:
            if ch["type"] == "concept":
                continue  # Never recommend mastered concept lessons
            elif flow["difficulty_target"] != "easy_win":
                continue  # Only allow mastered challenges in easy_win mode

        score = director.score_challenge_for_flow(ch)

        # Strong bonus for unstarted/uncompleted challenges (prioritize new content!)
        if not ch["is_completed"]:
            score += 0.3

        # Bonus for unstarted challenges at appropriate level
        if ch["mastery"] == 0:
            if flow["difficulty_target"] == "easy_win" and ch["level"] == 0:
                score += 0.2
            elif flow["difficulty_target"] == "balanced" and ch["level"] <= 1:
                score += 0.15

        # Penalize if concept is in avoid list
        if ch["concept_id"] in flow.get("avoid_concepts", []):
            score -= 0.3

        scored_items.append((score, ch))

    # Sort by score (highest first)
    scored_items.sort(key=lambda x: x[0], reverse=True)

    # Pick the best match
    if scored_items:
        best_score, best_item = scored_items[0]
        item_id = best_item["id"]
        item_type = best_item["type"]
        concept_id = best_item["concept_id"]
        concept_name = best_item["concept_name"]
        confidence = min(0.95, best_score)
    else:
        # Fallback: hello_world challenge for complete beginners
        item_id = "hello_world"
        item_type = "challenge"
        concept_id = "hello_world"
        concept_name = "Hello World"
        confidence = 0.5
        best_item = {"mastery": 0, "is_completed": False, "needs_review": False, "level": 0}

    # Generate a specific reason explaining WHY this item was chosen
    def build_specific_reason(item: dict, flow_ctx: dict, item_concept_id: str) -> str:
        """Build an insightful reason explaining the recommendation."""
        reasons = []
        item_mastery = item.get("mastery", 0)
        is_completed = item.get("is_completed", False)
        needs_review = item.get("needs_review", False)
        item_level = item.get("level", 0)
        item_type = item.get("type", "challenge")
        difficulty_target = flow_ctx.get("difficulty_target", "balanced")

        # Primary reason based on mastery/completion state
        if needs_review:
            reasons.append("Due for spaced repetition review")
        elif item_mastery == 0 and not is_completed:
            # Fresh content - make it inviting!
            if item_type == "concept":
                reasons.append("Fresh concept to explore")
            else:
                reasons.append("New challenge waiting for you")
        elif item_mastery > 0 and item_mastery < 1:
            reasons.append("Almost there - one more practice to level up")
        elif item_mastery >= 1 and item_mastery < 2:
            reasons.append("You're learning this - practice builds mastery")
        elif item_mastery >= 2 and item_mastery < 3:
            reasons.append("Building solid foundation on this concept")
        elif is_completed and not needs_review:
            reasons.append("Good for reinforcement")

        # Secondary reason based on flow state
        if difficulty_target == "easy_win":
            if item_level == 0:
                reasons.append("Quick win to build momentum")
            else:
                reasons.append("Within your comfort zone")
        elif difficulty_target == "slightly_harder":
            reasons.append("Time to stretch your skills")
        elif difficulty_target == "easier" and flow_ctx.get("frustration", 0) > 0.4:
            reasons.append("Easing off to rebuild confidence")

        # Concept relationships
        prefer_concepts = flow_ctx.get("prefer_concepts", [])
        if item_concept_id in prefer_concepts:
            reasons.append("Builds on your recent progress")

        # Combine into a coherent sentence
        if reasons:
            return ". ".join(reasons[:2]) + "."
        return flow_ctx.get("reason", "Good next step!")

    specific_reason = build_specific_reason(best_item, flow, concept_id)

    # Build the response with rich flow context
    # action tells the frontend where to navigate
    action = "concept" if item_type == "concept" else "challenge"

    return JSONResponse({
        "action": action,
        "type": item_type,
        "concept": concept_name,
        "challenge_id": item_id,  # Keep for backwards compat
        "item_id": item_id,
        "reason": specific_reason,
        "confidence": round(confidence, 2),
        # Flow state context for UI
        "flow": {
            "momentum": flow["momentum"],
            "velocity": flow["learning_velocity"],
            "frustration": flow["frustration"],
            "difficulty_target": flow["difficulty_target"],
        },
        # For learning/debugging
        "alternatives": [
            {"id": ch["id"], "type": ch["type"], "concept": ch["concept_name"], "score": round(sc, 2)}
            for sc, ch in scored_items[1:4]  # Top 3 alternatives
        ] if len(scored_items) > 1 else [],
    })


@app.get("/api/skill-tree")
async def get_skill_tree(player_id: str = Depends(get_current_player), include: str = "both"):
    """
    Get unified skill tree data with concepts AND challenges.

    Query params:
    - player_id: Player ID for mastery tracking
    - include: "concepts", "challenges", or "both" (default)
    """
    engine = get_adaptive_engine(player_id)
    mastery_levels = engine.profile.mastery_levels
    db = get_database()
    completions = db.get_completions(player_id)
    loader = get_lesson_loader()

    nodes = []
    edges = []
    node_ids = set()  # Track all node IDs for edge validation

    # Build nodes for concept lessons (using ConceptLessonLoader which has prerequisites)
    if include in ("concepts", "both"):
        all_lessons = loader.get_all()

        # Group by level for x-position calculation
        lessons_by_level: dict[int, list] = {}
        for lesson in all_lessons:
            if lesson.level not in lessons_by_level:
                lessons_by_level[lesson.level] = []
            lessons_by_level[lesson.level].append(lesson)

        for lesson in all_lessons:
            concept_id = lesson.id
            node_ids.add(concept_id)

            # Get mastery level (0-4)
            mastery = mastery_levels.get(concept_id, 0)

            # Calculate x position within level
            level_lessons = lessons_by_level.get(lesson.level, [])
            x_index = level_lessons.index(lesson) if lesson in level_lessons else 0

            # Get mastery hint (is_lesson=True for concept lessons)
            mastery_hint = get_mastery_hint(concept_id, int(mastery), is_lesson=True)

            # Determine state based on prerequisites mastery
            prereqs = lesson.prerequisites or []
            prereqs_met = all(mastery_levels.get(p, 0) >= 2 for p in prereqs) if prereqs else True

            if mastery >= 4:
                state = "mastered"
            elif mastery > 0:
                state = "learning"
            elif prereqs_met:
                state = "available"
            else:
                state = "locked"

            # Find what this concept unlocks
            unlocks = [l.id for l in all_lessons if concept_id in (l.prerequisites or [])]

            nodes.append({
                "id": concept_id,
                "name": lesson.name,
                "level": lesson.level,
                "type": "concept",  # Node type for filtering
                "mastery": mastery,
                "mastery_percent": mastery * 25,
                "mastery_hint": mastery_hint,
                "description": f"📚 {lesson.category.replace('_', ' ').title()} concept",
                "prerequisites": prereqs,
                "unlocks": unlocks,
                "has_try_it": lesson.try_it is not None,
                "time_to_read": lesson.time_to_read,
                "challenges": {
                    "starter": None,
                    "intermediate": None,
                    "mastery": None,
                },
                "position": {"x": x_index * 200, "y": lesson.level * 150},
                "state": state,
            })

            # Create edges from prerequisites
            for prereq in prereqs:
                edges.append({"from": prereq, "to": concept_id})

    # Build nodes for challenges
    if include in ("challenges", "both"):
        raw_challenge_ids = set(challenge_loader.list_challenges())  # IDs without ch_ prefix
        # Load actual challenge objects, skip any with parse errors
        challenges = []
        for cid in raw_challenge_ids:
            try:
                challenges.append(challenge_loader.load(cid))
            except Exception as e:
                print(f"Warning: Failed to load challenge {cid}: {e}")
                continue

        # Group by level for x-position calculation
        challenges_by_level: dict[int, list] = {}
        for ch in challenges:
            if ch.level not in challenges_by_level:
                challenges_by_level[ch.level] = []
            challenges_by_level[ch.level].append(ch)

        for challenge in challenges:
            challenge_id = f"ch_{challenge.id}"  # Prefix to avoid ID collisions
            node_ids.add(challenge_id)

            # Check completion status and calculate Director-managed retention
            is_completed = challenge.id in completions
            comp = completions.get(challenge.id)

            if is_completed and comp:
                # Use Director's retention system (same as ChallengesView)
                expected_time = 60.0 * (1 + challenge.level * 0.5)
                retention_data = calculate_retention_score(
                    completion_count=comp.count,
                    last_completed=comp.last_completed,
                    best_time=comp.best_time,
                    expected_time=expected_time,
                )
                retention = retention_data["retention"]
                is_mastered = retention_data.get("mastered", False)
                needs_review = retention_data.get("needs_review", False)

                if is_mastered:
                    state = "mastered"
                    mastery_hint = "Mastered! 🎉"
                elif needs_review:
                    state = "learning"
                    mastery_hint = f"Retention at {int(retention)}% - review to strengthen!"
                else:
                    state = "learning"
                    mastery_hint = f"Retention at {int(retention)}% - keep practicing!"

                mastery_percent = retention
            else:
                # Not completed yet
                retention = 0
                mastery_percent = 0
                mastery_hint = "Not yet attempted"

                # Check if prereqs met
                prereqs = challenge.prerequisites or []
                prereqs_met = all(p in completions for p in prereqs) if prereqs else True
                state = "available" if prereqs_met else "locked"

            # Calculate x position within level (offset from concepts)
            level_challenges = challenges_by_level.get(challenge.level, [])
            concept_count = len(lessons_by_level.get(challenge.level, [])) if include == "both" else 0
            x_index = concept_count + level_challenges.index(challenge) if challenge in level_challenges else concept_count

            # Convert retention (0-100) to mastery scale (0-4) for consistent node sizing
            mastery = retention / 25.0 if retention > 0 else 0

            nodes.append({
                "id": challenge_id,
                "name": challenge.name,
                "level": challenge.level,
                "type": "challenge",  # Node type for filtering
                "mastery": mastery,  # 0-4 scale for node radius calculation
                "retention": retention,  # Director-managed retention (0-100)
                "mastery_percent": mastery_percent,  # Same as retention for challenges
                "mastery_hint": mastery_hint,
                "needs_review": needs_review if is_completed else False,
                "description": f"🎮 {challenge.points} XP challenge",
                # Prerequisites can be challenge IDs OR concept IDs - normalize them
                "prerequisites": [
                    f"ch_{p}" if p in raw_challenge_ids else p
                    for p in (challenge.prerequisites or [])
                ],
                "unlocks": [],
                "challenges": {
                    "starter": challenge.id,
                    "intermediate": None,
                    "mastery": None,
                },
                "position": {"x": x_index * 200, "y": challenge.level * 150},
                "state": state,
            })

            # Create edges from prerequisites (can be challenge or concept IDs)
            for prereq in (challenge.prerequisites or []):
                # Normalize: if it's a challenge ID, add ch_ prefix
                from_id = f"ch_{prereq}" if prereq in raw_challenge_ids else prereq
                edges.append({"from": from_id, "to": challenge_id})

    # Filter edges to only include valid node pairs
    valid_edges = [e for e in edges if e["from"] in node_ids and e["to"] in node_ids]

    # Get counts for summary
    concept_nodes = [n for n in nodes if n["type"] == "concept"]
    challenge_nodes = [n for n in nodes if n["type"] == "challenge"]

    mastered_count = len([n for n in nodes if n["state"] == "mastered"])
    learning_count = len([n for n in nodes if n["state"] == "learning"])
    available_count = len([n for n in nodes if n["state"] == "available"])
    locked_count = len([n for n in nodes if n["state"] == "locked"])

    return JSONResponse({
        "nodes": nodes,
        "edges": valid_edges,
        "summary": {
            "total": len(nodes),
            "concepts": len(concept_nodes),
            "challenges": len(challenge_nodes),
            "mastered": mastered_count,
            "learning": learning_count,
            "available": available_count,
            "locked": locked_count,
        },
        "levels": {
            level: len([n for n in nodes if n["level"] == level])
            for level in range(7)
        },
    })


@app.get("/api/concepts/{concept_id}")
async def get_concept(concept_id: str, player_id: str = Depends(get_current_player)):
    """Get detailed info about a specific concept and record access."""
    concept = concept_dag.get_concept(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept '{concept_id}' not found")

    # Record that this player accessed this concept
    db = get_database()
    db.record_lesson_access(player_id, concept_id, "concept")

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
# Concept Lessons - Duolingo-style Micro-lessons
# ============================================================================


@app.get("/api/lessons")
async def get_lessons(player_id: str = Depends(get_current_player)):
    """
    Get all concept lessons grouped by category.

    Returns a summary suitable for the lesson browser, with full spaced
    repetition progress data (same as challenges).
    """
    loader = get_lesson_loader()
    db = get_database()

    # Get player's completions (concepts use "concept:" prefix)
    all_completions = db.get_completions(player_id)
    concept_completions = {
        key.replace("concept:", ""): comp
        for key, comp in all_completions.items()
        if key.startswith("concept:")
    }

    categories = {}
    for category in loader.get_categories():
        lessons = loader.get_by_category(category)
        category_lessons = []

        for l in lessons:
            lesson_data = {
                "id": l.id,
                "name": l.name,
                "level": l.level,
                "time_to_read": l.time_to_read,
                "difficulty": l.difficulty,
                "bonus": l.bonus,
            }

            # Add progress data if lesson has been completed (same as challenges)
            if l.id in concept_completions:
                comp = concept_completions[l.id]
                progress = calculate_retention_score(
                    completion_count=comp.count,
                    last_completed=comp.last_completed,
                    best_time=comp.best_time,
                    expected_time=float(l.time_to_read),  # Use read time as expected
                )
                lesson_data["progress"] = progress
            else:
                lesson_data["progress"] = None

            category_lessons.append(lesson_data)

        categories[category] = category_lessons

    return JSONResponse({
        "categories": categories,
        "total_lessons": len(loader.get_all()),
    })


@app.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, player_id: str = Depends(get_current_player)):
    """
    Get a single concept lesson with full content.

    This is what the player reads to learn the concept.
    """
    loader = get_lesson_loader()
    lesson = loader.get(lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")

    # Build response
    response = {
        "id": lesson.id,
        "name": lesson.name,
        "level": lesson.level,
        "category": lesson.category,
        "description_brief": lesson.description_brief,
        "description_detailed": lesson.description_detailed,
        "lesson": lesson.lesson,  # Reference content (collapsible)
        "time_to_read": lesson.time_to_read,
        "difficulty": lesson.difficulty,
        "bonus": lesson.bonus,
        "connections": {
            "prerequisites": lesson.prerequisites,
            "enables": lesson.enables,
            "used_in": lesson.used_in,
            "see_also": lesson.see_also,
        },
        "status": "unseen",  # TODO: Load from DB
    }

    # Add try_it if present
    if lesson.try_it:
        response["try_it"] = {
            "prompt": lesson.try_it.prompt,
            "starter": lesson.try_it.starter,
            # Don't send solution until requested
        }

    return JSONResponse(response)


@app.get("/api/lessons/{lesson_id}/solution")
async def get_lesson_solution(lesson_id: str):
    """Get the solution for a lesson's try_it exercise."""
    loader = get_lesson_loader()
    lesson = loader.get(lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")

    if not lesson.try_it:
        raise HTTPException(status_code=404, detail="This lesson has no try_it exercise")

    return JSONResponse({
        "solution": lesson.try_it.solution,
    })


@app.post("/api/lessons/{lesson_id}/mark-seen")
async def mark_lesson_seen(lesson_id: str, player_id: str = Depends(get_current_player)):
    """Mark a lesson as seen (player opened it). Records access time for timer tracking."""
    loader = get_lesson_loader()
    lesson = loader.get(lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")

    # Record lesson access for timer tracking
    db = get_database()
    accessed_at = db.record_lesson_access(player_id, lesson_id, "concept")

    return JSONResponse({"success": True, "status": "seen", "accessed_at": accessed_at})


@app.post("/api/lessons/{lesson_id}/mark-understood")
async def mark_lesson_understood(lesson_id: str, player_id: str = Depends(get_current_player)):
    """Mark a lesson as understood (player clicked 'Got it!')."""
    loader = get_lesson_loader()
    lesson = loader.get(lesson_id)

    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")

    # TODO: Save to database
    # db = get_database()
    # db.mark_lesson_understood(player_id, lesson_id)

    return JSONResponse({"success": True, "status": "understood"})


@app.get("/api/lessons/for-challenge/{challenge_id}")
async def get_lessons_for_challenge(challenge_id: str, player_id: str = Depends(get_current_player)):
    """
    Get concept lessons relevant to a challenge.

    The Director uses this to suggest lessons when player is struggling.
    """
    loader = get_lesson_loader()
    lessons = loader.get_for_challenge(challenge_id)

    return JSONResponse({
        "challenge_id": challenge_id,
        "lessons": [
            {
                "id": l.id,
                "name": l.name,
                "level": l.level,
                "time_to_read": l.time_to_read,
                "status": "unseen",  # TODO: Load from DB
            }
            for l in lessons
        ],
    })


# ============================================================================
# The Director - Adaptive Learning AI
# ============================================================================


@app.get("/api/director/state")
async def get_director_state(player_id: str = Depends(get_current_player)):
    """
    Get The Director's current state for a player.

    Returns frustration level, momentum, active struggles, and whether
    intervention is recommended.
    """
    director = get_director(player_id, db=get_database())
    state = director.get_state()

    # Add detailed struggle info
    struggles = []
    for key, struggle in director._struggles.items():
        if not struggle.resolved:
            struggles.append({
                "type": struggle.type.value,
                "description": struggle.description,
                "frequency": struggle.frequency,
                "first_seen": struggle.first_seen.isoformat(),
                "last_seen": struggle.last_seen.isoformat(),
            })

    state["struggles"] = struggles
    return JSONResponse(state)


@app.get("/api/director/practice-challenge")
async def get_practice_challenge(concept: str):
    """
    Find a challenge to practice a specific concept.

    The Director tracks concepts by both concept ID and challenge ID.
    This endpoint finds the best challenge to practice a given concept.

    Returns the first available challenge that teaches the concept,
    or the concept itself if it's a challenge_id.
    """
    challenges = find_challenges_for_concept(concept)

    if challenges:
        # Return the first challenge found
        challenge_id = challenges[0]
        try:
            challenge = challenge_loader.load(challenge_id)
            return JSONResponse({
                "found": True,
                "challenge_id": challenge_id,
                "challenge_name": challenge.name,
                "all_challenges": challenges,
            })
        except FileNotFoundError:
            pass

    return JSONResponse({
        "found": False,
        "message": f"No challenges found for concept '{concept}'",
        "suggestion": "Try browsing all challenges",
    })


@app.get("/api/director/intervention")
async def get_director_intervention(player_id: str = Depends(get_current_player), force: bool = False):
    """
    Explicitly request a Director intervention.

    Args:
        player_id: Player identifier
        force: If True, return intervention even if threshold not met
    """
    director = get_director(player_id, db=get_database())

    # Check if intervention is warranted (or forced)
    if not force and not director.should_intervene():
        return JSONResponse({
            "intervention": None,
            "reason": "No intervention needed - player is doing well!",
            "state": director.get_state(),
        })

    intervention = director.get_intervention()

    if intervention:
        return JSONResponse({
            "intervention": {
                "type": intervention.type,
                "content": intervention.content,
                "reason": intervention.reason,
                "confidence": intervention.confidence,
                "generated_challenge": intervention.generated_challenge,
            },
            "state": director.get_state(),
        })
    else:
        return JSONResponse({
            "intervention": None,
            "reason": "Director has no specific intervention to offer",
            "state": director.get_state(),
        })


@app.post("/api/director/save-challenge")
async def save_director_challenge(request: Request):
    """
    Save a Director-generated challenge to the challenges directory.

    This allows dynamically created challenges to become permanent
    parts of the curriculum.
    """
    data = await request.json()
    challenge_data = data.get("challenge")
    player_id = data.get("player_id", "default")

    if not challenge_data:
        return JSONResponse({
            "success": False,
            "error": "challenge data is required",
        }, status_code=400)

    # Validate required fields
    required = ["name", "description", "skeleton_code"]
    for field in required:
        if field not in challenge_data:
            return JSONResponse({
                "success": False,
                "error": f"Missing required field: {field}",
            }, status_code=400)

    # Generate challenge ID from name
    import re
    challenge_id = re.sub(r'[^a-z0-9]+', '_', challenge_data["name"].lower()).strip('_')

    # Create TOML content for the challenge
    toml_content = f'''# Auto-generated by The Director for player: {player_id}
# Generated to address a specific learning gap

[challenge]
id = "{challenge_id}"
name = "{challenge_data['name']}"
level = {challenge_data.get('level', 1)}
points = {challenge_data.get('points', 10)}

description_brief = "{challenge_data['description'][:100]}"
description_detailed = """
{challenge_data['description']}
"""

skeleton_code = """
{challenge_data['skeleton_code']}
"""

hints = {challenge_data.get('hints', [])}
'''

    # Save to generated challenges directory
    generated_dir = CHALLENGES_DIR / "generated"
    generated_dir.mkdir(exist_ok=True)

    challenge_file = generated_dir / f"{challenge_id}.toml"
    challenge_file.write_text(toml_content)

    return JSONResponse({
        "success": True,
        "challenge_id": challenge_id,
        "file_path": str(challenge_file),
        "message": f"Challenge '{challenge_data['name']}' saved successfully",
    })


@app.post("/api/director/resolve-struggle")
async def resolve_director_struggle(request: Request):
    """
    Mark a struggle as resolved after the player overcomes it.

    Called when the player successfully completes a challenge that
    was related to their struggle.
    """
    data = await request.json()
    player_id = data.get("player_id", "default")
    struggle_key = data.get("struggle_key")

    if not struggle_key:
        return JSONResponse({
            "success": False,
            "error": "struggle_key is required",
        }, status_code=400)

    director = get_director(player_id, db=get_database())
    director.mark_struggle_resolved(struggle_key)

    return JSONResponse({
        "success": True,
        "message": f"Struggle '{struggle_key}' marked as resolved",
        "state": director.get_state(),
    })


# ============================================================================
# Player Profiles API
# ============================================================================


@app.get("/api/players")
async def list_players():
    """List all player profiles for the profile picker."""
    db = get_database()
    players = db.list_players()
    return JSONResponse({"players": players})


@app.post("/api/players")
async def create_player(request: Request):
    """Create a new player profile."""
    data = await request.json()
    player_id = data.get("player_id", "").strip().lower()
    display_name = data.get("display_name", "").strip()

    if not player_id:
        return JSONResponse({
            "success": False,
            "error": "Player ID is required",
        }, status_code=400)

    # Validate player_id format (alphanumeric + underscore, 2-20 chars)
    import re
    if not re.match(r'^[a-z0-9_]{2,20}$', player_id):
        return JSONResponse({
            "success": False,
            "error": "Player ID must be 2-20 characters, lowercase letters, numbers, and underscores only",
        }, status_code=400)

    db = get_database()
    invite_code = data.get("invite_code", "").strip()

    # Check registration mode
    registration_mode = db.get_registration_mode()
    if registration_mode == "closed":
        return JSONResponse({
            "success": False,
            "error": "Registration is currently closed",
        }, status_code=403)
    elif registration_mode == "invite_only":
        # Require valid invite code
        if not invite_code:
            return JSONResponse({
                "success": False,
                "error": "Registration requires an invite code",
            }, status_code=403)
        valid, error_msg = db.validate_invite_code(invite_code)
        if not valid:
            return JSONResponse({
                "success": False,
                "error": error_msg,
            }, status_code=403)

    # Check if player already exists
    existing_players = db.list_players()
    if any(p["player_id"] == player_id for p in existing_players):
        return JSONResponse({
            "success": False,
            "error": f"Player '{player_id}' already exists",
        }, status_code=409)

    # Create the player
    player = db.get_or_create_player(player_id)

    # Set display name if provided
    if display_name:
        db.set_display_name(player_id, display_name)

    # Mark invite code as used (if provided)
    if invite_code:
        db.use_invite_code(invite_code, player_id)

    return JSONResponse({
        "success": True,
        "player": {
            "player_id": player_id,
            "display_name": display_name or None,
            "total_xp": 0,
        }
    })


@app.post("/api/players/migrate")
async def migrate_player(request: Request):
    """Migrate all data from one player to another.

    Used for "Import existing" feature - migrate default profile to a named profile.
    """
    data = await request.json()
    from_player_id = data.get("from_player_id", "").strip()
    to_player_id = data.get("to_player_id", "").strip().lower()
    display_name = data.get("display_name", "").strip()
    delete_source = data.get("delete_source", True)

    if not from_player_id:
        return JSONResponse({
            "success": False,
            "error": "Source player ID is required",
        }, status_code=400)

    if not to_player_id:
        return JSONResponse({
            "success": False,
            "error": "Destination player ID is required",
        }, status_code=400)

    # Validate to_player_id format
    import re
    if not re.match(r'^[a-z0-9_]{2,20}$', to_player_id):
        return JSONResponse({
            "success": False,
            "error": "Player ID must be 2-20 characters, lowercase letters, numbers, and underscores only",
        }, status_code=400)

    db = get_database()

    # Check if destination already exists
    existing_players = db.list_players()
    if any(p["player_id"] == to_player_id for p in existing_players):
        return JSONResponse({
            "success": False,
            "error": f"Player '{to_player_id}' already exists",
        }, status_code=409)

    try:
        stats = db.migrate_player_data(
            from_player_id=from_player_id,
            to_player_id=to_player_id,
            delete_source=delete_source
        )

        # Set display name if provided
        if display_name:
            db.set_display_name(to_player_id, display_name)

        # Get the migrated player's info
        players = db.list_players()
        new_player = next((p for p in players if p["player_id"] == to_player_id), None)

        return JSONResponse({
            "success": True,
            "player": new_player,
            "migration_stats": stats,
        })
    except ValueError as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=404)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Migration failed: {str(e)}",
        }, status_code=500)


# ============================================================================
# Security & Authentication API
# ============================================================================


@app.post("/api/auth/identify-by-combo")
async def identify_by_combo(request: Request):
    """Identify which player(s) match a gamepad combo.

    Used for quick-login from profile picker - enter combo, get logged in.
    Returns matching player_ids (usually 0 or 1, but could be multiple on conflict).
    """
    data = await request.json()
    combo = data.get("combo", [])

    if not combo or not isinstance(combo, list):
        return JSONResponse({
            "success": False,
            "error": "Combo sequence required",
        }, status_code=400)

    db = get_database()
    matching_players = db.identify_players_by_combo(combo)

    return JSONResponse({
        "success": True,
        "matching_players": matching_players,
        "count": len(matching_players),
    })


@app.get("/api/auth/status")
async def get_auth_status(player_id: str = Depends(get_current_player)):
    """Check if player has security enabled and what methods are available."""
    db = get_database()
    player = db.get_or_create_player(player_id)
    has_passkey = db.has_passkey(player_id)

    return JSONResponse({
        "player_id": player_id,
        "has_password": db.has_password(player_id),
        "has_gamepad_combo": bool(player.gamepad_combo),
        "has_passkey": has_passkey,
        "needs_auth": db.has_password(player_id) or bool(player.gamepad_combo) or has_passkey,
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

    # If passkey is set, password login is not allowed
    # (use passkey or gamepad combo instead)
    if db.has_passkey(player_id):
        player = db.get_or_create_player(player_id)
        has_gamepad = bool(player.gamepad_combo)
        return JSONResponse({
            "success": False,
            "error": "Passkey required for this account",
            "passkey_required": True,
            "gamepad_available": has_gamepad,
        }, status_code=401)

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
async def get_gamepad_combo(player_id: str = Depends(get_current_player)):
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
# Privacy Settings API
# ============================================================================


@app.get("/api/player/privacy")
async def get_privacy_settings(player_id: str = Depends(get_current_player)):
    """Get player's privacy settings."""
    db = get_database()
    settings = db.get_privacy_settings(player_id)

    return JSONResponse(settings)


@app.post("/api/player/privacy")
async def set_privacy_settings(request: Request, player_id: str = Depends(get_current_player)):
    """Update player's privacy settings."""
    data = await request.json()
    db = get_database()

    hide_from_leaderboards = data.get("hide_from_leaderboards", False)
    hide_from_picker = data.get("hide_from_picker", False)

    db.set_privacy_settings(player_id, hide_from_leaderboards, hide_from_picker)

    return JSONResponse({
        "success": True,
        "hide_from_leaderboards": hide_from_leaderboards,
        "hide_from_picker": hide_from_picker,
    })


# ============================================================================
# Passkey / WebAuthn API
# ============================================================================


@app.get("/api/auth/passkeys")
async def list_passkeys(player_id: str = Depends(get_current_player)):
    """List player's registered passkeys."""
    db = get_database()
    passkeys = db.get_passkeys(player_id)

    # Return minimal info (don't expose public keys)
    return JSONResponse({
        "passkeys": [
            {
                "id": pk["credential_id"],
                "name": pk["name"],
                "created_at": pk["created_at"],
            }
            for pk in passkeys
        ]
    })


@app.post("/api/auth/passkey/register/begin")
async def passkey_register_begin(request: Request, player_id: str = Depends(get_current_player)):
    """Begin passkey registration - returns WebAuthn options."""
    import base64
    from webauthn import generate_registration_options
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        ResidentKeyRequirement,
        UserVerificationRequirement,
    )
    from webauthn.helpers import bytes_to_base64url

    data = await request.json()
    passkey_name = data.get("name", "My Passkey")

    # Get hostname for RP ID
    host = request.headers.get("host", "localhost")
    rp_id = host.split(":")[0]  # Remove port

    db = get_database()
    player = db.get_or_create_player(player_id)

    # Get existing credentials to exclude (prevent re-registration)
    existing_passkeys = db.get_passkeys(player_id)
    exclude_credentials = []
    for pk in existing_passkeys:
        try:
            cred_id_bytes = base64.urlsafe_b64decode(pk["credential_id"] + "==")
            exclude_credentials.append({"id": cred_id_bytes, "type": "public-key"})
        except Exception:
            pass

    # Generate registration options using webauthn library
    user_id = player_id.encode()  # Use player_id bytes as user handle
    options = generate_registration_options(
        rp_id=rp_id,
        rp_name="Learn Me Some Py",
        user_id=user_id,
        user_name=player_id,
        user_display_name=player.display_name or player_id,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        timeout=60000,
    )

    # Store challenge for verification (in-memory for now)
    request.app.state.passkey_challenges = getattr(request.app.state, "passkey_challenges", {})
    request.app.state.passkey_challenges[player_id] = {
        "challenge": options.challenge,  # bytes
        "name": passkey_name,
        "rp_id": rp_id,
        "user_id": user_id,
    }

    # Convert options to JSON-serializable format
    return JSONResponse({
        "challenge": bytes_to_base64url(options.challenge),
        "rp": {
            "name": options.rp.name,
            "id": options.rp.id,
        },
        "user": {
            "id": bytes_to_base64url(options.user.id),
            "name": options.user.name,
            "displayName": options.user.display_name,
        },
        "pubKeyCredParams": [
            {"type": "public-key", "alg": param.alg} for param in options.pub_key_cred_params
        ],
        "timeout": options.timeout,
        "authenticatorSelection": {
            "residentKey": options.authenticator_selection.resident_key.value if options.authenticator_selection else "required",
            "requireResidentKey": True,
            "userVerification": options.authenticator_selection.user_verification.value if options.authenticator_selection else "preferred",
        },
    })


@app.post("/api/auth/passkey/register/complete")
async def passkey_register_complete(request: Request, player_id: str = Depends(get_current_player)):
    """Complete passkey registration - verify attestation and store credential."""
    from webauthn import verify_registration_response
    from webauthn.helpers.structs import RegistrationCredential, AuthenticatorAttestationResponse
    from webauthn.helpers import base64url_to_bytes, bytes_to_base64url

    data = await request.json()

    # Get stored challenge
    challenges = getattr(request.app.state, "passkey_challenges", {})
    stored = challenges.get(player_id)

    if not stored:
        raise HTTPException(status_code=400, detail="No pending registration")

    passkey_name = stored.get("name", "My Passkey")
    expected_challenge = stored["challenge"]
    rp_id = stored["rp_id"]
    user_id = stored["user_id"]

    # Get origin from request
    origin = request.headers.get("origin", f"https://{rp_id}")

    try:
        # Build the credential object from browser response
        credential = RegistrationCredential(
            id=data.get("id"),
            raw_id=base64url_to_bytes(data.get("rawId", data.get("id"))),
            response=AuthenticatorAttestationResponse(
                client_data_json=base64url_to_bytes(data["response"]["clientDataJSON"]),
                attestation_object=base64url_to_bytes(data["response"]["attestationObject"]),
            ),
            type=data.get("type", "public-key"),
        )

        # Verify the registration response - this does REAL cryptographic verification
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=rp_id,
            expected_origin=origin,
            require_user_verification=False,  # Preferred, not required
        )

        # Store the verified credential
        db = get_database()
        credential_id = bytes_to_base64url(verification.credential_id)
        public_key = bytes_to_base64url(verification.credential_public_key)
        user_handle = bytes_to_base64url(user_id)

        db.add_passkey(
            player_id=player_id,
            credential_id=credential_id,
            public_key=public_key,  # Now storing the actual verified public key
            name=passkey_name,
            user_handle=user_handle,
            sign_count=verification.sign_count,
        )

        # Clean up challenge
        del challenges[player_id]

        return JSONResponse({
            "success": True,
            "message": "Passkey registered successfully",
        })

    except Exception as e:
        # Clean up challenge on failure too
        if player_id in challenges:
            del challenges[player_id]
        raise HTTPException(status_code=400, detail=f"Registration verification failed: {str(e)}")


@app.delete("/api/auth/passkey/{credential_id}")
async def remove_passkey(credential_id: str, player_id: str = Depends(get_current_player)):
    """Remove a passkey."""
    db = get_database()

    if db.remove_passkey(player_id, credential_id):
        return JSONResponse({"success": True})
    else:
        raise HTTPException(status_code=404, detail="Passkey not found")


@app.post("/api/auth/passkey/authenticate/begin")
async def passkey_auth_begin(request: Request):
    """Begin passkey authentication - returns WebAuthn options."""
    from webauthn import generate_authentication_options
    from webauthn.helpers.structs import UserVerificationRequirement
    from webauthn.helpers import bytes_to_base64url

    # Get hostname for RP ID
    host = request.headers.get("host", "localhost")
    rp_id = host.split(":")[0]

    # Generate authentication options - no allowCredentials = discoverable credential flow
    options = generate_authentication_options(
        rp_id=rp_id,
        timeout=60000,
        user_verification=UserVerificationRequirement.PREFERRED,
        # No allow_credentials = discoverable credential (passkey) flow
    )

    # Store challenge for verification (keyed by challenge bytes for lookup)
    request.app.state.passkey_auth_challenges = getattr(request.app.state, "passkey_auth_challenges", {})
    challenge_b64 = bytes_to_base64url(options.challenge)
    request.app.state.passkey_auth_challenges[challenge_b64] = {
        "challenge": options.challenge,
        "rp_id": rp_id,
    }

    return JSONResponse({
        "challenge": challenge_b64,
        "rpId": rp_id,
        "timeout": options.timeout,
        "userVerification": options.user_verification.value if options.user_verification else "preferred",
    })


@app.post("/api/auth/passkey/authenticate/complete")
async def passkey_auth_complete(request: Request):
    """Complete passkey authentication - verify assertion and create session."""
    from webauthn import verify_authentication_response
    from webauthn.helpers.structs import AuthenticationCredential, AuthenticatorAssertionResponse
    from webauthn.helpers import base64url_to_bytes, bytes_to_base64url

    data = await request.json()
    response_data = data.get("response", {})

    # Get the challenge from the request to look up stored data
    # The challenge is in clientDataJSON but we need to find the stored challenge
    credential_id_b64 = data.get("rawId", data.get("id"))

    # For discoverable credentials, the authenticator returns the userHandle
    user_handle_b64 = response_data.get("userHandle")

    db = get_database()
    player_id = None
    passkey_data = None

    # Try to identify player by userHandle first (discoverable credential flow)
    if user_handle_b64:
        player_id = db.get_player_by_user_handle(user_handle_b64)
        if player_id:
            result = db.get_passkey_by_credential_id(credential_id_b64)
            if result and result[0] == player_id:
                passkey_data = result[1]

    # Fall back to credential_id lookup if userHandle not found
    if not player_id:
        result = db.get_passkey_by_credential_id(credential_id_b64)
        if result:
            player_id, passkey_data = result

    if not player_id or not passkey_data:
        raise HTTPException(status_code=401, detail="Unknown passkey")

    # Get stored challenge - we need to find it by iterating
    # (In production, you'd key this better or use a session store)
    auth_challenges = getattr(request.app.state, "passkey_auth_challenges", {})
    challenge_b64 = data.get("challenge")  # Frontend should pass this back

    # Find the matching challenge (look for recent ones)
    stored_challenge = None
    stored_rp_id = None
    for chal_key, chal_data in list(auth_challenges.items()):
        # Use the first valid challenge (in production, tie to session)
        stored_challenge = chal_data["challenge"]
        stored_rp_id = chal_data["rp_id"]
        # Clean up after use
        del auth_challenges[chal_key]
        break

    if not stored_challenge:
        raise HTTPException(status_code=400, detail="No pending authentication challenge")

    # Get origin from request
    origin = request.headers.get("origin", f"https://{stored_rp_id}")

    try:
        # Build the credential object from browser response
        credential = AuthenticationCredential(
            id=data.get("id"),
            raw_id=base64url_to_bytes(credential_id_b64),
            response=AuthenticatorAssertionResponse(
                client_data_json=base64url_to_bytes(response_data["clientDataJSON"]),
                authenticator_data=base64url_to_bytes(response_data["authenticatorData"]),
                signature=base64url_to_bytes(response_data["signature"]),
                user_handle=base64url_to_bytes(user_handle_b64) if user_handle_b64 else None,
            ),
            type=data.get("type", "public-key"),
        )

        # Get the stored public key and sign count
        stored_public_key = base64url_to_bytes(passkey_data["public_key"])
        stored_sign_count = passkey_data.get("sign_count", 0)

        # Verify the authentication response - REAL cryptographic verification!
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=stored_challenge,
            expected_rp_id=stored_rp_id,
            expected_origin=origin,
            credential_public_key=stored_public_key,
            credential_current_sign_count=stored_sign_count,
            require_user_verification=False,
        )

        # Update sign count for replay protection
        db.update_passkey_sign_count(player_id, credential_id_b64, verification.new_sign_count)

        # Create session
        session_id = db.create_session(player_id, auth_method="passkey")

        return JSONResponse({
            "success": True,
            "player_id": player_id,
            "session_id": session_id,
        })

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication verification failed: {str(e)}")


# ============================================================================
# Admin API Endpoints
# ============================================================================


def require_admin(player_id: str = Depends(get_current_player)) -> str:
    """Dependency that requires the current user to be an admin."""
    db = get_database()
    if not db.is_admin(player_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    return player_id


@app.get("/api/admin/users")
async def admin_list_users(admin_id: str = Depends(require_admin)):
    """List all users with their stats (admin only)."""
    db = get_database()
    players = db.list_players(include_hidden=True)  # Admins see all users

    # Enrich with stats for each player
    users = []
    for player in players:
        player_id = player["player_id"]
        completions = db.get_completions(player_id)
        xp = db.get_player_xp(player_id)

        users.append({
            "player_id": player_id,
            "display_name": player.get("display_name"),
            "created_at": player.get("created_at"),
            "is_admin": db.is_admin(player_id),
            "has_password": player.get("has_password", False),
            "has_gamepad_combo": player.get("has_gamepad_combo", False),
            "has_passkey": player.get("has_passkey", False),
            "hide_from_picker": player.get("hide_from_picker", False),
            "total_xp": xp,
            "challenges_completed": len(completions),
            "invited_by_code": player.get("invited_by_code"),
        })

    return JSONResponse({"users": users})


@app.get("/api/admin/users/{player_id}")
async def admin_get_user(player_id: str, admin_id: str = Depends(require_admin)):
    """Get detailed info for a specific user (admin only)."""
    db = get_database()
    players = db.list_players(include_hidden=True)

    # Find the player
    player = next((p for p in players if p["player_id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")

    completions = db.get_completions(player_id)
    xp = db.get_player_xp(player_id)

    return JSONResponse({
        "player_id": player_id,
        "display_name": player.get("display_name"),
        "created_at": player.get("created_at"),
        "is_admin": db.is_admin(player_id),
        "has_password": player.get("has_password", False),
        "has_gamepad_combo": player.get("has_gamepad_combo", False),
        "has_passkey": player.get("has_passkey", False),
        "total_xp": xp,
        "challenges_completed": len(completions),
        "invited_by_code": player.get("invited_by_code"),
    })


@app.put("/api/admin/users/{player_id}")
async def admin_update_user(player_id: str, request: Request, admin_id: str = Depends(require_admin)):
    """Update a user's properties (admin only)."""
    data = await request.json()
    db = get_database()

    # Check player exists
    players = db.list_players()
    player = next((p for p in players if p["player_id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")

    # Update display name if provided
    if "display_name" in data:
        db.set_display_name(player_id, data["display_name"])

    # Update admin status if provided
    if "is_admin" in data:
        # Prevent removing your own admin status
        if player_id == admin_id and not data["is_admin"]:
            raise HTTPException(status_code=400, detail="Cannot remove your own admin status")
        db.set_admin(player_id, data["is_admin"])

    return JSONResponse({
        "success": True,
        "message": f"User '{player_id}' updated",
    })


@app.delete("/api/admin/users/{player_id}")
async def admin_delete_user(player_id: str, admin_id: str = Depends(require_admin)):
    """Delete a user and all their data (admin only)."""
    db = get_database()

    # Prevent self-deletion
    if player_id == admin_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # Check player exists
    players = db.list_players()
    player = next((p for p in players if p["player_id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")

    result = db.delete_player(player_id)

    return JSONResponse({
        "success": result["success"],
        "message": f"Deleted player '{player_id}' and {result['deleted_completions']} completions, {result['deleted_xp_events']} XP events",
        "deleted": result,
    })


@app.get("/api/admin/stats")
async def admin_get_stats(admin_id: str = Depends(require_admin)):
    """Get node-wide statistics (admin only)."""
    db = get_database()
    stats = db.get_node_stats()
    return JSONResponse(stats)


@app.get("/api/admin/settings")
async def admin_get_settings(admin_id: str = Depends(require_admin)):
    """Get node settings (admin only)."""
    db = get_database()
    return JSONResponse({
        "registration_mode": db.get_registration_mode(),
    })


@app.put("/api/admin/settings")
async def admin_update_settings(request: Request, admin_id: str = Depends(require_admin)):
    """Update node settings (admin only)."""
    data = await request.json()
    db = get_database()

    if "registration_mode" in data:
        mode = data["registration_mode"]
        if mode not in ("open", "invite_only", "closed"):
            raise HTTPException(status_code=400, detail="Invalid registration mode. Must be 'open', 'invite_only', or 'closed'")
        db.set_registration_mode(mode)

    return JSONResponse({
        "success": True,
        "message": "Settings updated",
    })


@app.get("/api/admin/invites")
async def admin_list_invites(admin_id: str = Depends(require_admin), include_inactive: bool = False):
    """List all invite codes (admin only)."""
    db = get_database()
    invites = db.list_invite_codes(include_inactive=include_inactive)
    return JSONResponse({"invites": invites})


@app.post("/api/admin/invites")
async def admin_create_invite(request: Request, admin_id: str = Depends(require_admin)):
    """Create a new invite code (admin only)."""
    data = await request.json()
    db = get_database()

    max_uses = data.get("max_uses", 1)
    expires_in_days = data.get("expires_in_days")
    note = data.get("note")

    code = db.create_invite_code(
        created_by=admin_id,
        max_uses=max_uses,
        expires_days=expires_in_days,
        note=note,
    )

    return JSONResponse({
        "success": True,
        "code": code,
        "message": f"Invite code created: {code}",
    })


@app.delete("/api/admin/invites/{code}")
async def admin_deactivate_invite(code: str, admin_id: str = Depends(require_admin)):
    """Deactivate an invite code (admin only)."""
    db = get_database()

    success = db.deactivate_invite_code(code)
    if not success:
        raise HTTPException(status_code=404, detail=f"Invite code '{code}' not found")

    return JSONResponse({
        "success": True,
        "message": f"Invite code '{code}' deactivated",
    })


@app.post("/api/admin/invites/{code}/add-uses")
async def admin_add_invite_uses(code: str, request: Request, admin_id: str = Depends(require_admin)):
    """Add more uses to an invite code (admin only)."""
    data = await request.json()
    additional_uses = data.get("uses", 1)

    if additional_uses < 1:
        raise HTTPException(status_code=400, detail="Must add at least 1 use")

    db = get_database()
    success = db.add_invite_uses(code, additional_uses)

    if not success:
        raise HTTPException(status_code=404, detail=f"Invite code '{code}' not found")

    return JSONResponse({
        "success": True,
        "message": f"Added {additional_uses} use(s) to invite code '{code}'",
    })


# Public endpoint for checking registration mode (needed before login)
@app.get("/api/registration-mode")
async def get_registration_mode():
    """Get registration mode (public - needed for signup flow)."""
    db = get_database()
    return JSONResponse({
        "mode": db.get_registration_mode(),
    })


@app.post("/api/validate-invite")
async def validate_invite_code(request: Request):
    """Validate an invite code (public - needed for signup flow)."""
    data = await request.json()
    code = data.get("code")

    if not code:
        return JSONResponse({
            "valid": False,
            "message": "No invite code provided",
        }, status_code=400)

    db = get_database()
    valid, message = db.validate_invite_code(code)

    return JSONResponse({
        "valid": valid,
        "message": message,
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
