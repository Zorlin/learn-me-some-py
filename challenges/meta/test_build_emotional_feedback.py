"""
Tests for Meta: Build Emotional Input challenge.

The learner builds the analog emotional feedback system.
"""

import subprocess
import sys
import json


def run_player_code(code: str, inputs: list) -> dict:
    """Run player code and return emotional response."""
    full_code = f'''
{code}

import json
inputs = {repr(inputs)}
results = []

for inp in inputs:
    prompt = EmotionalPrompt("How are you feeling?")
    prompt.update(
        rt=inp.get("rt", 0.0),
        lt=inp.get("lt", 0.0),
        y_pressed=inp.get("y_pressed", False),
        a_pressed=inp.get("a_pressed", False)
    )
    response = prompt.get_response()
    results.append({{
        "dimension": response.dimension.value,
        "value": response.value,
        "is_complex": response.is_complex
    }})

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


def test_has_emotional_prompt_class(player_code):
    """Check that code defines an EmotionalPrompt class."""
    assert "class EmotionalPrompt" in player_code, "Define an 'EmotionalPrompt' class"


def test_rt_enjoyment(player_code):
    """High RT should indicate enjoyment."""
    results = run_player_code(player_code, [{"rt": 0.8, "lt": 0.2, "a_pressed": True}])
    assert results[0]["dimension"] == "enjoyment", "High RT should be enjoyment"
    assert abs(results[0]["value"] - 0.8) < 0.1, "Value should be ~0.8"


def test_lt_frustration(player_code):
    """High LT should indicate frustration."""
    results = run_player_code(player_code, [{"rt": 0.3, "lt": 0.7, "a_pressed": True}])
    assert results[0]["dimension"] == "frustration", "High LT should be frustration"
    assert abs(results[0]["value"] - 0.7) < 0.1, "Value should be ~0.7"


def test_complex_response(player_code):
    """Y button should trigger complex response."""
    results = run_player_code(player_code, [{"rt": 0.5, "lt": 0.5, "y_pressed": True}])
    assert results[0]["is_complex"] == True, "Y button should mark response as complex"
