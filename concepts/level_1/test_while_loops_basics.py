"""Pytest tests for while_loops_basics concept."""

import subprocess
import sys
from typing import Any, Dict, List


def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode


class TestWhileLoopsBasics:
    """Tests for the while_loops_basics concept."""

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

    def test_has_while_loop(self, player_code: str):
        """Code should contain a while loop."""
        assert "while " in player_code, "Code should contain a 'while' loop"

    def test_has_initialization(self, player_code: str):
        """Code should initialize a counter variable."""
        lines = [line.strip() for line in player_code.split('\n') if line.strip()]
        has_count = any('count' in line and '=' in line for line in lines)
        has_counter = any(line.startswith(('count = ', 'counter = ', 'i = '))
                          for line in lines)

        assert has_count or has_counter, "Code should initialize a counter variable (count, counter, or i)"

    def test_has_decrement(self, player_code: str):
        """Code should decrement the counter in the loop."""
        # Check for decrement patterns
        decrement_patterns = ['-= 1', '--', '- 1']
        has_decrement = any(pattern in player_code for pattern in decrement_patterns)

        assert has_decrement, "Code should decrement the counter variable in the loop"

    def test_counts_down_from_five(self, player_code: str):
        """Code should count down starting from 5."""
        # Check that the initial value is 5
        lines = player_code.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('count = ', 'counter = ', 'i = ')):
                value = stripped.split('=')[1].strip()
                # Handle possible expressions like "5" or just 5
                if value == "5":
                    break
        else:
            # If we don't find explicit initialization, check for count = 5 pattern
            assert 'count = 5' in player_code or 'counter = 5' in player_code or 'i = 5' in player_code, \
                   "Counter should be initialized to 5"

    def test_prints_countdown(self, player_code: str):
        """Code should print numbers during countdown."""
        assert "print(" in player_code, "Code should print numbers during countdown"

        # Test that it prints the expected countdown
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        # Check that numbers 5, 4, 3, 2, 1 appear in output
        expected_numbers = ['5', '4', '3', '2', '1']
        for num in expected_numbers:
            assert num in stdout, f"Output should contain the number {num}"

    def test_prints_blast_off(self, player_code: str):
        """Code should print 'Blast off!' after countdown."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        assert "Blast off!" in stdout, "Code should print 'Blast off!' after the countdown"

    def test_loop_condition_correct(self, player_code: str):
        """Loop should use correct condition (> 0)."""
        assert "count > 0" in player_code or "counter > 0" in player_code or "i > 0" in player_code, \
               "Loop condition should check if counter > 0"

    def test_no_infinite_loop(self, player_code: str):
        """Code should not create an infinite loop."""
        # This is implicitly tested by the timeout in run_player_code
        # But we can also check that the counter is modified
        lines = player_code.split('\n')
        in_loop = False
        modifies_counter = False

        for line in lines:
            if 'while' in line:
                in_loop = True
                continue

            if in_loop and line.strip():
                # Check if line modifies a counter variable
                if any(op in line for op in ['-= 1', '+=', '=', '--', '-=']):
                    if any(var in line for var in ['count', 'counter', 'i']):
                        modifies_counter = True
                        break

        assert modifies_counter, "Loop should modify the counter variable to avoid infinite loops"

    def test_proper_indentation(self, player_code: str):
        """Code should use proper indentation for the loop body."""
        lines = player_code.split('\n')
        while_found = False
        while_indent = None

        for line in lines:
            if 'while' in line and ':' in line:
                while_found = True
                while_indent = len(line) - len(line.lstrip())
                continue

            if while_found and line.strip():
                current_indent = len(line) - len(line.lstrip())
                # Loop body should be indented more than while statement
                if current_indent <= while_indent:
                    # We've moved out of the loop block
                    if 'print(' in line or 'count' in line:
                        raise AssertionError("Loop body should be properly indented")
                    while_found = False

    def test_uses_print_variable(self, player_code: str):
        """Code should print the counter variable, not just literals."""
        # Check that print statements reference variables
        lines = player_code.split('\n')
        prints_variable = False

        for line in lines:
            if 'print(' in line:
                # Check if print contains a variable name
                if any(var in line for var in ['count', 'counter', 'i']):
                    prints_variable = True

        assert prints_variable, "Code should print the counter variable, not just static text"