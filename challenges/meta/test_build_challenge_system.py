"""
Tests for Meta: Build Challenge Validation System.

The system that validates YOUR solutions!
"""

import subprocess
import sys
import json


def run_player_code(code: str, test_input) -> dict:
    """Run player code with given input and return result."""
    full_code = f'''
{code}

import json
# Test input
solution_code = {repr(test_input[0])}
test_cases = {repr(test_input[1])}

results = validate_solution(solution_code, test_cases)

# Convert results to dict for JSON
output = []
for r in results:
    output.append({{
        "name": r.name,
        "passed": r.passed,
        "expected": r.expected,
        "actual": r.actual,
        "error": r.error
    }})
print(json.dumps(output))
'''
    result = subprocess.run([sys.executable, "-c", full_code], capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        raise RuntimeError(f"Code failed: {result.stderr}")
    return json.loads(result.stdout.strip())


def test_has_validate_solution_function(player_code):
    """Check that code defines validate_solution function."""
    assert "def validate_solution" in player_code, "Define a 'validate_solution' function"


def test_has_test_result_class(player_code):
    """Check that code defines TestResult dataclass."""
    assert "class TestResult" in player_code, "Define a 'TestResult' dataclass"
    assert "@dataclass" in player_code, "Use @dataclass decorator"


def test_simple_function(player_code):
    """Test validating a simple function that passes."""
    results = run_player_code(player_code, [
        "def solution(x): return x * 2",
        [{"name": "double_5", "input": [5], "expected": 10}]
    ])
    
    assert len(results) == 1, "Should return one test result"
    assert results[0]["passed"] is True, "Simple test should pass"
    assert results[0]["actual"] == 10, "Should compute correct result"


def test_multiple_tests(player_code):
    """Test validating multiple test cases."""
    results = run_player_code(player_code, [
        "def solution(x): return x + 1",
        [
            {"name": "add_one_5", "input": [5], "expected": 6},
            {"name": "add_one_10", "input": [10], "expected": 11}
        ]
    ])
    
    assert len(results) == 2, "Should return two test results"
    assert all(r["passed"] for r in results), "All tests should pass"


def test_failing_test(player_code):
    """Test validating a function that fails the test."""
    results = run_player_code(player_code, [
        "def solution(x): return x * 2",
        [{"name": "wrong", "input": [5], "expected": 11}]
    ])
    
    assert len(results) == 1, "Should return one test result"
    assert results[0]["passed"] is False, "Test should fail"
    assert results[0]["expected"] == 11, "Should record expected value"
    assert results[0]["actual"] == 10, "Should record actual value"
