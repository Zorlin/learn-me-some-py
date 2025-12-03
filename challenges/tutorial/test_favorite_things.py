"""
Tests for Favorite Things challenge.

Validates that the learner:
1. Creates 'name', 'age', and 'hobby' variables
2. 'age' is a number (not a string)
3. Output follows the format: "NAME is AGE years old and loves HOBBY"

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


def extract_number_value(code: str, var_name: str) -> int | None:
    """Extract number value assigned to a variable."""
    # Match: var = 123 (not quoted)
    pattern = rf'{var_name}\s*=\s*(\d+)'
    match = re.search(pattern, code)
    if match:
        return int(match.group(1))
    return None


def test_has_name_variable(player_code):
    """Check that code defines a 'name' variable."""
    assert "name" in player_code, "Define a variable called 'name'"
    assert re.search(r'name\s*=', player_code), "Assign a value to 'name'"


def test_has_age_variable(player_code):
    """Check that code defines an 'age' variable."""
    assert "age" in player_code, "Define a variable called 'age'"
    assert re.search(r'age\s*=', player_code), "Assign a value to 'age'"


def test_has_hobby_variable(player_code):
    """Check that code defines a 'hobby' variable."""
    assert "hobby" in player_code, "Define a variable called 'hobby'"
    assert re.search(r'hobby\s*=', player_code), "Assign a value to 'hobby'"


def test_age_is_number(player_code):
    """Check that age is a number, not a string."""
    # Check for age = "..." or age = '...' (BAD)
    if re.search(r'age\s*=\s*["\']', player_code):
        raise AssertionError("age should be a NUMBER (no quotes). Use: age = 25, not age = \"25\"")

    # Check for age = NUMBER (GOOD)
    assert re.search(r'age\s*=\s*\d+', player_code), "age should be a number like: age = 25"


def test_output_format(player_code):
    """Check that output follows the required format."""
    output = run_player_code(player_code)

    # Extract user's values
    name = extract_string_value(player_code, "name")
    age = extract_number_value(player_code, "age")
    hobby = extract_string_value(player_code, "hobby")

    # Check the output contains the pattern
    assert "is" in output and "years old" in output and "loves" in output, \
        f"Output should be: 'NAME is AGE years old and loves HOBBY'. Got: '{output}'"

    # Check their values appear in the output
    if name:
        assert name in output, f"Your name '{name}' should appear in the output. Got: '{output}'"
    if age:
        assert str(age) in output, f"Your age '{age}' should appear in the output. Got: '{output}'"
    if hobby:
        assert hobby in output, f"Your hobby '{hobby}' should appear in the output. Got: '{output}'"
