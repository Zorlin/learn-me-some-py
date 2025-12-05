"""
Pytest tests for Type Conversion concept.

Simple test: Convert a string to int, add 5, print the result.
"""
import subprocess
import sys


def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode


class TestTypeConversion:
    """Test type conversion basics."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_uses_int(self, player_code: str):
        """Code should use int() to convert the string."""
        assert "int(" in player_code, "Use int() to convert the string '25' to a number"

    def test_outputs_30(self, player_code: str):
        """Code should output 30 (25 + 5)."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        assert "30" in stdout, "Expected output to include 30 (25 + 5)"
