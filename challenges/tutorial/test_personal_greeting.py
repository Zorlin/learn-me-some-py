"""
Tests for Personal Greeting challenge.

Validates that the learner:
1. Creates a 'name' variable
2. Uses print() to output a greeting
3. The output includes "Hello" and their name

PHILOSOPHY: This is Level 0. We want experimentation!
- "Hello Ben" is fine
- "Hello, Ben!" is also fine
- As long as they use a variable and greet, they pass
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


def extract_name_value(code: str) -> str | None:
    """Extract the value assigned to the 'name' variable."""
    # Match: name = "something" or name = 'something'
    match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', code)
    if match:
        return match.group(1)
    return None


def test_has_name_variable(player_code):
    """Check that code defines a 'name' variable."""
    assert "name" in player_code, "Define a variable called 'name'"
    assert "name =" in player_code or "name=" in player_code, "Assign a value to 'name'"


def test_has_print_statement(player_code):
    """Check that code uses print()."""
    assert "print" in player_code, "Use print() to output your greeting"


def test_output_contains_hello(player_code):
    """Check that output contains 'Hello' (case insensitive)."""
    output = run_player_code(player_code)
    assert "hello" in output.lower(), f"Your greeting should include 'Hello'. Got: '{output}'"


def test_output_contains_name(player_code):
    """Check that the output includes the name from the variable."""
    output = run_player_code(player_code)
    name_value = extract_name_value(player_code)

    if name_value:
        assert name_value in output, f"Your greeting should include your name '{name_value}'. Got: '{output}'"
    else:
        # They used a variable but we can't parse it - just check output isn't empty
        assert len(output) > 5, "Your greeting seems too short - make sure to include your name!"
