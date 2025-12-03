"""
Tests for Shopping List Manager challenge.

Validates that the learner:
1. Can add items to a shopping list
2. Can remove items from the list
3. Can check if items are on the list
4. Can count items
5. Can list all items

PHILOSOPHY: Test the solution function with command lists.
"""

import pytest


def test_basic_operations(player_code):
    """Test adding items and checking them."""
    solution = extract_solution(player_code)
    commands = ["ADD milk", "ADD eggs", "CHECK milk", "CHECK bread", "COUNT"]
    result = solution(commands)
    assert result == ["Added milk", "Added eggs", "yes", "no", "2"]


def test_remove_items(player_code):
    """Test removing an item from the list."""
    solution = extract_solution(player_code)
    commands = ["ADD milk", "ADD eggs", "REMOVE milk", "CHECK milk", "COUNT"]
    result = solution(commands)
    assert result == ["Added milk", "Added eggs", "Removed milk", "no", "1"]


def test_remove_nonexistent(player_code):
    """Test removing an item that doesn't exist."""
    solution = extract_solution(player_code)
    commands = ["ADD milk", "REMOVE eggs"]
    result = solution(commands)
    assert result == ["Added milk", "Item not found"]


def test_list_items(player_code):
    """Test listing all items."""
    solution = extract_solution(player_code)
    commands = ["ADD milk", "ADD eggs", "ADD bread", "LIST"]
    result = solution(commands)
    assert result == ["Added milk", "Added eggs", "Added bread", "milk,eggs,bread"]


def test_empty_list(player_code):
    """Test operations on an empty list."""
    solution = extract_solution(player_code)
    commands = ["COUNT", "LIST"]
    result = solution(commands)
    assert result == ["0", ""]


def extract_solution(player_code: str):
    """Extract the solution function from player code."""
    namespace = {}
    exec(player_code, namespace)
    return namespace['solution']
