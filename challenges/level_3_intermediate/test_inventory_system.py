"""
Tests for Inventory Management System.
"""

import subprocess
import sys
import json


def run_player_code(code: str, input_data) -> list:
    """Run player code with given input and return output."""
    full_code = f'''
{code}

import json
input_data = {repr(input_data)}
result = solution(input_data)
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


def test_has_item_class(player_code):
    """Check that code defines an Item class."""
    assert "class Item" in player_code, "Define an 'Item' class"


def test_has_inventory_class(player_code):
    """Check that code defines an Inventory class."""
    assert "class Inventory" in player_code, "Define an 'Inventory' class"


def test_basic_inventory(player_code):
    """Test basic inventory operations."""
    commands = ["ADD sword 1 50", "ADD potion 3 10", "TOTAL"]
    result = run_player_code(player_code, commands)
    assert result == ["Added: sword", "Added: potion", "80"], \
        f"Expected ['Added: sword', 'Added: potion', '80'], got {result}"


def test_list_items(player_code):
    """Test listing inventory items."""
    commands = ["ADD sword 1 50", "ADD shield 1 30", "ADD potion 5 10", "LIST"]
    result = run_player_code(player_code, commands)
    assert result == ["Added: sword", "Added: shield", "Added: potion", "sword,shield,potion"], \
        f"Expected ['Added: sword', 'Added: shield', 'Added: potion', 'sword,shield,potion'], got {result}"


def test_remove_item(player_code):
    """Test removing an item from inventory."""
    commands = ["ADD sword 1 50", "ADD potion 3 10", "REMOVE potion", "TOTAL", "LIST"]
    result = run_player_code(player_code, commands)
    assert result == ["Added: sword", "Added: potion", "Removed: potion", "50", "sword"], \
        f"Expected ['Added: sword', 'Added: potion', 'Removed: potion', '50', 'sword'], got {result}"


def test_remove_missing(player_code):
    """Test removing a missing item."""
    commands = ["ADD sword 1 50", "REMOVE missing"]
    result = run_player_code(player_code, commands)
    assert result == ["Added: sword", "Not found"], \
        f"Expected ['Added: sword', 'Not found'], got {result}"


def test_complex_inventory(player_code):
    """Test complex inventory operations."""
    commands = [
        "ADD sword 2 50",
        "ADD potion 10 5",
        "ADD armor 1 100",
        "TOTAL",
        "LIST",
        "REMOVE potion",
        "TOTAL"
    ]
    expected = [
        "Added: sword", "Added: potion", "Added: armor",
        "250", "sword,potion,armor", "Removed: potion", "200"
    ]
    result = run_player_code(player_code, commands)
    assert result == expected, f"Expected {expected}, got {result}"


def test_empty_inventory(player_code):
    """Test operations on empty inventory."""
    commands = ["TOTAL", "LIST"]
    result = run_player_code(player_code, commands)
    assert result == ["0", ""], f"Expected ['0', ''], got {result}"
