"""Pytest tests for Custom Calculator Class challenge."""
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

class TestCustomCalculator:
    """Tests for the custom calculator class challenge."""

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

    def test_has_calculator_class(self, player_code: str):
        """Code should define a Calculator class."""
        assert "class Calculator" in player_code, "Define a 'Calculator' class"
        assert "def solution" in player_code, "Define a 'solution' function"

    def test_calculator_initialization(self, player_code: str):
        """Calculator should initialize with memory = 0."""
        test_code = f'''
{player_code}

# Test Calculator initialization
calc = Calculator()
print(f"memory: {{calc.memory}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "memory: 0" in stdout

    def test_add_method(self, player_code: str):
        """Calculator.add should return sum of two numbers."""
        test_code = f'''
{player_code}

# Test add method
calc = Calculator()
result = calc.add(5, 3)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "8" in stdout

    def test_subtract_method(self, player_code: str):
        """Calculator.subtract should return difference."""
        test_code = f'''
{player_code}

# Test subtract method
calc = Calculator()
result = calc.subtract(10, 4)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "6" in stdout

    def test_multiply_method(self, player_code: str):
        """Calculator.multiply should return product."""
        test_code = f'''
{player_code}

# Test multiply method
calc = Calculator()
result = calc.multiply(6, 7)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "42" in stdout

    def test_divide_method_normal(self, player_code: str):
        """Calculator.divide should return quotient for normal division."""
        test_code = f'''
{player_code}

# Test divide method
calc = Calculator()
result = calc.divide(20, 4)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "5.0" in stdout

    def test_divide_method_zero(self, player_code: str):
        """Calculator.divide should return 'Error' for division by zero."""
        test_code = f'''
{player_code}

# Test divide by zero
calc = Calculator()
result = calc.divide(10, 0)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Error" in stdout

    def test_store_method(self, player_code: str):
        """Calculator.store should save value to memory."""
        test_code = f'''
{player_code}

# Test store method
calc = Calculator()
calc.store(42)
print(f"memory: {{calc.memory}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "memory: 42" in stdout

    def test_recall_method(self, player_code: str):
        """Calculator.recall should return current memory value."""
        test_code = f'''
{player_code}

# Test recall method
calc = Calculator()
calc.store(100)
result = calc.recall()
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "100" in stdout

    def test_clear_method(self, player_code: str):
        """Calculator.clear should reset memory to 0."""
        test_code = f'''
{player_code}

# Test clear method
calc = Calculator()
calc.store(50)
calc.clear()
print(f"memory: {{calc.memory}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "memory: 0" in stdout

    def test_solution_add_command(self, player_code: str):
        """Solution should handle ADD command."""
        test_code = f'''
{player_code}

# Test ADD command
commands = ["ADD 5 3"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "8" in stdout

    def test_solution_divide_command(self, player_code: str):
        """Solution should handle DIVIDE command including errors."""
        test_code = f'''
{player_code}

# Test DIVIDE commands
commands = ["DIVIDE 20 4", "DIVIDE 10 0", "DIVIDE 15 3"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "5.0" in stdout
        assert "Error" in stdout
        assert "5.0" in stdout

    def test_solution_memory_commands(self, player_code: str):
        """Solution should handle STORE, RECALL, and CLEAR commands."""
        test_code = f'''
{player_code}

# Test memory commands
commands = ["STORE 42", "RECALL", "STORE 100", "RECALL", "CLEAR", "RECALL"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Stored" in stdout
        assert "42" in stdout
        assert "Stored" in stdout
        assert "100" in stdout
        assert "Cleared" in stdout
        assert "0" in stdout

    def test_solution_mixed_operations(self, player_code: str):
        """Solution should handle mixed operations."""
        test_code = f'''
{player_code}

# Test mixed operations
commands = [
    "ADD 10 20",
    "STORE 50",
    "MULTIPLY 3 4",
    "RECALL",
    "DIVIDE 100 5",
    "CLEAR",
    "RECALL"
]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        expected = ["30", "Stored", "12", "50", "20.0", "Cleared", "0"]
        for exp in expected:
            assert exp in stdout

    def test_all_methods_require_self(self, player_code: str):
        """All methods should properly use 'self' parameter."""
        test_code = f'''
{player_code}

# Test that methods work with instance
calc = Calculator()

# Test all methods exist and are callable
methods = ["add", "subtract", "multiply", "divide", "store", "recall", "clear"]
for method in methods:
    if hasattr(calc, method):
        print(f"{{method}}: yes", end="")
    else:
        print(f"{{method}}: no", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        for method in ["add", "subtract", "multiply", "divide", "store", "recall", "clear"]:
            assert f"{method}: yes" in stdout
