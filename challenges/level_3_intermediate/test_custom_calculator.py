"""
Tests for Custom Calculator Class challenge.

The learner creates a Calculator class with memory and operations.
"""

import subprocess
import sys
import json


def run_player_code(code: str, commands: list) -> list:
    """Run player code with given commands and return results."""
    full_code = f'''
{code}

import json
commands = {repr(commands)}
result = solution(commands)
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


def test_has_calculator_class(player_code):
    """Check that code defines a Calculator class."""
    assert "class Calculator" in player_code, "Define a 'Calculator' class"


def test_has_solution_function(player_code):
    """Check that code defines a solution function."""
    assert "def solution" in player_code, "Define a 'solution' function"


def test_basic_operations(player_code):
    """Test basic math operations."""
    commands = ["ADD 5 3", "SUBTRACT 10 4", "MULTIPLY 6 7"]
    expected = ["8", "6", "42"]
    result = run_player_code(player_code, commands)
    assert result == expected, f"Expected {expected}, got {result}"


def test_division(player_code):
    """Test division including division by zero."""
    commands = ["DIVIDE 20 4", "DIVIDE 10 0", "DIVIDE 15 3"]
    expected = ["5.0", "Error", "5.0"]
    result = run_player_code(player_code, commands)
    assert result == expected, f"Expected {expected}, got {result}"


def test_memory_operations(player_code):
    """Test store, recall, and clear operations."""
    commands = ["STORE 42", "RECALL", "STORE 100", "RECALL", "CLEAR", "RECALL"]
    expected = ["Stored", "42", "Stored", "100", "Cleared", "0"]
    result = run_player_code(player_code, commands)
    assert result == expected, f"Expected {expected}, got {result}"


def test_mixed_operations(player_code):
    """Test a mix of all operations."""
    commands = [
        "ADD 10 20",
        "STORE 50",
        "MULTIPLY 3 4",
        "RECALL",
        "DIVIDE 100 5",
        "CLEAR",
        "RECALL"
    ]
    expected = ["30", "Stored", "12", "50", "20.0", "Cleared", "0"]
    result = run_player_code(player_code, commands)
    assert result == expected, f"Expected {expected}, got {result}"
