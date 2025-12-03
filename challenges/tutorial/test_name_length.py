"""
Tests for Name Length challenge.

Validates that the learner:
1. Creates a 'name' variable with a string value
2. Uses len() to find the length
3. Output follows the format: "Your name has X letters"

PHILOSOPHY: Let them personalize! We check the PATTERN, not exact values.
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


def extract_string_value(code: str, var_name: str) -> str | None:
    """Extract string value assigned to a variable."""
    # Match: var = "something" or var = 'something'
    pattern = rf'{var_name}\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, code)
    if match:
        return match.group(1)
    return None


def test_has_name_variable(player_code):
    """Check that code defines a 'name' variable."""
    assert "name" in player_code, "Define a variable called 'name'"
    assert re.search(r'name\s*=', player_code), "Assign a value to 'name'"


def test_name_is_string(player_code):
    """Check that name is a string (has quotes)."""
    # Check for name = "..." or name = '...'
    if not re.search(r'name\s*=\s*["\']', player_code):
        raise AssertionError("name should be a STRING (with quotes). Use: name = \"Alice\"")


def test_uses_len_function(player_code):
    """Check that code uses len() function."""
    assert "len(" in player_code, "Use len() to find the length of your name"
    # Check it's used with name
    assert re.search(r'len\s*\(\s*name\s*\)', player_code), "Use len(name) to get the length"


def test_output_format(player_code):
    """Check that output follows the required format."""
    output = run_player_code(player_code)

    # Extract user's name value
    name = extract_string_value(player_code, "name")

    # Check the output contains the pattern
    assert "Your name has" in output and "letters" in output, \
        f"Output should be: 'Your name has X letters'. Got: '{output}'"

    # If we found their name, verify the length is correct
    if name:
        expected_length = len(name)
        assert str(expected_length) in output, \
            f"Your name '{name}' has {expected_length} letters, but output says: '{output}'"
