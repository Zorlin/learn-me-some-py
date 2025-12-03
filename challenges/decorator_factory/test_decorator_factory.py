"""
Tests for Decorator Factory challenge.
"""

import subprocess
import sys
import json

def run_player_code(code: str, input_data):
    """Execute player code."""
    full_code = f'''
{code}

import json
input_data = {repr(input_data)}
result = solution(input_data)
print(json.dumps(result))
'''
    result = subprocess.run([sys.executable, "-c", full_code], capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        raise RuntimeError(f"Code failed: {result.stderr}")
    return json.loads(result.stdout.strip())

def test_has_solution_function(player_code):
    assert "def solution" in player_code

def test_has_retry_decorator(player_code):
    assert "def retry" in player_code

def test_succeeds_first_try(player_code):
    input_data = {"max_attempts": 3, "delay_seconds": 0.01, "failures_before_success": 0}
    result = run_player_code(player_code, input_data)
    assert result == "SUCCESS"

def test_succeeds_second_try(player_code):
    input_data = {"max_attempts": 3, "delay_seconds": 0.01, "failures_before_success": 1}
    result = run_player_code(player_code, input_data)
    assert result == "SUCCESS"

def test_succeeds_last_try(player_code):
    input_data = {"max_attempts": 3, "delay_seconds": 0.01, "failures_before_success": 2}
    result = run_player_code(player_code, input_data)
    assert result == "SUCCESS"

def test_exhausts_all_attempts(player_code):
    input_data = {"max_attempts": 3, "delay_seconds": 0.01, "failures_before_success": 3}
    result = run_player_code(player_code, input_data)
    assert result == "FAILED"

def test_single_attempt_success(player_code):
    input_data = {"max_attempts": 1, "delay_seconds": 0.01, "failures_before_success": 0}
    result = run_player_code(player_code, input_data)
    assert result == "SUCCESS"

def test_single_attempt_failure(player_code):
    input_data = {"max_attempts": 1, "delay_seconds": 0.01, "failures_before_success": 1}
    result = run_player_code(player_code, input_data)
    assert result == "FAILED"
