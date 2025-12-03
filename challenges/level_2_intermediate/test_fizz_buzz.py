"""
Tests for FizzBuzz challenge.

Validates that the learner:
1. Returns "Fizz" for multiples of 3
2. Returns "Buzz" for multiples of 5
3. Returns "FizzBuzz" for multiples of both 3 and 5
4. Returns the number as string otherwise
5. Generates correct sequence from 1 to N

PHILOSOPHY: Test the solution function with different N values.
"""

import pytest


def test_fizzbuzz_15(player_code):
    """Test FizzBuzz from 1 to 15."""
    solution = extract_solution(player_code)
    result = solution(15)
    expected = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]
    assert result == expected


def test_fizzbuzz_5(player_code):
    """Test FizzBuzz from 1 to 5."""
    solution = extract_solution(player_code)
    result = solution(5)
    expected = ["1", "2", "Fizz", "4", "Buzz"]
    assert result == expected


def test_fizzbuzz_3(player_code):
    """Test FizzBuzz from 1 to 3."""
    solution = extract_solution(player_code)
    result = solution(3)
    expected = ["1", "2", "Fizz"]
    assert result == expected


def test_fizzbuzz_20(player_code):
    """Test FizzBuzz from 1 to 20."""
    solution = extract_solution(player_code)
    result = solution(20)
    expected = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz", "16", "17", "Fizz", "19", "Buzz"]
    assert result == expected


def extract_solution(player_code: str):
    """Extract the solution function from player code."""
    namespace = {}
    exec(player_code, namespace)
    return namespace['solution']
