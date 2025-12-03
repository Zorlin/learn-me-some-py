"""Pytest tests for strings concept."""
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


class TestStrings:
    """Tests for the strings concept."""

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

    def test_creates_greeting(self, player_code: str):
        """Code should create a greeting using the user's name."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        # Check that output contains "Hello" and the name
        assert "Hello" in stdout or "hello" in stdout, "Output should contain a greeting"
        assert "Player" in stdout, "Output should contain the name 'Player'"
        assert "!" in stdout, "Output should contain an exclamation mark"

    def test_uses_string_concatenation(self, player_code: str):
        """Code should use string concatenation with + operator."""
        assert "+" in player_code, "Code should use the + operator for string concatenation"

        # Check that it's concatenating strings with "Hello" and name
        lines = player_code.split('\n')
        found_concatenation = False
        for line in lines:
            if '+' in line and 'Hello' in line and 'name' in line:
                found_concatenation = True
                break

        assert found_concatenation, "Should concatenate 'Hello, ' + name + '!'"

    def test_uses_variables(self, player_code: str):
        """Code should use variables for name and greeting."""
        assert "name = " in player_code, "Code should assign a value to name variable"

        # Look for greeting variable
        lines = player_code.split('\n')
        found_greeting_var = False
        for line in lines:
            if 'greeting' in line and '=' in line:
                found_greeting_var = True
                break

        assert found_greeting_var, "Code should create a greeting variable"

    def test_prints_result(self, player_code: str):
        """Code should print the greeting."""
        assert "print(" in player_code, "Code should print the result"

        # Check that it's printing the greeting
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        assert len(stdout.strip()) > 0, "Should print output to screen"

    def test_quotes_consistency(self, player_code: str):
        """Code should use consistent quote marks."""
        # Check for mismatched quotes
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            if '"' in str(e) or "'" in str(e):
                raise AssertionError(f"Quote marks might be mismatched: {e.msg}")

    def test_output_format(self, player_code: str):
        """Output should be in the format 'Hello, [name]!'"""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        expected_patterns = [
            "Hello, Player!",
            "Hello, Player!",
            "Hello , Player!",
            "Hello ,Player!",
        ]

        # Clean up whitespace and check
        output_clean = stdout.strip()
        assert any(pattern.lower() in output_clean.lower() for pattern in expected_patterns), \
            f"Output should be like 'Hello, Player!' but got: {output_clean}"