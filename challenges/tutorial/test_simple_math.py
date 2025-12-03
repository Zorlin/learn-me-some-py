"""
Tests for Simple Math challenge.

Validates that the learner:
1. Creates a variable called 'result'
2. Calculates 42 + 58
3. Prints the result (100)

PHILOSOPHY: We test the calculation understanding, not creative variations.
"""

import subprocess
import sys


def run_player_code(code: str) -> str:
    """Run player code and return stdout."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout.strip()


def test_has_result_variable(player_code):
    """Check that code defines a result variable."""
    assert "result" in player_code, "Define a variable called 'result'"


def test_has_addition(player_code):
    """Check that code performs addition."""
    assert "+" in player_code, "Use the + operator to add numbers"
    assert "42" in player_code, "Use the number 42"
    assert "58" in player_code, "Use the number 58"


def test_has_print(player_code):
    """Check that code prints the result."""
    assert "print" in player_code, "Use print() to output the result"


def test_output_is_number(player_code):
    """Check that output is a valid number."""
    output = run_player_code(player_code)
    try:
        int(output)
    except ValueError:
        assert False, f"Output should be a number, got: '{output}'"


def test_correct_calculation(player_code):
    """Check that 42 + 58 = 100."""
    output = run_player_code(player_code)
    try:
        result = int(output)
        assert result == 100, f"42 + 58 should equal 100, got {result}"
    except ValueError:
        assert False, f"Output should be a number, got: '{output}'"
