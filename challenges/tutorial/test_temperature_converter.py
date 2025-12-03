"""
Tests for Temperature Converter challenge.

Validates that the learner:
1. Uses the correct formula: (fahrenheit - 32) * 5 / 9
2. Rounds to 1 decimal place
3. Prints the result

PHILOSOPHY: We test the formula understanding, not exact values.
"""

import subprocess
import sys
import re


def run_player_code(code: str) -> str:
    """Run player code and return stdout."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout.strip()


def test_has_fahrenheit_variable(player_code):
    """Check that code defines a fahrenheit variable."""
    assert "fahrenheit" in player_code, "Define a variable called 'fahrenheit'"


def test_has_celsius_calculation(player_code):
    """Check that code calculates celsius."""
    assert "celsius" in player_code, "Create a 'celsius' variable for the result"
    # Check for the formula components
    has_subtract_32 = "- 32" in player_code or "-32" in player_code
    has_multiply = "*" in player_code
    has_divide = "/" in player_code or "5/9" in player_code
    assert has_subtract_32, "Use the formula: subtract 32 from fahrenheit"
    assert has_multiply or has_divide, "Use multiplication and division in the formula"


def test_has_print(player_code):
    """Check that code prints the result."""
    assert "print" in player_code, "Use print() to output the result"


def test_output_is_number(player_code):
    """Check that output is a valid number."""
    output = run_player_code(player_code)
    try:
        float(output)
    except ValueError:
        assert False, f"Output should be a number, got: '{output}'"


def test_correct_conversion(player_code):
    """Check that 98.6°F converts to approximately 37°C."""
    output = run_player_code(player_code)
    try:
        result = float(output)
        # 98.6°F = 37.0°C (body temperature)
        # Allow some tolerance for different rounding approaches
        assert 36.9 <= result <= 37.1, f"98.6°F should convert to ~37.0°C, got {result}"
    except ValueError:
        assert False, f"Output should be a number, got: '{output}'"


def test_rounded_output(player_code):
    """Check that output appears to be rounded (not too many decimals)."""
    output = run_player_code(player_code)
    # Should have at most 1 decimal place
    if "." in output:
        decimal_part = output.split(".")[1]
        assert len(decimal_part) <= 1, f"Round to 1 decimal place. Got: {output}"
