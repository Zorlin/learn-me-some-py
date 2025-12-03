"""
Tests for Build a Test Suite challenge.

The learner writes their own test function to validate word_stats implementations.
"""

import subprocess
import sys


def run_player_tests(player_code: str, impl_name: str) -> str:
    """Run player's test function against an implementation."""
    impl_code = '''
def correct_word_stats(text):
    if not text.strip():
        return {"word_count": 0, "char_count": 0, "avg_word_length": 0.0, "longest_word": ""}
    words = text.split()
    word_count = len(words)
    char_count = sum(len(w) for w in words)
    avg_word_length = round(char_count / word_count, 2) if word_count > 0 else 0.0
    longest_word = max(words, key=len) if words else ""
    return {"word_count": word_count, "char_count": char_count, "avg_word_length": avg_word_length, "longest_word": longest_word}

def buggy_word_count(text):
    words = text.split() if text.strip() else []
    return {"word_count": len(text), "char_count": sum(len(w) for w in words), "avg_word_length": round(sum(len(w) for w in words) / len(words), 2) if words else 0.0, "longest_word": max(words, key=len) if words else ""}

def buggy_char_count(text):
    words = text.split() if text.strip() else []
    return {"word_count": len(words), "char_count": len(text), "avg_word_length": round(sum(len(w) for w in words) / len(words), 2) if words else 0.0, "longest_word": max(words, key=len) if words else ""}

def buggy_average(text):
    words = text.split() if text.strip() else []
    return {"word_count": len(words), "char_count": sum(len(w) for w in words), "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0.0, "longest_word": max(words, key=len) if words else ""}

def buggy_edge_cases(text):
    words = text.split()
    if not words:
        return {"word_count": 0, "char_count": 0, "avg_word_length": 0.0, "longest_word": ""}
    return {"word_count": len(words), "char_count": sum(len(w) for w in words), "avg_word_length": round(sum(len(w) for w in words) / len(words), 2), "longest_word": words[0]}  # BUG: returns first word not longest
'''

    full_code = f'''
{impl_code}

{player_code}

impl = {{"correct": correct_word_stats, "buggy_word_count": buggy_word_count, "buggy_char_count": buggy_char_count, "buggy_average": buggy_average, "buggy_edge_cases": buggy_edge_cases}}

try:
    solution(impl["{impl_name}"])
    print("PASS")
except AssertionError as e:
    print("FAIL")
except Exception as e:
    print("FAIL")
'''

    result = subprocess.run(
        [sys.executable, "-c", full_code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout.strip()


def test_has_solution_function(player_code):
    """Check that code defines a solution function."""
    assert "def solution" in player_code, "Define a 'solution' function"


def test_catches_correct_implementation(player_code):
    """Your tests should pass for correct implementation."""
    result = run_player_tests(player_code, "correct")
    assert result == "PASS", "Your tests should pass for a correct implementation"


def test_catches_wrong_word_count(player_code):
    """Should catch incorrect word counting."""
    result = run_player_tests(player_code, "buggy_word_count")
    assert result == "FAIL", "Your tests should catch incorrect word counting"


def test_catches_wrong_char_count(player_code):
    """Should catch incorrect character counting."""
    result = run_player_tests(player_code, "buggy_char_count")
    assert result == "FAIL", "Your tests should catch incorrect character counting"


def test_catches_wrong_average(player_code):
    """Should catch incorrect average calculation."""
    result = run_player_tests(player_code, "buggy_average")
    assert result == "FAIL", "Your tests should catch incorrect average rounding"


def test_catches_edge_case_bugs(player_code):
    """Should catch bugs in edge case handling."""
    result = run_player_tests(player_code, "buggy_edge_cases")
    assert result == "FAIL", "Your tests should catch edge case bugs"
