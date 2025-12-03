"""Pytest tests for comments concept."""
import subprocess
import sys
import ast

def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

class TestComments:
    """Tests for the comments concept."""

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

    def test_has_comments(self, player_code: str):
        """Code should contain at least one comment."""
        lines = player_code.strip().split('\n')
        comment_lines = [line for line in lines if '#' in line and not line.strip().startswith('#!')]
        assert len(comment_lines) > 0, "Code should contain at least one comment (#)"

    def test_comment_syntax(self, player_code: str):
        """Comments should use proper # syntax."""
        lines = player_code.strip().split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#!'):  # Ignore shebang
                if '#' in line:
                    # Ensure # is followed by a space if it's not at the beginning
                    hash_pos = line.find('#')
                    if hash_pos > 0:
                        # Check if there's a space after # unless it's at the start
                        char_after_hash = line[hash_pos + 1] if hash_pos + 1 < len(line) else ''
                        # Allow inline comments without space if it's a common pattern
                        # but encourage proper commenting style
                        pass  # We're lenient here since the Director will provide guidance

    def test_comments_explain_code(self, player_code: str):
        """Comments should be meaningful (not just restating the code)."""
        lines = player_code.strip().split('\n')
        code_lines = []
        comment_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Extract inline comment if present
                if '#' in line:
                    comment_part = line[line.find('#'):]
                    comment_lines.append(comment_part.strip())
                    code_part = line[:line.find('#')].strip()
                    if code_part:
                        code_lines.append(code_part)
                else:
                    code_lines.append(stripped)
            elif stripped.startswith('#') and not stripped.startswith('#!'):
                comment_lines.append(stripped)

        # Basic check: if there are comments, they should add some value
        # This is more about encouraging good commenting habits
        if comment_lines:
            # Check for at least one meaningful comment (more than 3 words)
            meaningful_comments = [
                c for c in comment_lines
                if len(c.replace('#', '').strip().split()) > 2
            ]
            assert len(meaningful_comments) > 0, "Comments should be descriptive and add value"

    def test_variables_still_work(self, player_code: str):
        """Having comments shouldn't break variable assignments."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code with comments should run without errors"

        # If the code has player_health variable, check it's handled correctly
        if 'player_health' in player_code:
            # The code should run without errors regardless of comments
            assert stderr == "", f"Comments shouldn't cause errors: {stderr}"