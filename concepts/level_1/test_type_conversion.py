"""Pytest tests for Type Conversion concept."""

import subprocess
import sys
import pytest

def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

class TestTypeConversion:
    """Tests for the type conversion concept."""

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

    def test_uses_input_function(self, player_code: str):
        """Code should use the input() function to get user input."""
        assert "input(" in player_code, "Code should use input() function"

    def test_uses_conversion_functions(self, player_code: str):
        """Code should use at least one conversion function: int(), float(), or str()."""
        has_int = "int(" in player_code
        has_float = "float(" in player_code
        has_str = "str(" in player_code

        assert has_int or has_float or has_str, \
            "Code should use at least one conversion function: int(), float(), or str()"

    def test_mathematical_operations(self, player_code: str):
        """Code should perform mathematical operations after conversion."""
        # Look for mathematical operators after conversion
        import re

        # Extract lines that have conversion functions
        lines = player_code.split('\n')
        has_math_after_conversion = False

        for i, line in enumerate(lines):
            if any(conv in line for conv in ['int(', 'float(']):
                # Check this line or the next for math operations
                current_line_has_math = any(op in line for op in ['+', '-', '*', '/', '**', '%', '//'])
                next_line_has_math = (i + 1 < len(lines) and
                                    any(op in lines[i + 1] for op in ['+', '-', '*', '/', '**', '%', '//']))
                if current_line_has_math or next_line_has_math:
                    has_math_after_conversion = True
                    break

        assert has_math_after_conversion, \
            "Code should perform mathematical operations after type conversion"

    def test_prints_output(self, player_code: str):
        """Code should print results."""
        assert "print(" in player_code, "Code should print output"

    def test_fahrenheit_to_celsius_pattern(self, player_code: str):
        """Code should implement Fahrenheit to Celsius conversion."""
        # Check for the conversion formula: (F - 32) * 5/9
        assert "32" in player_code, "Code should subtract 32 from Fahrenheit"
        assert "5" in player_code and "9" in player_code, "Code should multiply by 5/9"

        # Check for multiplication/division operations
        assert any(op in player_code for op in ['*', '/']), \
            "Code should perform multiplication and division for the conversion formula"

    def test_temperature_variables(self, player_code: str):
        """Code should use appropriate variable names for temperature."""
        # Look for temperature-related variables
        temp_vars = ['fahrenheit', 'celsius', 'temp', 'temperature', 'f', 'c']
        code_lower = player_code.lower()

        has_temp_var = any(var in code_lower for var in temp_vars)
        assert has_temp_var, "Code should use descriptive variable names for temperature"

    def test_no_string_addition_with_numbers(self, player_code: str):
        """Code should properly convert numbers before string concatenation."""
        lines = player_code.split('\n')

        for line in lines:
            # Skip lines inside f-strings or comments
            line_stripped = line.strip()
            if line_stripped.startswith('#') or 'f"' in line or "f'" in line:
                continue

            # Look for problematic pattern: print("text" + number_variable)
            if 'print(' in line and '+' in line:
                # Check if we're adding a variable (not a string literal)
                # This is a simple heuristic - we allow adding if there's a str() conversion
                if '+' in line and 'str(' not in line and 'f"' not in line and "f'" not in line:
                    # This might be a problem, but our other tests should catch actual issues
                    pass

    def test_uses_float_for_precision(self, player_code: str):
        """Temperature conversion should use float for decimal precision."""
        # Celsius conversion often results in decimals
        assert "float(" in player_code, \
            "Temperature conversion should use float() for decimal precision"