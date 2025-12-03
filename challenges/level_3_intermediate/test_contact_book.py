"""
Tests for Contact Book Manager challenge.

Validates that the learner:
1. Can add contacts with name, phone, and email
2. Can find contacts by name
3. Can search contacts by partial name match
4. Can count total contacts
5. Can delete contacts

PHILOSOPHY: Test the solution function with command lists.
"""

import pytest


def test_basic_contacts(player_code):
    """Test adding a contact and finding it."""
    solution = extract_solution(player_code)
    commands = ["ADD Alice 555-1234 alice@email.com", "FIND Alice", "COUNT"]
    result = solution(commands)
    assert result == ["Added: Alice", "555-1234,alice@email.com", "1"]


def test_multiple_contacts(player_code):
    """Test adding multiple contacts."""
    solution = extract_solution(player_code)
    commands = [
        "ADD Alice 555-1234 alice@email.com",
        "ADD Bob 555-5678 bob@email.com",
        "ADD Charlie 555-9999 charlie@email.com",
        "COUNT"
    ]
    result = solution(commands)
    assert result == ["Added: Alice", "Added: Bob", "Added: Charlie", "3"]


def test_find_missing(player_code):
    """Test finding a contact that doesn't exist."""
    solution = extract_solution(player_code)
    commands = ["ADD Alice 555-1234 alice@email.com", "FIND Bob"]
    result = solution(commands)
    assert result == ["Added: Alice", "Not found"]


def test_search_contacts(player_code):
    """Test searching contacts by partial name."""
    solution = extract_solution(player_code)
    commands = [
        "ADD Alice 555-1234 alice@email.com",
        "ADD Alicia 555-5678 alicia@email.com",
        "ADD Bob 555-9999 bob@email.com",
        "SEARCH Ali"
    ]
    result = solution(commands)
    assert result == ["Added: Alice", "Added: Alicia", "Added: Bob", "Alice\nAlicia"]


def test_delete_contact(player_code):
    """Test deleting a contact."""
    solution = extract_solution(player_code)
    commands = ["ADD Alice 555-1234 alice@email.com", "DELETE Alice", "COUNT", "FIND Alice"]
    result = solution(commands)
    assert result == ["Added: Alice", "Deleted: Alice", "0", "Not found"]


def test_empty_search(player_code):
    """Test searching when no matches found."""
    solution = extract_solution(player_code)
    commands = ["ADD Alice 555-1234 alice@email.com", "SEARCH xyz"]
    result = solution(commands)
    assert result == ["Added: Alice", ""]


def extract_solution(player_code: str):
    """Extract the solution function from player code."""
    namespace = {}
    exec(player_code, namespace)
    return namespace['solution']
