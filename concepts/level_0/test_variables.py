"""
Pytest tests for Variables concept (Level 0)

These tests validate that the player correctly:
1. Creates a variable with a value
2. Uses print() to display the variable's value
"""
import subprocess
import sys


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


class TestVariables:
    """Tests for the Variables concept."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_code_runs(self, player_code: str):
        """Code should execute without runtime errors."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

    def test_creates_variable(self, player_code: str):
        """Code should create a variable using assignment (=)."""
        assert "=" in player_code, (
            "Use = to create a variable, like: score = 100"
        )

    def test_uses_print(self, player_code: str):
        """Code should use print() to display output."""
        assert "print" in player_code, (
            "Use print() to display your variable's value"
        )

    def test_produces_output(self, player_code: str):
        """Code should print something."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        assert stdout.strip(), (
            "No output! Use print(variable_name) to display your variable"
        )

    def test_prints_number(self, player_code: str):
        """Output should be a number (the score value)."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        output = stdout.strip()
        # The solution prints 100, but any number is acceptable for learning
        try:
            int(output)
        except ValueError:
            raise AssertionError(
                f"Expected a number to be printed, got: '{output}'\n"
                "Create a variable with a number and print it!"
            )


# Standalone tests for example solutions
def test_example_solution():
    """Test with the expected solution."""
    code = """
score = 100
print(score)
"""
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "100"


def test_alternative_variable_name():
    """Test with different variable name."""
    code = """
player_score = 42
print(player_score)
"""
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "42"


def test_with_comment():
    """Test solution with comment preserved."""
    code = """
# Create a score variable and print it
score = 100
print(score)
"""
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "100"
