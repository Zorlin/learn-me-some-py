"""
Pytest tests for the Mad Libs challenge.

Tests that the player's code:
1. Uses all four variables (adjective, noun, verb, place)
2. Builds a story following the pattern "The {adjective} {noun} {verb} to the {place}"
3. Prints the result
"""
import pytest
from io import StringIO
import re


def run_with_vars(player_code: str, adjective: str, noun: str, verb: str, place: str) -> str:
    """
    Execute player code with injected variable values.

    Strategy: Execute player code, then override variables and
    re-execute just the story-building and print parts.
    """
    output = StringIO()

    # Parse the player's code to find the story expression
    # We'll inject our variables and let their story template use them

    # Build modified code that uses our variables
    # Remove the player's variable assignments and inject ours
    lines = player_code.split('\n')
    modified_lines = []

    for line in lines:
        stripped = line.strip()
        # Skip lines that assign to our target variables
        if stripped.startswith('adjective') and '=' in stripped:
            continue
        if stripped.startswith('noun') and '=' in stripped:
            continue
        if stripped.startswith('verb') and '=' in stripped:
            continue
        if stripped.startswith('place') and '=' in stripped:
            continue
        modified_lines.append(line)

    # Prepend our variable assignments
    injected_code = f'''
adjective = "{adjective}"
noun = "{noun}"
verb = "{verb}"
place = "{place}"
''' + '\n'.join(modified_lines)

    namespace = {
        '__builtins__': __builtins__,
        'print': lambda *args, **kwargs: print(*args, file=output, **kwargs),
    }

    exec(injected_code, namespace)
    return output.getvalue().strip()


def test_template_with_silly_story(player_code):
    """Story template should work with 'silly cat danced moon'."""
    result = run_with_vars(player_code, "silly", "cat", "danced", "moon")
    assert result == "The silly cat danced to the moon", (
        f"Expected 'The silly cat danced to the moon', got '{result}'"
    )


def test_template_with_purple_elephant(player_code):
    """Story template should work with 'purple elephant flew supermarket'."""
    result = run_with_vars(player_code, "purple", "elephant", "flew", "supermarket")
    assert result == "The purple elephant flew to the supermarket", (
        f"Expected 'The purple elephant flew to the supermarket', got '{result}'"
    )


def test_template_with_awesome_robot(player_code):
    """Story template should work with 'awesome robot jumped castle'."""
    result = run_with_vars(player_code, "awesome", "robot", "jumped", "castle")
    assert result == "The awesome robot jumped to the castle", (
        f"Expected 'The awesome robot jumped to the castle', got '{result}'"
    )


def test_uses_all_variables(player_code):
    """Player code should reference all four variables."""
    assert "adjective" in player_code, "Your code should use the 'adjective' variable"
    assert "noun" in player_code, "Your code should use the 'noun' variable"
    assert "verb" in player_code, "Your code should use the 'verb' variable"
    assert "place" in player_code, "Your code should use the 'place' variable"
