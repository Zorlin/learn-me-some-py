"""Pytest tests for input_function concept."""
import subprocess
import sys
from unittest.mock import patch
from io import StringIO

def run_player_code(code: str, user_inputs: list[str] = None) -> tuple[str, str, int]:
    """Execute player code with simulated user input and capture output."""
    if user_inputs:
        # Create a mock for input() that returns the specified values
        input_mock = iter(user_inputs)
        with patch('builtins.input', side_effect=lambda prompt: next(input_mock)):
            # Redirect stdout to capture print output
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            try:
                exec(code, {})
                stdout = captured_output.getvalue()
                returncode = 0
                stderr = ""
            except Exception as e:
                stdout = captured_output.getvalue()
                returncode = 1
                stderr = str(e)
            finally:
                sys.stdout = old_stdout

            return stdout, stderr, returncode
    else:
        # No input mocking needed
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout, result.stderr, result.returncode

class TestInputFunction:
    """Tests for the input() function concept."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_uses_input_function(self, player_code: str):
        """Code should use the input() function."""
        # Check that input() is called in the code
        assert "input(" in player_code, "Code should call input() function"

    def test_code_runs_with_input(self, player_code: str):
        """Code should execute without runtime errors when given input."""
        # Test with some sample inputs
        stdout, stderr, returncode = run_player_code(
            player_code,
            user_inputs=["Archer", "blue"]
        )
        assert returncode == 0, f"Code failed with error: {stderr}"

    def test_asks_for_name_and_color(self, player_code: str):
        """Code should ask for both name and favorite color."""
        # Check for relevant keywords in prompts
        code_lower = player_code.lower()
        assert any(word in code_lower for word in ["name", "what's your name"]), \
               "Code should ask for the user's name"
        assert any(word in code_lower for word in ["color", "favourite", "favorite"]), \
               "Code should ask for the user's favorite color"

    def test_uses_user_input_in_output(self, player_code: str):
        """Code should use the user's input in its output."""
        # Run with specific inputs and check if they appear in output
        stdout, stderr, returncode = run_player_code(
            player_code,
            user_inputs=["Zara", "purple"]
        )
        assert returncode == 0, f"Code failed: {stderr}"
        assert "Zara" in stdout or "zara" in stdout, \
            "Output should contain the user's name"
        assert "purple" in stdout, \
            "Output should contain the user's favorite color"

    def test_prints_message(self, player_code: str):
        """Code should print a message using the inputs."""
        stdout, stderr, returncode = run_player_code(
            player_code,
            user_inputs=["Sam", "green"]
        )
        assert returncode == 0, f"Code failed: {stderr}"
        assert len(stdout.strip()) > 0, \
            "Code should print something to the screen"

    def test_multiple_different_inputs(self, player_code: str):
        """Code should work with different user inputs."""
        test_cases = [
            ["Alex", "red"],
            ["Jordan", "yellow"],
            ["Casey", "orange"],
            ["Morgan", "black"]
        ]

        for name, color in test_cases:
            stdout, stderr, returncode = run_player_code(
                player_code,
                user_inputs=[name, color]
            )
            assert returncode == 0, f"Code failed with inputs {name}, {color}: {stderr}"
            assert name in stdout or name.lower() in stdout, \
                f"Output should contain {name}"
            assert color in stdout or color.lower() in stdout, \
                f"Output should contain {color}"