"""
Tests for Custom Context Manager challenge.
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

def test_has_timer_class(player_code):
    assert "class Timer" in player_code

def test_successful_execution(player_code):
    input_data = {"will_raise": False, "duration": 0.05}
    result = run_player_code(player_code, input_data)
    
    assert result["success"] == True
    assert result["exception"] is None
    assert 0.04 <= result["elapsed"] <= 0.10

def test_exception_caught(player_code):
    input_data = {"will_raise": True, "duration": 0.02}
    result = run_player_code(player_code, input_data)
    
    assert result["success"] == False
    assert result["exception"] == "ValueError"
    assert 0.01 <= result["elapsed"] <= 0.10

def test_zero_duration(player_code):
    input_data = {"will_raise": False, "duration": 0.0}
    result = run_player_code(player_code, input_data)
    
    assert result["success"] == True
    assert result["exception"] is None

def test_long_duration_success(player_code):
    input_data = {"will_raise": False, "duration": 0.1}
    result = run_player_code(player_code, input_data)
    
    assert result["success"] == True
    assert result["exception"] is None
    assert result["elapsed"] >= 0.08

def test_long_duration_failure(player_code):
    input_data = {"will_raise": True, "duration": 0.1}
    result = run_player_code(player_code, input_data)
    
    assert result["success"] == False
    assert result["exception"] == "ValueError"
    assert result["elapsed"] >= 0.08
