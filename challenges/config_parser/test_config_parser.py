"""
Tests for Configuration File Parser challenge.
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

def test_simple_flat(player_code):
    input_data = """
[app]
name = myapp
version = 1.0
"""
    expected = {"app": {"name": "myapp", "version": "1.0"}}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_type_conversion(player_code):
    input_data = """
[settings]
count = 42
ratio = 3.14
enabled = true
disabled = false
"""
    expected = {"settings": {"count": 42, "ratio": 3.14, "enabled": True, "disabled": False}}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_nested_sections(player_code):
    input_data = """
[server]
host = localhost

[server.ssl]
enabled = true
port = 443

[database]
url = postgres://localhost
"""
    expected = {
        "server": {
            "host": "localhost",
            "ssl": {"enabled": True, "port": 443}
        },
        "database": {"url": "postgres://localhost"}
    }
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_missing_section(player_code):
    input_data = "key = value"
    expected = {"error": "key before section"}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_invalid_line(player_code):
    input_data = """
[app]
this is not valid syntax
"""
    expected = {"error": "invalid line: this is not valid syntax"}
    result = run_player_code(player_code, input_data)
    assert result == expected

def test_realistic_config(player_code):
    input_data = """
[database]
host = db.example.com
port = 5432
name = production

[redis]
host = cache.example.com
port = 6379
timeout = 5.0

[server]
host = 0.0.0.0
port = 8080
workers = 4

[server.logging]
level = info
file = /var/log/app.log
"""
    expected = {
        "database": {"host": "db.example.com", "port": 5432, "name": "production"},
        "redis": {"host": "cache.example.com", "port": 6379, "timeout": 5.0},
        "server": {
            "host": "0.0.0.0",
            "port": 8080,
            "workers": 4,
            "logging": {"level": "info", "file": "/var/log/app.log"}
        }
    }
    result = run_player_code(player_code, input_data)
    assert result == expected
