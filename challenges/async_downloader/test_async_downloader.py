"""
Tests for Async File Downloader challenge.
"""

import subprocess
import sys
import json
import time

def run_player_code(code: str, input_data):
    """Execute player code with async support."""
    full_code = f'''
import asyncio
{code}

input_data = {repr(input_data)}
result = asyncio.run(solution(input_data))
print(json.dumps(result, default=str))
'''
    result = subprocess.run([sys.executable, "-c", full_code], capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        raise RuntimeError(f"Code failed: {result.stderr}")
    return json.loads(result.stdout.strip())

def test_has_solution_function(player_code):
    assert "async def solution" in player_code

def test_all_succeed(player_code):
    input_data = [
        {"url": "a.txt", "duration": 0.01, "will_fail": False},
        {"url": "b.txt", "duration": 0.01, "will_fail": False},
        {"url": "c.txt", "duration": 0.01, "will_fail": False}
    ]
    expected = [
        {"url": "a.txt", "status": "success"},
        {"url": "b.txt", "status": "success"},
        {"url": "c.txt", "status": "success"}
    ]
    
    start = time.time()
    result = run_player_code(player_code, input_data)
    duration = time.time() - start
    
    assert result == expected
    assert duration < 0.05, "Must be concurrent, not sequential"

def test_some_fail(player_code):
    input_data = [
        {"url": "x.txt", "duration": 0.01, "will_fail": False},
        {"url": "y.txt", "duration": 0.01, "will_fail": True},
        {"url": "z.txt", "duration": 0.01, "will_fail": False}
    ]
    expected = [
        {"url": "x.txt", "status": "success"},
        {"url": "y.txt", "status": "failed"},
        {"url": "z.txt", "status": "success"}
    ]
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_concurrent_not_sequential(player_code):
    input_data = [
        {"url": "1.txt", "duration": 0.05, "will_fail": False},
        {"url": "2.txt", "duration": 0.05, "will_fail": False},
        {"url": "3.txt", "duration": 0.05, "will_fail": False}
    ]
    expected = [
        {"url": "1.txt", "status": "success"},
        {"url": "2.txt", "status": "success"},
        {"url": "3.txt", "status": "success"}
    ]
    
    start = time.time()
    result = run_player_code(player_code, input_data)
    duration = time.time() - start
    
    assert result == expected
    assert duration < 0.08, f"Sequential would be 0.15s, got {duration}s - must be concurrent"

def test_single_file(player_code):
    input_data = [{"url": "solo.txt", "duration": 0.01, "will_fail": False}]
    expected = [{"url": "solo.txt", "status": "success"}]
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_all_fail(player_code):
    input_data = [
        {"url": "bad1.txt", "duration": 0.01, "will_fail": True},
        {"url": "bad2.txt", "duration": 0.01, "will_fail": True}
    ]
    expected = [
        {"url": "bad1.txt", "status": "failed"},
        {"url": "bad2.txt", "status": "failed"}
    ]
    result = run_player_code(player_code, input_data)
    assert result == expected
