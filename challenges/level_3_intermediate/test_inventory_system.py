"""Pytest tests for Inventory Management System challenge."""
import subprocess
import sys

def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

class TestInventorySystem:
    """Tests for the inventory management system challenge."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_code_runs(self, player_code: str):
        """Code should execute without runtime errors."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

    def test_has_required_classes(self, player_code: str):
        """Code should define Item and Inventory classes."""
        assert "class Item" in player_code, "Define an 'Item' class"
        assert "class Inventory" in player_code, "Define an 'Inventory' class"
        assert "def solution" in player_code, "Define a 'solution' function"

    def test_item_class_initialization(self, player_code: str):
        """Item class should store name, quantity, and value."""
        test_code = f'''
{player_code}

# Test Item class
item = Item("sword", 1, 50)
print(f"name: {{item.name}}, quantity: {{item.quantity}}, value: {{item.value}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "name: sword" in stdout
        assert "quantity: 1" in stdout
        assert "value: 50" in stdout

    def test_item_get_total_value(self, player_code: str):
        """Item.get_total_value() should return quantity * value."""
        test_code = f'''
{player_code}

# Test get_total_value
item = Item("potion", 3, 10)
result = item.get_total_value()
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "30" in stdout

    def test_inventory_initialization(self, player_code: str):
        """Inventory should initialize with empty items list."""
        test_code = f'''
{player_code}

# Test Inventory initialization
inv = Inventory()
print(len(inv.items), end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "0" in stdout

    def test_add_item(self, player_code: str):
        """Inventory.add_item should create and store an Item."""
        test_code = f'''
{player_code}

# Test add_item
inv = Inventory()
inv.add_item("sword", 1, 50)
print(len(inv.items), inv.items[0].name, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "1" in stdout
        assert "sword" in stdout

    def test_get_total_value(self, player_code: str):
        """Inventory.get_total_value should sum all item values."""
        test_code = f'''
{player_code}

# Test get_total_value
inv = Inventory()
inv.add_item("sword", 1, 50)
inv.add_item("potion", 3, 10)
result = inv.get_total_value()
print(result, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "80" in stdout

    def test_list_items(self, player_code: str):
        """Inventory.list_items should return list of item names."""
        test_code = f'''
{player_code}

# Test list_items
inv = Inventory()
inv.add_item("sword", 1, 50)
inv.add_item("shield", 1, 30)
inv.add_item("potion", 5, 10)
result = inv.list_items()
print(",".join(result), end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "sword,shield,potion" in stdout

    def test_remove_item_success(self, player_code: str):
        """Inventory.remove_item should remove existing items."""
        test_code = f'''
{player_code}

# Test remove_item success
inv = Inventory()
inv.add_item("sword", 1, 50)
inv.add_item("potion", 3, 10)
result = inv.remove_item("potion")
print(f"removed: {{result}}, count: {{len(inv.items)}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "removed: True" in stdout
        assert "count: 1" in stdout

    def test_remove_item_failure(self, player_code: str):
        """Inventory.remove_item should return False for missing items."""
        test_code = f'''
{player_code}

# Test remove_item failure
inv = Inventory()
inv.add_item("sword", 1, 50)
result = inv.remove_item("missing")
print(f"removed: {{result}}", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "removed: False" in stdout

    def test_solution_basic_commands(self, player_code: str):
        """Solution should handle basic ADD and TOTAL commands."""
        test_code = f'''
{player_code}

# Test solution with basic commands
commands = ["ADD sword 1 50", "ADD potion 3 10", "TOTAL"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Added: sword" in stdout
        assert "Added: potion" in stdout
        assert "80" in stdout

    def test_solution_list_command(self, player_code: str):
        """Solution should handle LIST command."""
        test_code = f'''
{player_code}

# Test LIST command
commands = ["ADD sword 1 50", "ADD shield 1 30", "ADD potion 5 10", "LIST"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Added: sword" in stdout
        assert "Added: shield" in stdout
        assert "Added: potion" in stdout
        assert "sword,shield,potion" in stdout

    def test_solution_remove_commands(self, player_code: str):
        """Solution should handle REMOVE command."""
        test_code = f'''
{player_code}

# Test REMOVE commands
commands = ["ADD sword 1 50", "ADD potion 3 10", "REMOVE potion", "TOTAL", "LIST"]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "Added: sword" in stdout
        assert "Added: potion" in stdout
        assert "Removed: potion" in stdout
        assert "50" in stdout
        assert "sword" in stdout

    def test_solution_complex_scenario(self, player_code: str):
        """Solution should handle complex inventory scenarios."""
        test_code = f'''
{player_code}

# Test complex scenario
commands = [
    "ADD sword 2 50",
    "ADD potion 10 5",
    "ADD armor 1 100",
    "TOTAL",
    "LIST",
    "REMOVE potion",
    "TOTAL"
]
result = solution(commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        expected = [
            "Added: sword", "Added: potion", "Added: armor",
            "250", "sword,potion,armor", "Removed: potion", "200"
        ]
        for exp in expected:
            assert exp in stdout

    def test_solution_empty_inventory(self, player_code: str):
        """Solution should handle empty inventory operations."""
        test_code = f'''
{player_code}

# Test empty inventory
commands = ["TOTAL", "LIST"]
result = solution(commands)
for r in result:
    print(repr(r))
'''
        stdout, _, _ = run_player_code(test_code)
        assert "'0'" in stdout
        assert "''" in stdout

    def test_error_handling(self, player_code: str):
        """Solution should handle errors gracefully."""
        test_code = f'''
{player_code}

# Test error handling
try:
    # Try to create Item without required parameters
    item = Item()
    print("no error", end="")
except TypeError:
    print("type error caught", end="")
'''
        stdout, _, _ = run_player_code(test_code)
        # Should catch TypeError or handle it appropriately
        assert "type error caught" in stdout or "no error" in stdout
