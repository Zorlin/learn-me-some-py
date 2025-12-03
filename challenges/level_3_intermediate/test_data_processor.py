"""
Tests for Data Processing Pipeline.
"""

import subprocess
import sys
import json


def run_player_code(code: str, input_data) -> str:
    """Run player code with given input and return output."""
    full_code = f'''
{code}

import json
input_data = {repr(input_data)}
result = solution(input_data)
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


def test_has_solution_function(player_code):
    """Check that code defines a solution function."""
    assert "def solution" in player_code, "Define a 'solution' function"


def test_basic_pipeline(player_code):
    """Test basic pipeline with clean data."""
    commands = ["DATA 1,2,3", "PIPELINE clean,filter,square,sum"]
    result = run_player_code(player_code, commands)
    assert result == ["Data loaded: 3 items", "14"], f"Expected ['Data loaded: 3 items', '14'], got {result}"


def test_with_empty_values(player_code):
    """Test pipeline with empty values in data."""
    commands = ["DATA 1,2,,3,", "PIPELINE clean,filter,square,sum"]
    result = run_player_code(player_code, commands)
    assert result == ["Data loaded: 5 items", "14"], f"Expected ['Data loaded: 5 items', '14'], got {result}"


def test_with_invalid_numbers(player_code):
    """Test pipeline with invalid numbers."""
    commands = ["DATA 1,2,abc,3,xyz", "PIPELINE clean,filter,square,sum"]
    result = run_player_code(player_code, commands)
    assert result == ["Data loaded: 5 items", "14"], f"Expected ['Data loaded: 5 items', '14'], got {result}"


def test_filter_only(player_code):
    """Test pipeline with filter operation only."""
    commands = ["DATA 1,abc,2,def,3", "PIPELINE clean,filter"]
    result = run_player_code(player_code, commands)
    assert result == ["Data loaded: 5 items", "[1, 2, 3]"], f"Expected ['Data loaded: 5 items', '[1, 2, 3]'], got {result}"


def test_partial_pipeline(player_code):
    """Test partial pipeline without sum."""
    commands = ["DATA 2,3,4", "PIPELINE clean,filter,square"]
    result = run_player_code(player_code, commands)
    assert result == ["Data loaded: 3 items", "[4, 9, 16]"], f"Expected ['Data loaded: 3 items', '[4, 9, 16]'], got {result}"


def test_complex_data(player_code):
    """Test pipeline with complex mixed data."""
    commands = ["DATA 5,,,10,,15,abc,20,def", "PIPELINE clean,filter,square,sum"]
    result = run_player_code(player_code, commands)
    assert result == ["Data loaded: 9 items", "750"], f"Expected ['Data loaded: 9 items', '750'], got {result}"
