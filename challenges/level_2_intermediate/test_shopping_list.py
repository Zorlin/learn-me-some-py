"""
Tests for Shopping List Manager challenge (Multi-Stage).

Stages 1-5: Test individual functions directly (add, count, check, remove, list_items)
Stage 6: Test the command handler (solution)

Each stage builds on the previous - learners implement one function at a time,
then wire them together in the final stage.
"""

import pytest


def extract_functions(player_code: str) -> dict:
    """Extract all functions from player code."""
    namespace = {'shopping_list': []}  # Provide the shared list
    exec(player_code, namespace)
    return namespace


def reset_list(namespace: dict):
    """Clear the shopping list between tests."""
    namespace['shopping_list'].clear()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: Add Items
# ═══════════════════════════════════════════════════════════════════════════

class TestStage1:
    """Stage 1: add(item) function."""

    def test_stage1_add_returns_message(self, player_code):
        """add() returns 'Added {item}'."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['add']("milk")
        assert result == "Added milk", f"Expected 'Added milk', got {result!r}"

    def test_stage1_add_actually_adds(self, player_code):
        """add() actually puts item in the list."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("eggs")
        assert "eggs" in ns['shopping_list'], "Item should be in shopping_list after add()"

    def test_stage1_add_multiple(self, player_code):
        """Can add multiple items."""
        ns = extract_functions(player_code)
        reset_list(ns)
        r1 = ns['add']("milk")
        r2 = ns['add']("bread")
        assert r1 == "Added milk"
        assert r2 == "Added bread"
        assert len(ns['shopping_list']) == 2


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: Count Items
# ═══════════════════════════════════════════════════════════════════════════

class TestStage2:
    """Stage 2: count() function."""

    def test_stage2_count_empty(self, player_code):
        """count() returns '0' for empty list."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['count']()
        assert result == "0", f"Expected '0', got {result!r}"

    def test_stage2_count_after_add(self, player_code):
        """count() returns correct count after adding items."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        ns['add']("eggs")
        result = ns['count']()
        assert result == "2", f"Expected '2', got {result!r}"

    def test_stage2_count_returns_string(self, player_code):
        """count() returns a string, not an int."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        result = ns['count']()
        assert isinstance(result, str), f"count() should return a string, got {type(result)}"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 3: Check Items
# ═══════════════════════════════════════════════════════════════════════════

class TestStage3:
    """Stage 3: check(item) function."""

    def test_stage3_check_found(self, player_code):
        """check() returns 'yes' when item exists."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        result = ns['check']("milk")
        assert result == "yes", f"Expected 'yes', got {result!r}"

    def test_stage3_check_not_found(self, player_code):
        """check() returns 'no' when item doesn't exist."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        result = ns['check']("bread")
        assert result == "no", f"Expected 'no', got {result!r}"

    def test_stage3_check_empty_list(self, player_code):
        """check() returns 'no' on empty list."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['check']("anything")
        assert result == "no"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 4: Remove Items
# ═══════════════════════════════════════════════════════════════════════════

class TestStage4:
    """Stage 4: remove(item) function."""

    def test_stage4_remove_existing(self, player_code):
        """remove() returns 'Removed {item}' when found."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        result = ns['remove']("milk")
        assert result == "Removed milk", f"Expected 'Removed milk', got {result!r}"

    def test_stage4_remove_actually_removes(self, player_code):
        """remove() actually removes from the list."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        ns['remove']("milk")
        assert "milk" not in ns['shopping_list'], "Item should be gone after remove()"

    def test_stage4_remove_not_found(self, player_code):
        """remove() returns 'Item not found' when item doesn't exist."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        result = ns['remove']("bread")
        assert result == "Item not found", f"Expected 'Item not found', got {result!r}"

    def test_stage4_remove_doesnt_crash(self, player_code):
        """remove() on empty list doesn't crash."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['remove']("anything")
        assert result == "Item not found"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 5: List Items
# ═══════════════════════════════════════════════════════════════════════════

class TestStage5:
    """Stage 5: list_items() function."""

    def test_stage5_list_empty(self, player_code):
        """list_items() returns '' for empty list."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['list_items']()
        assert result == "", f"Expected '', got {result!r}"

    def test_stage5_list_single(self, player_code):
        """list_items() returns single item without comma."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        result = ns['list_items']()
        assert result == "milk", f"Expected 'milk', got {result!r}"

    def test_stage5_list_multiple(self, player_code):
        """list_items() returns comma-separated items."""
        ns = extract_functions(player_code)
        reset_list(ns)
        ns['add']("milk")
        ns['add']("eggs")
        ns['add']("bread")
        result = ns['list_items']()
        assert result == "milk,eggs,bread", f"Expected 'milk,eggs,bread', got {result!r}"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 6: Command Handler
# ═══════════════════════════════════════════════════════════════════════════

class TestStage6:
    """Stage 6: solution() command handler - wire it all together!"""

    def test_stage6_add_command(self, player_code):
        """solution() handles ADD command."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['solution'](["ADD milk", "ADD eggs"])
        assert result == ["Added milk", "Added eggs"]

    def test_stage6_count_command(self, player_code):
        """solution() handles COUNT command."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['solution'](["ADD milk", "ADD eggs", "COUNT"])
        assert result == ["Added milk", "Added eggs", "2"]

    def test_stage6_check_command(self, player_code):
        """solution() handles CHECK command."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['solution'](["ADD milk", "CHECK milk", "CHECK bread"])
        assert result == ["Added milk", "yes", "no"]

    def test_stage6_remove_command(self, player_code):
        """solution() handles REMOVE command."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['solution'](["ADD milk", "REMOVE milk", "REMOVE bread"])
        assert result == ["Added milk", "Removed milk", "Item not found"]

    def test_stage6_list_command(self, player_code):
        """solution() handles LIST command."""
        ns = extract_functions(player_code)
        reset_list(ns)
        result = ns['solution'](["ADD milk", "ADD eggs", "LIST"])
        assert result == ["Added milk", "Added eggs", "milk,eggs"]

    def test_stage6_full_shopping_trip(self, player_code):
        """Complete shopping workflow using command handler."""
        ns = extract_functions(player_code)
        reset_list(ns)
        commands = [
            "ADD milk",
            "ADD eggs",
            "ADD bread",
            "CHECK butter",
            "ADD butter",
            "COUNT",
            "REMOVE eggs",
            "LIST",
            "COUNT"
        ]
        expected = [
            "Added milk",
            "Added eggs",
            "Added bread",
            "no",
            "Added butter",
            "4",
            "Removed eggs",
            "milk,bread,butter",
            "3"
        ]
        result = ns['solution'](commands)
        assert result == expected
