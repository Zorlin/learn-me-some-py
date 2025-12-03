"""
Tests for Hello World challenge.

The classic first program - validates the learner outputs "Hello, World!"
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


def test_uses_print(player_code):
    """Check that code uses the print function."""
    assert "print" in player_code, "Use the print() function to display text"


def test_outputs_hello_world(player_code):
    """Check that the output is exactly 'Hello, World!'"""
    output = run_player_code(player_code)
    assert output == "Hello, World!", \
        f"Output should be exactly 'Hello, World!' (got: '{output}')"
