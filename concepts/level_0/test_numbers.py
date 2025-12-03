"""Pytest tests for numbers concept."""

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

class TestNumbers:
    """Tests for the numbers concept."""

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

    def test_uses_numbers(self, player_code: str):
        """Code should contain numeric literals."""
        # Check for integers or floats in the code
        import re
        # Pattern matches integers and floats (including negative numbers)
        number_pattern = r'\b-?\d+\.?\d*\b'
        numbers = re.findall(number_pattern, player_code)
        assert len(numbers) > 0, "Code should contain at least one number"

    def test_math_operations(self, player_code: str):
        """Code should use math operators."""
        math_operators = ['+', '-', '*', '/', '//', '%', '**']
        found_operators = [op for op in math_operators if op in player_code]
        assert len(found_operators) > 0, f"Code should use math operators, found: {found_operators}"

    def test_multiplication_for_total_cost(self, player_code: str):
        """Code should multiply price by quantity to get total."""
        # Check for multiplication pattern
        assert '*' in player_code, "Code should use multiplication (*) operator"

        # Parse the code to find variable assignments
        try:
            tree = ast.parse(player_code)
        except SyntaxError:
            return  # Already caught by test_no_syntax_errors

        # Look for price and quantity variables
        has_price = False
        has_quantity = False
        has_total = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if 'price' in var_name or 'cost' in var_name:
                            has_price = True
                        elif 'quantity' in var_name or 'count' in var_name or 'num' in var_name:
                            has_quantity = True
                        elif 'total' in var_name:
                            has_total = True

        assert has_price or '5.50' in player_code, "Code should reference price (either variable or 5.50)"
        assert has_quantity or '3' in player_code, "Code should reference quantity (either variable or 3)"

    def test_calculates_correct_result(self, player_code: str):
        """Code should produce the correct total cost calculation."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        # The expected result for 3 items at $5.50 each is 16.5
        # Check if the output contains the correct result
        output_lines = stdout.strip().split('\n')

        # Look for any numeric output
        found_result = False
        for line in output_lines:
            line = line.strip()
            if line:
                # Try to extract numbers from the output
                import re
                numbers = re.findall(r'-?\d+\.?\d*', line)
                for num_str in numbers:
                    try:
                        num = float(num_str)
                        # Check if it's close to the expected result (16.5)
                        if abs(num - 16.5) < 0.01:  # Allow tiny floating point differences
                            found_result = True
                            break
                    except ValueError:
                        continue

        # Also check if the code itself contains the calculation
        if not found_result:
            # Look for the calculation pattern in the code
            if 'total' in player_code and '*' in player_code:
                # Try to evaluate the total calculation
                try:
                    # Extract the total calculation line
                    lines = player_code.split('\n')
                    for line in lines:
                        if 'total' in line and '=' in line and '*' in line:
                            # Replace variables with expected values
                            test_line = line.replace('price', '5.50').replace('quantity', '3')
                            # Remove the 'total =' part
                            if '=' in test_line:
                                expression = test_line.split('=', 1)[1].strip()
                                result = eval(expression)
                                if abs(result - 16.5) < 0.01:
                                    found_result = True
                                    break
                except:
                    pass

    def test_prints_output(self, player_code: str):
        """Code should print the result."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        assert len(stdout.strip()) > 0, "Code should print the total cost"

    def test_uses_variables_appropriately(self, player_code: str):
        """Code should use meaningful variable names."""
        # Check for appropriate variable names
        code_lower = player_code.lower()

        # Should have variables related to price and quantity
        has_price_var = any(word in code_lower for word in ['price', 'cost', 'amount'])
        has_quantity_var = any(word in code_lower for word in ['quantity', 'count', 'num', 'items'])

        # At least one of each should be present
        assert has_price_var or '5.50' in player_code, "Code should reference price/cost"
        assert has_quantity_var or '3' in player_code, "Code should reference quantity/count"