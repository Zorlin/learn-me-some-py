"""
Pytest tests for Lists concept.

Simple test: Create a list and print each item.
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


class TestLists:
    """Test list basics."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_creates_list(self, player_code: str):
        """Code should create a list with square brackets."""
        assert "[" in player_code and "]" in player_code, \
            "Create a list using square brackets [ ]"

    def test_prints_items(self, player_code: str):
        """Code should print the list items."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        lines = [l for l in stdout.strip().split('\n') if l]
        assert len(lines) >= 3, f"Expected at least 3 items printed, got {len(lines)}"
