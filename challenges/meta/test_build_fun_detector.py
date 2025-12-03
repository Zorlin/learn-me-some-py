"""
Tests for Meta: Build the Fun Detector challenge.

The learner builds the engagement tracker that learns player preferences.
"""

import subprocess
import sys
import json


def run_player_code(code: str, samples: list) -> dict:
    """Run player code and return fun profile."""
    full_code = f'''
{code}

import json
samples_raw = {repr(samples)}
samples = [
    EmotionalSample(
        fun_type=FunType(s["fun_type"]),
        enjoyment=s["enjoyment"],
        duration_seconds=s["duration"]
    )
    for s in samples_raw
]

profile = analyze_fun_patterns(samples)
recommended = recommend_challenge_type(profile)

result = {{
    "scores": {{k.value: v for k, v in profile.scores.items()}},
    "recommended": recommended.value
}}
print(json.dumps(result))
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


def test_has_analyze_function(player_code):
    """Check that code defines analyze_fun_patterns function."""
    assert "def analyze_fun_patterns" in player_code, "Define 'analyze_fun_patterns' function"


def test_detect_puzzle_lover(player_code):
    """High enjoyment + long duration on puzzle should identify puzzle lover."""
    samples = [
        {"fun_type": "puzzle", "enjoyment": 0.9, "duration": 300},
        {"fun_type": "speedrun", "enjoyment": 0.3, "duration": 60}
    ]
    result = run_player_code(player_code, samples)
    assert result["recommended"] == "puzzle", "Should recommend puzzle type"


def test_detect_speedrunner(player_code):
    """Multiple high-enjoyment speedrun sessions should identify speedrunner."""
    samples = [
        {"fun_type": "speedrun", "enjoyment": 0.95, "duration": 180},
        {"fun_type": "speedrun", "enjoyment": 0.9, "duration": 120},
        {"fun_type": "puzzle", "enjoyment": 0.5, "duration": 100}
    ]
    result = run_player_code(player_code, samples)
    assert result["recommended"] == "speedrun", "Should recommend speedrun type"
