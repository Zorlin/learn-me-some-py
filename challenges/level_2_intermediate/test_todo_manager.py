"""
Tests for TODO List Manager challenge.

Validates that the learner:
1. Can add tasks to a list
2. Can complete tasks by number
3. Can list all tasks with status
4. Can count pending tasks
5. Can clear completed tasks

PHILOSOPHY: Test the solution function with command lists.
"""

import pytest


def test_basic_todo(player_code):
    """Test adding tasks and listing them."""
    solution = extract_solution(player_code)
    commands = ["ADD Buy milk", "ADD Write code", "LIST"]
    result = solution(commands)
    assert result == ["Added: Buy milk", "Added: Write code", "1. [ ] Buy milk\n2. [ ] Write code"]


def test_complete_task(player_code):
    """Test completing a task."""
    solution = extract_solution(player_code)
    commands = ["ADD Task 1", "ADD Task 2", "COMPLETE 1", "LIST"]
    result = solution(commands)
    assert result == ["Added: Task 1", "Added: Task 2", "Completed: Task 1", "1. [X] Task 1\n2. [ ] Task 2"]


def test_invalid_complete(player_code):
    """Test completing a non-existent task."""
    solution = extract_solution(player_code)
    commands = ["ADD Task 1", "COMPLETE 5"]
    result = solution(commands)
    assert result == ["Added: Task 1", "Invalid task"]


def test_pending_count(player_code):
    """Test counting pending tasks."""
    solution = extract_solution(player_code)
    commands = ["ADD Task 1", "ADD Task 2", "COMPLETE 1", "PENDING"]
    result = solution(commands)
    assert result == ["Added: Task 1", "Added: Task 2", "Completed: Task 1", "1"]


def test_clear_completed(player_code):
    """Test clearing completed tasks."""
    solution = extract_solution(player_code)
    commands = ["ADD Task 1", "ADD Task 2", "COMPLETE 1", "CLEAR", "LIST"]
    result = solution(commands)
    assert result == ["Added: Task 1", "Added: Task 2", "Completed: Task 1", "Cleared 1 tasks", "1. [ ] Task 2"]


def test_empty_list(player_code):
    """Test operations on empty list."""
    solution = extract_solution(player_code)
    commands = ["LIST", "PENDING"]
    result = solution(commands)
    assert result == ["", "0"]


def extract_solution(player_code: str):
    """Extract the solution function from player code."""
    namespace = {}
    exec(player_code, namespace)
    return namespace['solution']
