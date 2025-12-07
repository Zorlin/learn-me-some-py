"""Pytest tests for String Methods concept."""
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


class TestStringMethods:
    """Tests for parsing user command."""

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

    def test_prints_action(self, player_code: str):
        """Should print the action (attack)."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        stdout_lower = stdout.lower()
        assert "attack" in stdout_lower, f"Should print 'attack' - got: {stdout}"

    def test_prints_target(self, player_code: str):
        """Should print the target (goblin)."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        stdout_lower = stdout.lower()
        assert "goblin" in stdout_lower, f"Should print 'goblin' - got: {stdout}"

    def test_uses_strip_or_split(self, player_code: str):
        """Code should use strip() or split() to clean input."""
        code_lower = player_code.lower()
        uses_cleaning = "strip" in code_lower or "split" in code_lower
        assert uses_cleaning, "Use .strip() to remove whitespace or .split() to parse the command"
