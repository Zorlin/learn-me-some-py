"""
Tests for ORM Lite with Metaclasses challenge.
"""

import subprocess
import sys
import json

def run_player_code(code: str, input_data):
    """Execute player code."""
    full_code = f'''
{code}

import json
input_data = {repr(input_data)}
result = solution(input_data)
print(json.dumps(result))
'''
    result = subprocess.run([sys.executable, "-c", full_code], capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        raise RuntimeError(f"Code failed: {result.stderr}")
    return json.loads(result.stdout.strip())

def test_has_solution_function(player_code):
    assert "def solution" in player_code

def test_has_metaclass(player_code):
    assert "class Model(type)" in player_code or "class Model(metaclass=" in player_code

def test_create_table_simple(player_code):
    input_data = {
        "operation": "create_table",
        "class_name": "User",
        "fields": {"name": "TEXT", "age": "INTEGER"}
    }
    expected = "CREATE TABLE User (name TEXT, age INTEGER)"
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_create_table_multiple_fields(player_code):
    input_data = {
        "operation": "create_table",
        "class_name": "Product",
        "fields": {"id": "INTEGER", "title": "TEXT", "price": "REAL", "stock": "INTEGER"}
    }
    expected = "CREATE TABLE Product (id INTEGER, title TEXT, price REAL, stock INTEGER)"
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_insert_single_row(player_code):
    input_data = {
        "operation": "insert",
        "class_name": "User",
        "fields": {"name": "TEXT", "age": "INTEGER"},
        "values": {"name": "Alice", "age": 30}
    }
    expected = "INSERT INTO User (name, age) VALUES ('Alice', 30)"
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_insert_with_string_escaping(player_code):
    input_data = {
        "operation": "insert",
        "class_name": "Post",
        "fields": {"title": "TEXT", "content": "TEXT"},
        "values": {"title": "Hello", "content": "World"}
    }
    expected = "INSERT INTO Post (title, content) VALUES ('Hello', 'World')"
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_select_by_condition(player_code):
    input_data = {
        "operation": "select",
        "class_name": "User",
        "fields": {"name": "TEXT", "age": "INTEGER"},
        "where": {"name": "Alice"}
    }
    expected = "SELECT * FROM User WHERE name='Alice'"
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_select_multiple_conditions(player_code):
    input_data = {
        "operation": "select",
        "class_name": "Product",
        "fields": {"title": "TEXT", "price": "REAL"},
        "where": {"title": "Widget", "price": 9.99}
    }
    expected = "SELECT * FROM Product WHERE title='Widget' AND price=9.99"
    result = run_player_code(player_code, input_data)
    assert result == expected
