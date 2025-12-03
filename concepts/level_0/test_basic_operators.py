"""
Pytest tests for Basic Operators concept (Level 0)

These tests validate that the player correctly:
1. Uses the -= operator to subtract damage from health
2. Uses a comparison operator to check if alive
3. Prints both values in the correct order
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


class TestBasicOperators:
    """Tests for the Basic Operators concept."""

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

    def test_prints_health_value(self, player_code: str):
        """First line of output should be the health value (75)."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

        lines = stdout.strip().split('\n')
        assert len(lines) >= 1, "No output! Use print() to display results"
        assert lines[0].strip() == "75", (
            f"First output should be '75' (100 - 25), got '{lines[0].strip()}'"
        )

    def test_prints_is_alive(self, player_code: str):
        """Second line of output should be True (health > 0)."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

        lines = stdout.strip().split('\n')
        assert len(lines) >= 2, (
            "Expected two outputs: health value AND is_alive boolean"
        )
        assert lines[1].strip() == "True", (
            f"Second output should be 'True' (75 > 0), got '{lines[1].strip()}'"
        )

    def test_uses_subtraction(self, player_code: str):
        """Code should use subtraction (- or -=)."""
        has_minus_equals = "-=" in player_code
        has_subtraction = " - " in player_code or "- " in player_code

        assert has_minus_equals or has_subtraction, (
            "Use the -= operator or - to subtract damage from health"
        )

    def test_uses_comparison(self, player_code: str):
        """Code should use a comparison operator."""
        has_greater = ">" in player_code
        has_comparison = any(op in player_code for op in [">=", "<=", "!=", "==", ">", "<"])

        assert has_comparison, (
            "Use a comparison operator (like >) to check if health > 0"
        )

    def test_complete_output(self, player_code: str):
        """Output should be exactly '75' followed by 'True'."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

        expected = "75\nTrue"
        actual = stdout.strip()
        assert actual == expected, (
            f"Expected output:\n{expected}\n\nGot:\n{actual}"
        )


# For running standalone tests with example solutions
def test_example_solution():
    """Test with the expected solution."""
    code = """
health = 100
damage = 25
health -= damage
is_alive = health > 0
print(health)
print(is_alive)
"""
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "75\nTrue"


def test_alternative_solution():
    """Test alternative valid solution (without -=)."""
    code = """
health = 100
damage = 25
health = health - damage
is_alive = health > 0
print(health)
print(is_alive)
"""
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "75\nTrue"


def test_inline_print():
    """Test inline print solution."""
    code = """
health = 100
damage = 25
health -= damage
print(health)
print(health > 0)
"""
    stdout, stderr, returncode = run_player_code(code)
    assert returncode == 0
    assert stdout.strip() == "75\nTrue"
