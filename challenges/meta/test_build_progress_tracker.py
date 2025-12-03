"""
Tests for Meta: Build Progress Tracking challenge.

The learner builds the XP and mastery system.
"""

import subprocess
import sys
import json
import tempfile


def run_player_code(code: str, actions: list) -> dict:
    """Run player code with given actions."""
    full_code = f'''
{code}

import json
actions = {repr(actions)}
progress = PlayerProgress(player_id="test_player")
results = {{}}

for action in actions:
    if action["type"] == "earn_xp":
        progress.earn_xp(action["amount"])
        results["total_xp"] = progress.total_xp
    elif action["type"] == "complete_challenge":
        progress.complete_challenge(action["challenge_id"], action["concept"], action["xp"])
        results["total_xp"] = progress.total_xp
        results["mastery"] = progress.get_mastery(action["concept"])
    elif action["type"] == "get_mastery":
        results["mastery"] = progress.get_mastery(action["concept"])

print(json.dumps(results))
'''
    result = subprocess.run(
        [sys.executable, "-c", full_code],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode != 0:
        raise RuntimeError(f"Code failed: {result.stderr}")
    return json.loads(result.stdout.strip())


def test_has_player_progress_class(player_code):
    """Check that code defines PlayerProgress class."""
    assert "class PlayerProgress" in player_code, "Define 'PlayerProgress' class"


def test_earn_xp(player_code):
    """Test earning XP."""
    actions = [{"type": "earn_xp", "amount": 100}]
    result = run_player_code(player_code, actions)
    assert result["total_xp"] == 100, "Should have 100 XP"


def test_complete_challenge_increases_mastery(player_code):
    """Completing a challenge should increase mastery."""
    actions = [
        {"type": "complete_challenge", "challenge_id": "lists_basics", "concept": "lists", "xp": 50}
    ]
    result = run_player_code(player_code, actions)
    assert result["mastery"] >= 1, "Mastery should increase after completing challenge"
    assert result["total_xp"] == 50, "Should earn XP from challenge"


def test_mastery_caps_at_4(player_code):
    """Mastery should not exceed 4."""
    actions = [
        {"type": "complete_challenge", "challenge_id": f"c{i}", "concept": "concept1", "xp": 100}
        for i in range(6)
    ]
    result = run_player_code(player_code, actions)
    assert result["mastery"] == 4, "Mastery should cap at 4"
