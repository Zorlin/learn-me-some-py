"""
Tests for Meta: Build Gamepad Support challenge.

The learner builds the gamepad input mapping system.
"""

import subprocess
import sys
import json


def run_player_code(code: str, inputs: list) -> list:
    """Run player code and return actions."""
    full_code = f'''
{code}

import json
inputs = {repr(inputs)}
results = []

for inp in inputs:
    state = ControllerState(
        buttons_pressed=set([Button[inp.get("button")]] if "button" in inp else []),
        left_trigger=inp.get("left_trigger", 0.0),
        right_trigger=inp.get("right_trigger", 0.0),
        left_stick_x=0.0,
        left_stick_y=0.0,
        right_stick_x=0.0,
        right_stick_y=0.0
    )
    mapper = ControllerMapping()
    actions = mapper.handle_input(state)
    results.append(actions)

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


def test_has_controller_mapping_class(player_code):
    """Check that code defines a ControllerMapping class."""
    assert "class ControllerMapping" in player_code, "Define a 'ControllerMapping' class"


def test_button_a_inserts_def(player_code):
    """Button A should insert 'def '."""
    results = run_player_code(player_code, [{"button": "A"}])
    assert "insert:def " in results[0], "Button A should produce 'insert:def '"


def test_rt_trigger_indents(player_code):
    """Right trigger > 0.5 should indent."""
    results = run_player_code(player_code, [{"right_trigger": 0.8}])
    assert "indent" in results[0], "Right trigger > 0.5 should indent"


def test_lt_trigger_dedents(player_code):
    """Left trigger > 0.5 should dedent."""
    results = run_player_code(player_code, [{"left_trigger": 0.7}])
    assert "dedent" in results[0], "Left trigger > 0.5 should dedent"


def test_lb_undoes(player_code):
    """LB button should undo."""
    results = run_player_code(player_code, [{"button": "LB"}])
    assert "undo" in results[0], "LB button should produce 'undo'"
