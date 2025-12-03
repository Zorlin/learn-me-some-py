"""
Tests for Safe Calculator with Error Handling.
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


def test_basic_math(player_code):
    """Test basic math operations."""
    commands = ["ADD 5 3", "ADD 10 20", "DIVIDE 10 2"]
    result = run_player_code(player_code, commands)
    assert result == ["8", "30", "5.0"], f"Expected ['8', '30', '5.0'], got {result}"


def test_division_by_zero(player_code):
    """Test division by zero error handling."""
    commands = ["DIVIDE 10 0", "DIVIDE 5 0"]
    result = run_player_code(player_code, commands)
    assert result == ["ERROR: division by zero", "ERROR: division by zero"], \
        f"Expected ['ERROR: division by zero', 'ERROR: division by zero'], got {result}"


def test_invalid_numbers(player_code):
    """Test invalid number error handling."""
    commands = ["ADD 5 abc", "PARSE notanumber", "DIVIDE x y"]
    result = run_player_code(player_code, commands)
    assert result == ["ERROR: invalid number", "ERROR: invalid number", "ERROR: invalid number"], \
        f"Expected ['ERROR: invalid number', 'ERROR: invalid number', 'ERROR: invalid number'], got {result}"


def test_storage_operations(player_code):
    """Test storage and retrieval operations."""
    commands = ["STORE age 25", "GET age", "GET missing"]
    result = run_player_code(player_code, commands)
    assert result == ["Stored: age", "25", "ERROR: key not found"], \
        f"Expected ['Stored: age', '25', 'ERROR: key not found'], got {result}"


def test_mixed_operations(player_code):
    """Test mixed operations with various errors."""
    commands = [
        "ADD 10 5",
        "DIVIDE 20 4",
        "DIVIDE 1 0",
        "PARSE 42",
        "PARSE bad",
        "STORE x 100",
        "GET x",
        "GET y"
    ]
    expected = [
        "15", "5.0", "ERROR: division by zero", "42",
        "ERROR: invalid number", "Stored: x", "100", "ERROR: key not found"
    ]
    result = run_player_code(player_code, commands)
    assert result == expected, f"Expected {expected}, got {result}"
