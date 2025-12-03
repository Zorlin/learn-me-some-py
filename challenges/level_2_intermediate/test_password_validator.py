"""
Tests for Password Strength Validator challenge.

Validates that the learner:
1. Checks password length (minimum 8 characters)
2. Checks for uppercase letters
3. Checks for lowercase letters
4. Checks for digits
5. Checks for special characters
6. Returns "strong" or "weak" appropriately
7. Provides specific reasons for weak passwords

PHILOSOPHY: Test the solution function with command lists.
"""

import pytest


def test_strong_password(player_code):
    """Test a strong password that meets all requirements."""
    solution = extract_solution(player_code)
    commands = ["CHECK Password123!", "REASON Password123!"]
    result = solution(commands)
    assert result == ["strong", "valid"]


def test_weak_too_short(player_code):
    """Test password that is too short."""
    solution = extract_solution(player_code)
    commands = ["CHECK Pass1!", "REASON Pass1!"]
    result = solution(commands)
    assert result == ["weak", "too_short"]


def test_weak_no_uppercase(player_code):
    """Test password with no uppercase letters."""
    solution = extract_solution(player_code)
    commands = ["CHECK password123!", "REASON password123!"]
    result = solution(commands)
    assert result == ["weak", "no_uppercase"]


def test_weak_no_digit(player_code):
    """Test password with no digits."""
    solution = extract_solution(player_code)
    commands = ["CHECK Password!", "REASON Password!"]
    result = solution(commands)
    assert result == ["weak", "no_digit"]


def test_weak_no_special(player_code):
    """Test password with no special characters."""
    solution = extract_solution(player_code)
    commands = ["CHECK Password123", "REASON Password123"]
    result = solution(commands)
    assert result == ["weak", "no_special"]


def test_multiple_checks(player_code):
    """Test multiple password checks in sequence."""
    solution = extract_solution(player_code)
    commands = ["CHECK Abc123!@#", "CHECK weak", "CHECK NoDigits!"]
    result = solution(commands)
    assert result == ["strong", "weak", "weak"]


def extract_solution(player_code: str):
    """Extract the solution function from player code."""
    namespace = {}
    exec(player_code, namespace)
    return namespace['solution']
