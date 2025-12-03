"""Pytest tests for match_case concept."""

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


class TestMatchCase:
    """Tests for the match_case concept."""

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

    def test_has_match_statement(self, player_code: str):
        """Code should contain a match statement."""
        assert "match " in player_code, "Code should contain a 'match' statement"

    def test_has_case_statements(self, player_code: str):
        """Code should contain at least 3 case statements."""
        case_count = player_code.count("case ")
        assert case_count >= 3, f"Code should have at least 3 case statements, found {case_count}"

    def test_has_catch_all(self, player_code: str):
        """Code should have a catch-all case with underscore."""
        assert "case _:" in player_code, "Code should have a catch-all 'case _:' statement"

    def test_match_structure_valid(self, player_code: str):
        """Match statement should be properly structured."""
        lines = player_code.split('\n')
        match_found = False
        indent_level = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('match ') and ':' in stripped:
                match_found = True
                # Get the indent level of the match statement
                indent_level = len(line) - len(line.lstrip())

            if match_found and stripped.startswith('case ') and ':' in stripped:
                # Case statements should be indented more than match
                case_indent = len(line) - len(line.lstrip())
                assert indent_level is not None, "Found case before match"
                assert case_indent > indent_level, f"Case statement should be indented more than match statement"

        assert match_found, "No valid match statement found"

    def test_menu_behavior(self, player_code: str):
        """Code should create a menu that responds to different choices."""
        # Test that the code handles different inputs appropriately
        # We can't easily test interactive input, but we can validate structure
        assert "input(" in player_code, "Code should get user input"

        # Check for print statements in each case
        lines = player_code.split('\n')
        in_case_block = False
        case_indent = None
        print_count = 0

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('case ') and ':' in stripped:
                in_case_block = True
                case_indent = len(line) - len(line.lstrip())
                continue

            if in_case_block and line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= case_indent:
                    # We've moved out of the case block
                    in_case_block = False

                if in_case_block and 'print(' in stripped:
                    print_count += 1

        assert print_count >= 3, f"Each case should have a print statement, found {print_count}"

    def test_no_break_statements(self, player_code: str):
        """Match cases should not use break (unlike switch statements)."""
        # In match/case, break is not needed like in switch statements
        # We check that break is not used immediately after a case
        lines = player_code.split('\n')
        in_case_block = False
        case_indent = None

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('case ') and ':' in stripped:
                in_case_block = True
                case_indent = len(line) - len(line.lstrip())
                continue

            if in_case_block and line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= case_indent:
                    in_case_block = False

                if in_case_block and stripped.startswith('break'):
                    raise AssertionError("Match cases should not use 'break' statements")

        # If we get here, no inappropriate break statements were found
        assert True