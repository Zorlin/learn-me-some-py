"""
Tests for Meta: Build the Concept Loader.

Build the system that loads concept definitions from TOML files.
"""

import subprocess
import sys
import json
import tempfile
from pathlib import Path


def run_player_code(code: str, toml_content: str) -> dict:
    """Run player code with a temporary TOML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write(toml_content)
        toml_path = f.name
    
    try:
        full_code = f'''
{code}

import json
concept = load_concept({repr(toml_path)})

# Convert to dict for JSON
output = {{
    "id": concept.id,
    "name": concept.name,
    "level": concept.level,
    "prerequisites": concept.prerequisites,
    "description_brief": concept.description_brief,
    "description_detailed": concept.description_detailed
}}
print(json.dumps(output))
'''
        result = subprocess.run([sys.executable, "-c", full_code], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            raise RuntimeError(f"Code failed: {result.stderr}")
        return json.loads(result.stdout.strip())
    finally:
        Path(toml_path).unlink()


def test_has_load_concept_function(player_code):
    """Check that code defines load_concept function."""
    assert "def load_concept" in player_code, "Define a 'load_concept' function"


def test_has_concept_class(player_code):
    """Check that code defines Concept dataclass."""
    assert "class Concept" in player_code, "Define a 'Concept' dataclass"
    assert "@dataclass" in player_code, "Use @dataclass decorator"


def test_load_simple_concept(player_code):
    """Test loading a simple concept."""
    toml_content = """[concept]
id = "test_concept"
name = "Test Concept"
level = 1
prerequisites = []

[description]
brief = "A test"
detailed = "Testing"
"""
    result = run_player_code(player_code, toml_content)
    
    assert result["id"] == "test_concept", "Should load concept ID"
    assert result["name"] == "Test Concept", "Should load concept name"
    assert result["level"] == 1, "Should load concept level"


def test_load_with_prerequisites(player_code):
    """Test loading a concept with prerequisites."""
    toml_content = """[concept]
id = "advanced"
name = "Advanced Concept"
level = 3
prerequisites = ["basic1", "basic2"]

[description]
brief = "Advanced stuff"
detailed = "Requires prerequisites"
"""
    result = run_player_code(player_code, toml_content)
    
    assert result["prerequisites"] == ["basic1", "basic2"], "Should load prerequisites list"


def test_parse_descriptions(player_code):
    """Test parsing description fields."""
    toml_content = """[concept]
id = "desc_test"
name = "Description Test"
level = 2
prerequisites = []

[description]
brief = "Brief description"
detailed = "This is a detailed description"
"""
    result = run_player_code(player_code, toml_content)
    
    assert result["description_brief"] == "Brief description", "Should parse brief description"
    assert result["description_detailed"] == "This is a detailed description", "Should parse detailed description"
