"""Pytest tests for Data Types concept."""
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

class TestTypes:
    """Tests for the Data Types concept."""

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

    def test_uses_type_function(self, player_code: str):
        """Code should use the type() function."""
        assert "type(" in player_code, "Code should use the type() function"

    def test_prints_type_output(self, player_code: str):
        """Code should print type information."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        # Check for type-related output (should contain <class '...'>)
        assert "<class" in stdout, f"Expected type output like '<class str>', but got: {stdout}"

    def test_types_for_basic_values(self, player_code: str):
        """Code should correctly identify types of basic values."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        # Parse the code to check variables and their types
        try:
            tree = ast.parse(player_code)
        except SyntaxError:
            # Already caught by test_no_syntax_errors
            return

        # Look for variable assignments
        variables = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    # Determine the type based on the value node
                    if isinstance(node.value, ast.Constant):
                        value_type = type(node.value.value).__name__
                        variables[var_name] = value_type
                    elif isinstance(node.value, ast.Num):  # Python < 3.8 compatibility
                        variables[var_name] = "int" if isinstance(node.value.n, int) else "float"
                    elif isinstance(node.value, ast.Str):  # Python < 3.8 compatibility
                        variables[var_name] = "str"
                    elif isinstance(node.value, ast.NameConstant):  # Python < 3.8 compatibility
                        variables[var_name] = "bool"

        # Check if at least one basic type is represented
        expected_types = {"str", "int", "float", "bool"}
        found_types = set(variables.values())
        assert len(found_types.intersection(expected_types)) > 0, \
            f"Code should work with basic types, found variables: {variables}"

    def test_multiple_type_checks(self, player_code: str):
        """Code should check types of multiple variables."""
        # Count how many times type() is called
        type_count = player_code.count("type(")
        assert type_count >= 2, f"Should check types of multiple variables, found {type_count} type() calls"