"""Pytest tests for Safe Calculator with Error Handling challenge."""
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

class TestErrorHandler:
    """Tests for the error handling calculator challenge."""

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

    def test_has_solution_function(self, player_code: str):
        """Code should define a solution function."""
        assert "def solution" in player_code, "Define a 'solution' function"

    def test_basic_addition(self, player_code: str):
        """Solution should handle basic addition."""
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

    def test_basic_division(self, player_code: str):
        """Solution should handle normal division."""
        test_code = f'''
{player_code}

# Test DIVIDE command
commands = ["DIVIDE 10 2"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "5.0" in stdout

    def test_division_by_zero_error(self, player_code: str):
        """Solution should handle division by zero gracefully."""
        test_code = f'''
{player_code}

# Test division by zero
commands = ["DIVIDE 10 0"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "ERROR: division by zero" in stdout

    def test_invalid_number_error(self, player_code: str):
        """Solution should handle invalid numbers gracefully."""
        test_code = f'''
{player_code}

# Test invalid numbers
commands = ["ADD 5 abc", "PARSE notanumber"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        # Should have two error messages
        assert stdout.count("ERROR: invalid number") == 2

    def test_storage_and_retrieval(self, player_code: str):
        """Solution should handle STORE and GET operations."""
        test_code = f'''
{player_code}

# Test storage operations
commands = ["STORE age 25", "GET age"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Stored: age" in stdout
        assert "25" in stdout

    def test_key_not_found_error(self, player_code: str):
        """Solution should handle missing key errors."""
        test_code = f'''
{player_code}

# Test missing key
commands = ["STORE x 100", "GET missing"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Stored: x" in stdout
        assert "ERROR: key not found" in stdout

    def test_parse_valid_number(self, player_code: str):
        """Solution should parse valid numbers correctly."""
        test_code = f'''
{player_code}

# Test PARSE with valid number
commands = ["PARSE 42"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "42" in stdout

    def test_mixed_operations(self, player_code: str):
        """Solution should handle mixed operations without crashing."""
        test_code = f'''
{player_code}

# Test mixed operations
commands = [
    "ADD 10 5",
    "DIVIDE 20 4",
    "DIVIDE 1 0",
    "PARSE 42",
    "PARSE bad",
    "STORE x 100",
    "GET x",
    "GET y"
]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        expected = [
            "15", "5.0", "ERROR: division by zero", "42",
            "ERROR: invalid number", "Stored: x", "100", "ERROR: key not found"
        ]
        for exp in expected:
            assert exp in stdout

    def test_error_handling_catches_exceptions(self, player_code: str):
        """Solution should use try/except to handle errors."""
        test_code = f'''
{player_code}

# Check that try/except is used
if "try:" not in player_code:
    print("NO_TRY", end="")
if "except" not in player_code:
    print("NO_EXCEPT", end="")
else:
    print("HAS_ERROR_HANDLING", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "HAS_ERROR_HANDLING" in stdout

    def test_no_crashes_on_extreme_input(self, player_code: str):
        """Solution should never crash, even with extreme input."""
        test_code = f'''
{player_code}

# Test extreme cases
commands = [
    "ADD 999999999999999999999 1",
    "DIVIDE 1 0.0000000000000001",
    "PARSE",
    "GET",
    "STORE",
    ""
]
result = solution(commands)
print(f"Result count: {{len(result)}}", end="")
'''
        stdout, stderr, returncode = run_player_code(test_code)
        assert returncode == 0, f"Code crashed with: {stderr}"
        # Should not crash and should return results
        assert "Result count:" in stdout
