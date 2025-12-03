"""
Tests for Code Analyzer with AST challenge.
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
    input_data = """
def hello():
    return "world"
"""
    expected = {
        "functions": [{"name": "hello", "line": 2, "args": 0, "complexity": 1}],
        "imports": [],
        "dangerous": []
    }
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_multiple_functions(player_code):
    input_data = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""
    expected = {
        "functions": [
            {"name": "add", "line": 2, "args": 2, "complexity": 1},
            {"name": "multiply", "line": 5, "args": 2, "complexity": 1}
        ],
        "imports": [],
        "dangerous": []
    }
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_complex_function(player_code):
    input_data = """
def categorize(value):
    if value < 0:
        return "negative"
    elif value == 0:
        return "zero"
    else:
        return "positive"
"""
    expected = {
        "functions": [{"name": "categorize", "line": 2, "args": 1, "complexity": 3}],
        "imports": [],
        "dangerous": []
    }
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_nested_conditions(player_code):
    input_data = """
def check(x, y):
    if x > 0:
        if y > 0:
            return "both positive"
    return "not both positive"
"""
    expected = {
        "functions": [{"name": "check", "line": 2, "args": 2, "complexity": 3}],
        "imports": [],
        "dangerous": []
    }
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_imports_detected(player_code):
    input_data = """
import os
import sys
from pathlib import Path

def work():
    pass
"""
    expected = {
        "functions": [{"name": "work", "line": 5, "args": 0, "complexity": 1}],
        "imports": ["os", "sys", "pathlib"],
        "dangerous": []
    }
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_dangerous_patterns(player_code):
    input_data = """
def unsafe():
    eval(user_input)
    exec(code)
    return result
"""
    expected = {
        "functions": [{"name": "unsafe", "line": 2, "args": 0, "complexity": 1}],
        "imports": [],
        "dangerous": ["eval", "exec"]
    }
    result = run_player_code(player_code, input_data)
    # Check that dangerous contains at least eval and exec
    assert "eval" in result["dangerous"]
    assert "exec" in result["dangerous"]

def test_realistic_code(player_code):
    input_data = """
import json
import requests

def fetch_data(url, timeout=30):
    if not url:
        raise ValueError("URL required")

    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None
    except Exception:
        return None
"""
    expected = {
        "functions": [{"name": "fetch_data", "line": 4, "args": 2, "complexity": 5}],
        "imports": ["json", "requests"],
        "dangerous": []
    }
    result = run_player_code(player_code, input_data)
    assert result == expected
