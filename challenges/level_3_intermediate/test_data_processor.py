"""Pytest tests for Data Processing Pipeline challenge."""
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

class TestDataProcessor:
    """Tests for the data processing pipeline challenge."""

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

    def test_has_required_functions(self, player_code: str):
        """Code should define all required functions."""
        required_functions = [
            "clean_data",
            "filter_numbers",
            "square_values",
            "sum_values",
            "process_pipeline",
            "solution"
        ]
        for func in required_functions:
            assert f"def {func}" in player_code, f"Define function '{func}'"

    def test_clean_data_removes_empty_and_none(self, player_code: str):
        """clean_data should remove empty strings and None values."""
        test_code = f'''
{player_code}

# Test clean_data function
test_data = ["1", "2", "", None, "3", "", "abc"]
result = clean_data(test_data)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        # Should remove empty strings and None
        assert "['1', '2', '3', 'abc']" in stdout or "['1', '2', 'abc', '3']" in stdout

    def test_filter_numbers_keeps_only_integers(self, player_code: str):
        """filter_numbers should keep only items convertible to int."""
        test_code = f'''
{player_code}

# Test filter_numbers function
test_data = ["1", "2", "abc", "3", "xyz", "4.5"]
result = filter_numbers(test_data)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        # Should keep only 1, 2, 3
        assert "[1, 2, 3]" in stdout

    def test_square_values_squares_numbers(self, player_code: str):
        """square_values should square each number."""
        test_code = f'''
{player_code}

# Test square_values function
test_data = [1, 2, 3, 4]
result = square_values(test_data)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "[1, 4, 9, 16]" in stdout

    def test_sum_values_calculates_sum(self, player_code: str):
        """sum_values should return the sum of numbers."""
        test_code = f'''
{player_code}

# Test sum_values function
test_data = [1, 2, 3, 4]
result = sum_values(test_data)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "10" in stdout

    def test_process_pipeline_basic(self, player_code: str):
        """process_pipeline should apply operations in order."""
        test_code = f'''
{player_code}

# Test process_pipeline function
data = ["1", "2", "3"]
operations = ["clean", "filter", "square", "sum"]
result = process_pipeline(data, operations)
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        # 1² + 2² + 3² = 1 + 4 + 9 = 14
        assert "14" in stdout

    def test_solution_basic_pipeline(self, player_code: str):
        """Solution should handle basic pipeline correctly."""
        test_code = f'''
{player_code}

# Test full solution
commands = ["DATA 1,2,3", "PIPELINE clean,filter,square,sum"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Data loaded: 3 items" in stdout
        assert "14" in stdout

    def test_solution_with_empty_values(self, player_code: str):
        """Solution should handle empty values in data."""
        test_code = f'''
{player_code}

# Test with empty values
commands = ["DATA 1,2,,3,", "PIPELINE clean,filter,square,sum"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Data loaded: 5 items" in stdout
        assert "14" in stdout

    def test_solution_with_invalid_numbers(self, player_code: str):
        """Solution should filter out non-numeric values."""
        test_code = f'''
{player_code}

# Test with invalid numbers
commands = ["DATA 1,2,abc,3,xyz", "PIPELINE clean,filter,square,sum"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Data loaded: 5 items" in stdout
        assert "14" in stdout

    def test_solution_filter_only(self, player_code: str):
        """Solution should return list when pipeline ends with filter."""
        test_code = f'''
{player_code}

# Test filter-only pipeline
commands = ["DATA 1,abc,2,def,3", "PIPELINE clean,filter"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Data loaded: 5 items" in stdout
        # Should show the filtered numbers
        assert "[1, 2, 3]" in stdout or "[1.0, 2.0, 3.0]" in stdout

    def test_solution_partial_pipeline(self, player_code: str):
        """Solution should handle partial pipeline ending in square."""
        test_code = f'''
{player_code}

# Test partial pipeline
commands = ["DATA 2,3,4", "PIPELINE clean,filter,square"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Data loaded: 3 items" in stdout
        # 2²=4, 3²=9, 4²=16
        assert "[4, 9, 16]" in stdout or "[4.0, 9.0, 16.0]" in stdout

    def test_solution_complex_data(self, player_code: str):
        """Solution should handle complex data with mixed values."""
        test_code = f'''
{player_code}

# Test with complex data
commands = ["DATA 5,,,10,,15,abc,20,def", "PIPELINE clean,filter,square,sum"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Data loaded: 9 items" in stdout
        # 5²+10²+15²+20² = 25+100+225+400 = 750
        assert "750" in stdout

    def test_uses_dictionary_for_operations(self, player_code: str):
        """process_pipeline should use a dictionary to map operations."""
        test_code = f'''
{player_code}

# Test individual operations
data = ["1", "2", "3"]
print("filter:", process_pipeline(data, ["filter"]))
print("square:", process_pipeline([1, 2, 3], ["square"]))
print("sum:", process_pipeline([1, 2, 3], ["sum"]))
'''
        stdout, stderr, returncode = run_player_code(test_code)
        assert returncode == 0, f"Operations test failed: {stderr}"
        # All operations should be supported
        assert "filter:" in stdout
        assert "square:" in stdout
        assert "sum:" in stdout
