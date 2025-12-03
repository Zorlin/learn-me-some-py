"""
Tests for Task Scheduler with DAG Dependencies challenge.
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

def test_simple_chain(player_code):
    input_data = {"a": [], "b": ["a"], "c": ["b"]}
    expected = ["a", "b", "c"]
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_independent_tasks(player_code):
    input_data = {"x": [], "y": [], "z": []}
    result = run_player_code(player_code, input_data)
    # Any ordering is valid for independent tasks
    assert set(result) == {"x", "y", "z"}
    assert len(result) == 3

def test_diamond_dependency(player_code):
    input_data = {"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}
    result = run_player_code(player_code, input_data)
    
    # Check that dependencies are respected
    assert result.index("a") < result.index("b")
    assert result.index("a") < result.index("c")
    assert result.index("b") < result.index("d")
    assert result.index("c") < result.index("d")

def test_simple_cycle(player_code):
    input_data = {"a": ["b"], "b": ["a"]}
    result = run_player_code(player_code, input_data)
    assert result == "CYCLE"

def test_complex_cycle(player_code):
    # Note: This test has a cycle (b depends on e, e depends on b indirectly)
    input_data = {"a": [], "b": ["a", "e"], "c": ["b"], "d": ["c"], "e": ["d"]}
    result = run_player_code(player_code, input_data)
    assert result == "CYCLE"

def test_realistic_build(player_code):
    input_data = {
        "compile": ["parse"],
        "parse": [],
        "link": ["compile", "optimize"],
        "optimize": ["compile"],
        "package": ["link", "test"],
        "test": ["compile"]
    }
    result = run_player_code(player_code, input_data)
    
    # Check that dependencies are respected
    assert result.index("parse") < result.index("compile")
    assert result.index("compile") < result.index("optimize")
    assert result.index("compile") < result.index("test")
    assert result.index("compile") < result.index("link")
    assert result.index("optimize") < result.index("link")
    assert result.index("test") < result.index("package")
    assert result.index("link") < result.index("package")
