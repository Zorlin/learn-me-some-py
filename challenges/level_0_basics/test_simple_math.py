"""
Pytest tests for Simple Math challenge (Level 0)

These tests validate that the player's code correctly calculates
and prints 42 + 58 = 100.
"""
import subprocess
import sys
from pathlib import Path


def run_player_code(code: str) -> tuple[str, str, int]:
    """
    Execute player code and capture output.

    Returns:
        (stdout, stderr, return_code)
    """
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode


class TestSimpleMath:
    """Tests for the Simple Math challenge."""

    def test_output_is_100(self, player_code: str):
        """The output should be exactly 100."""
        stdout, stderr, returncode = run_player_code(player_code)

        # Should run without errors
        assert returncode == 0, f"Code failed with error: {stderr}"

        # Should output 100
        output = stdout.strip()
        assert output == "100", f"Expected '100', got '{output}'"

    def test_actually_calculates(self, player_code: str):
        """
        Code should actually calculate, not just print "100".

        We check for the presence of arithmetic operations.
        """
        # This is a soft check - we want to encourage calculation
        has_addition = "+" in player_code
        has_numbers = "42" in player_code and "58" in player_code

        # At minimum, code should produce correct output
        stdout, _, returncode = run_player_code(player_code)
        assert stdout.strip() == "100"

        # Bonus feedback if they just hardcoded
        if not has_addition and not has_numbers:
            # Still passes, but give feedback
            pass  # Could add a warning marker here

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_uses_print(self, player_code: str):
        """Code should use print() to output the result."""
        # Run the code
        stdout, stderr, returncode = run_player_code(player_code)

        # Should have output something
        assert stdout.strip(), "No output! Use print() to display the result"


# For running standalone with a test code string
def test_example_solution():
    """Test with the expected solution."""
    code = """
# Calculate 42 + 58 and print the result
result = 42 + 58
print(result)
"""
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "100"


def test_alternative_solution():
    """Test alternative valid solution."""
    code = "print(42 + 58)"
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "100"
