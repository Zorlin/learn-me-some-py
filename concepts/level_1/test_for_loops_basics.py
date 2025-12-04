"""Pytest tests for for_loops_basics concept."""
import subprocess
import sys
import re

def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

class TestForLoopsBasics:
    """Tests for the for loops basics concept."""

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

    def test_uses_for_loop(self, player_code: str):
        """Code should contain a for loop."""
        assert "for " in player_code, "Code should use a for loop"
        assert "in " in player_code, "For loop should use 'in' keyword"

    def test_uses_range_function(self, player_code: str):
        """Code should use the range() function."""
        assert "range(" in player_code, "Code should use range() function"

    def test_prints_numbers_1_to_5(self, player_code: str):
        """Code should print numbers 1 through 5, each on its own line."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        # Split output into lines and filter out empty lines
        lines = [line.strip() for line in stdout.strip().split('\n') if line.strip()]

        # Should have exactly 5 lines
        assert len(lines) == 5, f"Expected 5 lines of output, got {len(lines)}"

        # Each line should contain one number from 1 to 5
        expected_numbers = ['1', '2', '3', '4', '5']
        for i, line in enumerate(lines):
            assert expected_numbers[i] in line, f"Line {i+1} should contain '{expected_numbers[i]}', got: '{line}'"

    def test_starts_at_one_not_zero(self, player_code: str):
        """Output should start at 1, not 0 (common off-by-one error)."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        lines = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
        if lines:
            first_output = lines[0]
            assert '0' not in first_output or '10' in first_output, \
                "Output starts with 0! Remember: range(5) gives 0-4, but range(1, 6) gives 1-5"

    def test_no_hardcoded_prints(self, player_code: str):
        """Code should not use hardcoded print statements for each number."""
        # Count how many times print appears with a number
        hardcoded_prints = len(re.findall(r'print\s*\(\s*[12345]\s*\)', player_code))
        assert hardcoded_prints <= 1, f"Should use a loop, not {hardcoded_prints} hardcoded print statements"