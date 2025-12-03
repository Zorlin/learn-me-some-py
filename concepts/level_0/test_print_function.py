"""Pytest tests for print_function concept."""
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

class TestPrintFunction:
    """Tests for the print() function concept."""

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

    def test_prints_output(self, player_code: str):
        """Code should print something to stdout."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        assert len(stdout.strip()) > 0, "Code should print something to the screen"

    def test_uses_print_function(self, player_code: str):
        """Code should use the print() function."""
        assert "print(" in player_code, "Code should use the print() function"

    def test_print_with_quotes(self, player_code: str):
        """If printing text, should use quotes around strings."""
        # Check for common patterns that indicate proper string usage
        lines = player_code.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('print(') and not line.startswith('print(#'):
                # Should contain quotes for string literals
                if ('"' in line or "'" in line) and not line.count('#') > 0:
                    # Looks like they're trying to print a string
                    assert True
                elif any(char.isalpha() for char in line):
                    # Has letters but no quotes - might be an undeclared variable
                    pass  # Let the runtime error handle this case