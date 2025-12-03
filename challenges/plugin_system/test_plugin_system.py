"""
Tests for Plugin System with Dynamic Imports challenge.
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

def test_simple_function(player_code):
    input_data = {
        "plugin_code": "def greet(name): return f'Hello, {name}!'",
        "command": "greet",
        "args": ["World"]
    }
    expected = {"result": "Hello, World!"}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_math_function(player_code):
    input_data = {
        "plugin_code": "def add(a, b): return a + b",
        "command": "add",
        "args": [5, 3]
    }
    expected = {"result": 8}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_function_not_found(player_code):
    input_data = {
        "plugin_code": "def foo(): return 42",
        "command": "bar",
        "args": []
    }
    expected = {"error": "function not found"}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_execution_error(player_code):
    input_data = {
        "plugin_code": "def divide(a, b): return a / b",
        "command": "divide",
        "args": [10, 0]
    }
    expected = {"error": "execution failed"}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_multiple_functions(player_code):
    input_data = {
        "plugin_code": "def add(a, b): return a + b\ndef sub(a, b): return a - b",
        "command": "sub",
        "args": [10, 3]
    }
    expected = {"result": 7}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_no_args_function(player_code):
    input_data = {
        "plugin_code": "def get_answer(): return 42",
        "command": "get_answer",
        "args": []
    }
    expected = {"result": 42}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_complex_logic(player_code):
    input_data = {
        "plugin_code": """
def process(items):
    return [x * 2 for x in items if x > 0]
""",
        "command": "process",
        "args": [[-1, 2, -3, 4, 5]]
    }
    expected = {"result": [4, 8, 10]}
    result = run_player_code(player_code, input_data)
    assert result == expected
