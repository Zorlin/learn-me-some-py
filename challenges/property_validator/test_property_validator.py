"""
Tests for Property Validator with Descriptors challenge.
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

def test_has_validators(player_code):
    assert "class PositiveInt" in player_code
    assert "class EmailStr" in player_code
    assert "class RangeInt" in player_code

def test_positive_int_valid(player_code):
    input_data = {"validator": "PositiveInt", "value": 42}
    expected = {"status": "valid", "stored_value": 42}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_positive_int_invalid_negative(player_code):
    input_data = {"validator": "PositiveInt", "value": -5}
    result = run_player_code(player_code, input_data)
    assert result["status"] == "invalid"
    assert "positive" in result["error"]

def test_positive_int_invalid_zero(player_code):
    input_data = {"validator": "PositiveInt", "value": 0}
    result = run_player_code(player_code, input_data)
    assert result["status"] == "invalid"
    assert "positive" in result["error"]

def test_email_valid(player_code):
    input_data = {"validator": "EmailStr", "value": "user@example.com"}
    expected = {"status": "valid", "stored_value": "user@example.com"}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_email_invalid_no_at(player_code):
    input_data = {"validator": "EmailStr", "value": "invalidemail.com"}
    result = run_player_code(player_code, input_data)
    assert result["status"] == "invalid"
    assert "@" in result["error"]

def test_email_invalid_no_dot(player_code):
    input_data = {"validator": "EmailStr", "value": "user@example"}
    result = run_player_code(player_code, input_data)
    assert result["status"] == "invalid"
    assert "." in result["error"]

def test_range_int_valid_min(player_code):
    input_data = {"validator": "RangeInt", "min": 0, "max": 100, "value": 0}
    expected = {"status": "valid", "stored_value": 0}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_range_int_valid_max(player_code):
    input_data = {"validator": "RangeInt", "min": 0, "max": 100, "value": 100}
    expected = {"status": "valid", "stored_value": 100}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_range_int_valid_middle(player_code):
    input_data = {"validator": "RangeInt", "min": 0, "max": 100, "value": 50}
    expected = {"status": "valid", "stored_value": 50}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_range_int_invalid_below(player_code):
    input_data = {"validator": "RangeInt", "min": 0, "max": 100, "value": -1}
    result = run_player_code(player_code, input_data)
    assert result["status"] == "invalid"
    assert "between" in result["error"] or "0" in result["error"]

def test_range_int_invalid_above(player_code):
    input_data = {"validator": "RangeInt", "min": 0, "max": 100, "value": 101}
    result = run_player_code(player_code, input_data)
    assert result["status"] == "invalid"
    assert "between" in result["error"] or "100" in result["error"]
