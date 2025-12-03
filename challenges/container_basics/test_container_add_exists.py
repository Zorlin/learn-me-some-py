"""
Tests for Container Add and Exists challenge.

The learner builds a container with ADD and EXISTS operations.
"""

import subprocess
import sys
import json


def run_player_code(code: str, input_data: list) -> list:
    """Run player code with given input and return output."""
    full_code = f'''
{code}

import json
queries = {repr(input_data)}
result = solution(queries)
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


def test_basic_add_and_exists(player_code):
    """Test basic ADD and EXISTS operations."""
    queries = [["ADD", "1"], ["ADD", "2"], ["EXISTS", "1"], ["EXISTS", "3"]]
    expected = ["", "", "true", "false"]
    result = run_player_code(player_code, queries)
    assert result == expected, f"Expected {expected}, got {result}"


def test_duplicates(player_code):
    """Test adding duplicate values."""
    queries = [["ADD", "5"], ["ADD", "5"], ["EXISTS", "5"]]
    expected = ["", "", "true"]
    result = run_player_code(player_code, queries)
    assert result == expected, f"Expected {expected}, got {result}"


def test_empty_check(player_code):
    """Test EXISTS on empty container."""
    queries = [["EXISTS", "1"]]
    expected = ["false"]
    result = run_player_code(player_code, queries)
    assert result == expected, f"Expected {expected}, got {result}"
