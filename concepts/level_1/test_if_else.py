"""Pytest tests for if_else concept."""

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


class TestIfElse:
    """Tests for the if_else concept."""

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

    def test_has_if_statement(self, player_code: str):
        """Code should contain an if statement."""
        assert "if " in player_code, "Code should contain an 'if' statement"

    def test_has_else_statement(self, player_code: str):
        """Code should contain an else statement."""
        assert "else:" in player_code, "Code should contain an 'else' statement"

    def test_uses_comparison_operator(self, player_code: str):
        """Code should use a comparison operator."""
        operators = [">=", "<=", ">", "<", "==", "!="]
        has_operator = any(op in player_code for op in operators)
        assert has_operator, f"Code should use a comparison operator like {operators}"

    def test_checks_gold_vs_sword_price(self, player_code: str):
        """Code should compare gold with sword_price."""
        assert "gold" in player_code, "Code should use the gold variable"
        assert "sword_price" in player_code, "Code should use the sword_price variable"

    def test_prints_appropriate_message(self, player_code: str):
        """Code should print different messages based on the condition."""
        # Test with the provided values (gold=50, sword_price=75)
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        assert len(stdout.strip()) > 0, "Code should print something"

        # With gold=50 and sword_price=75, should print "Not enough gold!"
        assert "Not enough gold!" in stdout or "not enough" in stdout.lower(), \
            "With gold=50 and sword_price=75, should print insufficient funds message"

    def test_modified_gold_values_work(self, player_code: str):
        """Code should work correctly when gold values are modified."""
        # Create a version with enough gold
        enough_gold_code = player_code.replace("gold = 50", "gold = 100")
        stdout, stderr, returncode = run_player_code(enough_gold_code)
        assert returncode == 0, f"Code failed with enough gold: {stderr}"
        assert "bought" in stdout.lower() or "sword" in stdout.lower(), \
            "With enough gold, should print purchase success message"

    def test_proper_indentation(self, player_code: str):
        """Code should use proper indentation for if/else blocks."""
        lines = player_code.split('\n')
        if_indent = None
        else_indent = None
        print_indents = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith('if ') and ':' in stripped:
                if_indent = len(line) - len(line.lstrip())

            elif stripped == 'else:':
                else_indent = len(line) - len(line.lstrip())

            elif stripped.startswith('print('):
                print_indents.append((i, len(line) - len(line.lstrip())))

        assert if_indent is not None, "No if statement found"
        assert else_indent is not None, "No else statement found"
        assert if_indent == else_indent, "if and else should be at the same indentation level"

        # Check that print statements are indented more than if/else
        for line_idx, print_indent in print_indents:
            # Check context around print to see if it's in if/else block
            context_lines = lines[max(0, line_idx-2):line_idx+1]
            in_if_else_block = any('if' in line or 'else:' in line for line in context_lines)

            if in_if_else_block:
                assert print_indent > if_indent, \
                    "print statements inside if/else should be indented more than if/else"

    def test_no_assignment_in_condition(self, player_code: str):
        """Code should not use assignment (=) in if condition."""
        lines = player_code.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('if ') and ':' in line:
                # Check for common assignment mistake
                assert not ('if ' in line and '= ' in line and '==' not in line and '>=' not in line
                           and '<=' not in line and '!=' not in line), \
                    "if condition should use comparison (==) not assignment (=)"

    def test_boolean_logic_understanding(self, player_code: str):
        """Code should demonstrate understanding of boolean logic."""
        # This is a basic test - the code should compile and run
        # More complex boolean logic tests would be in advanced concepts
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"