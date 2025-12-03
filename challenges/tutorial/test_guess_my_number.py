"""
Pytest tests for the Guess My Number challenge.

Tests that the player's code:
1. Uses input() to get a guess
2. Compares guess to secret (42)
3. Prints "correct" when guess matches
4. Prints "wrong" when guess doesn't match
"""
import pytest
from io import StringIO
from unittest.mock import patch


def run_player_code(player_code: str, mock_input: str) -> str:
    """
    Execute player code with mocked input and capture output.

    Args:
        player_code: The player's Python code
        mock_input: The value to return from input()

    Returns:
        The captured stdout output
    """
    output = StringIO()

    # Create namespace with mocked input
    namespace = {
        '__builtins__': __builtins__,
        'input': lambda prompt="": mock_input,
        'print': lambda *args, **kwargs: print(*args, file=output, **kwargs),
    }

    exec(player_code, namespace)
    return output.getvalue().strip()


def test_correct_guess(player_code):
    """When guess equals secret (42), should print 'correct'."""
    result = run_player_code(player_code, "42")
    assert result == "correct", f"Expected 'correct' when guess is 42, got '{result}'"


def test_wrong_guess_high(player_code):
    """When guess is higher than secret, should print 'wrong'."""
    result = run_player_code(player_code, "100")
    assert result == "wrong", f"Expected 'wrong' when guess is 100, got '{result}'"


def test_wrong_guess_low(player_code):
    """When guess is lower than secret, should print 'wrong'."""
    result = run_player_code(player_code, "1")
    assert result == "wrong", f"Expected 'wrong' when guess is 1, got '{result}'"


def test_uses_input(player_code):
    """Player code should call input() to get the guess."""
    assert "input(" in player_code, "Your code should use input() to get the user's guess"


def test_uses_int_conversion(player_code):
    """Player code should convert input to int for comparison."""
    assert "int(" in player_code, "Remember: input() returns text. Use int() to convert to a number!"
