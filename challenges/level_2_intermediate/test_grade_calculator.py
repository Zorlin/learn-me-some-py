"""
Tests for Grade Calculator challenge.

Validates that the learner:
1. Tracks grades by category with weights
2. Calculates averages correctly
3. Computes weighted final grades
4. Converts numeric grades to letter grades

PHILOSOPHY: Test the solution function with command lists.
"""

import pytest


def test_basic_grading(player_code):
    """Test adding grades and calculating category average."""
    solution = extract_solution(player_code)
    commands = ["ADD homework 20 85", "ADD homework 20 90", "AVERAGE homework"]
    result = solution(commands)
    assert result == ["Added homework: 85", "Added homework: 90", "87.5"]


def test_multiple_categories(player_code):
    """Test multiple categories with different averages."""
    solution = extract_solution(player_code)
    commands = ["ADD homework 30 80", "ADD exam 70 90", "AVERAGE homework", "AVERAGE exam"]
    result = solution(commands)
    assert result == ["Added homework: 80", "Added exam: 90", "80.0", "90.0"]


def test_final_grade_calculation(player_code):
    """Test weighted final grade calculation."""
    solution = extract_solution(player_code)
    commands = ["ADD homework 40 80", "ADD exam 60 90", "FINAL"]
    result = solution(commands)
    assert result == ["Added homework: 80", "Added exam: 90", "86.0"]


def test_letter_grades(player_code):
    """Test letter grade conversion."""
    solution = extract_solution(player_code)
    commands = ["ADD test 100 95", "LETTER"]
    result = solution(commands)
    assert result == ["Added test: 95", "A"]


def test_complete_workflow(player_code):
    """Test complete grading workflow with multiple operations."""
    solution = extract_solution(player_code)
    commands = [
        "ADD homework 20 85",
        "ADD homework 20 90",
        "ADD quiz 30 88",
        "ADD exam 50 92",
        "AVERAGE homework",
        "FINAL",
        "LETTER"
    ]
    result = solution(commands)
    assert result == ["Added homework: 85", "Added homework: 90", "Added quiz: 88", "Added exam: 92", "87.5", "90.4", "A"]


def extract_solution(player_code: str):
    """Extract the solution function from player code."""
    namespace = {}
    exec(player_code, namespace)
    return namespace['solution']
