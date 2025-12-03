"""
Tests for File Content Analyzer.
"""

import subprocess
import sys
import json


def run_player_code(code: str, file_contents: str, commands: list) -> list:
    """Run player code with given input and return output."""
    full_code = f'''
{code}

import json
file_contents = {repr(file_contents)}
commands = {repr(commands)}
result = solution(file_contents, commands)
print(json.dumps(result))
'''
    result = subprocess.run(
        [sys.executable, "-c", full_code],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode != 0:
        raise RuntimeError(f"Code failed: {result.stderr}")
    return json.loads(result.stdout.strip())


def test_has_solution_function(player_code):
    """Check that code defines a solution function."""
    assert "def solution" in player_code, "Define a 'solution' function"


def test_basic_analysis(player_code):
    """Test basic file analysis - lines, words, chars."""
    file_contents = "Hello world!\nHello Python.\nWorld of code."
    commands = ["LINES", "WORDS", "CHARS"]
    result = run_player_code(player_code, file_contents, commands)
    assert result == ["3", "7", "41"], f"Expected ['3', '7', '41'], got {result}"


def test_longest_word(player_code):
    """Test finding the longest word."""
    file_contents = "The quick brown fox jumps"
    commands = ["LONGEST"]
    result = run_player_code(player_code, file_contents, commands)
    assert result == ["brown"], f"Expected ['brown'], got {result}"


def test_most_frequent(player_code):
    """Test finding the most frequent word."""
    file_contents = "hello world hello python world world"
    commands = ["FREQUENT"]
    result = run_player_code(player_code, file_contents, commands)
    assert result == ["world"], f"Expected ['world'], got {result}"


def test_case_insensitive_frequent(player_code):
    """Test case-insensitive frequency counting."""
    file_contents = "Hello HELLO hello World"
    commands = ["FREQUENT"]
    result = run_player_code(player_code, file_contents, commands)
    assert result == ["hello"], f"Expected ['hello'], got {result}"


def test_complete_analysis(player_code):
    """Test complete file analysis."""
    file_contents = "Python is great.\nPython is powerful.\nI love Python!"
    commands = ["LINES", "WORDS", "LONGEST", "FREQUENT"]
    result = run_player_code(player_code, file_contents, commands)
    assert result == ["3", "9", "powerful", "python"], \
        f"Expected ['3', '9', 'powerful', 'python'], got {result}"


def test_empty_file(player_code):
    """Test analysis of empty file."""
    file_contents = ""
    commands = ["LINES", "WORDS", "CHARS"]
    result = run_player_code(player_code, file_contents, commands)
    assert result == ["0", "0", "0"], f"Expected ['0', '0', '0'], got {result}"
