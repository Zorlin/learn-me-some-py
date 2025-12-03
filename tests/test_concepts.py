"""
Tests for Concept DAG loader and operations.

This file tests:
- Loading concepts from TOML files
- Building the DAG structure
- Topological sorting (learning order)
- Cycle detection
- Unlockable concept discovery
- Path finding between concepts
"""

import tempfile
from pathlib import Path
import pytest

from lmsp.python.concepts import Concept, ConceptLoader, ConceptDAG


# Fixtures for test concepts


@pytest.fixture
def temp_concepts_dir():
    """Create a temporary directory with test concepts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = Path(tmpdir) / "concepts"
        concepts_dir.mkdir()

        # Level 0: Root concepts (no prerequisites)
        level_0 = concepts_dir / "level_0"
        level_0.mkdir()

        (level_0 / "variables.toml").write_text("""
[concept]
id = "variables"
name = "Variables: Storing Values"
level = 0
prerequisites = []

[description]
brief = "Store data in named containers"
detailed = "Variables are like labeled boxes that hold values."
""")

        (level_0 / "print.toml").write_text("""
[concept]
id = "print"
name = "Print: Show Output"
level = 0
prerequisites = []

[description]
brief = "Display text on screen"
detailed = "Print shows messages to the player."
""")

        # Level 1: Basic concepts
        level_1 = concepts_dir / "level_1"
        level_1.mkdir()

        (level_1 / "if_else.toml").write_text("""
[concept]
id = "if_else"
name = "If/Else: Making Decisions"
level = 1
prerequisites = ["variables"]

[description]
brief = "Choose different paths"
detailed = "If/else lets your code make choices."
""")

        (level_1 / "for_loops.toml").write_text("""
[concept]
id = "for_loops"
name = "For Loops: Repetition"
level = 1
prerequisites = ["variables"]

[description]
brief = "Repeat actions"
detailed = "For loops do things multiple times."
""")

        # Level 2: Advanced concepts
        level_2 = concepts_dir / "level_2"
        level_2.mkdir()

        (level_2 / "lists.toml").write_text("""
[concept]
id = "lists"
name = "Lists: Collections"
level = 2
prerequisites = ["variables", "for_loops"]

[description]
brief = "Store multiple values"
detailed = "Lists are like inventories."

[challenges]
starter = "lists_create"
intermediate = "lists_iterate"
mastery = "lists_advanced"
""")

        (level_2 / "functions.toml").write_text("""
[concept]
id = "functions"
name = "Functions: Reusable Code"
level = 2
prerequisites = ["if_else"]

[description]
brief = "Package code for reuse"
detailed = "Functions are like spells you can cast repeatedly."
""")

        yield concepts_dir


@pytest.fixture
def cyclic_concepts_dir():
    """Create concepts with a cycle (invalid DAG)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        concepts_dir = Path(tmpdir) / "concepts"
        concepts_dir.mkdir()

        level_0 = concepts_dir / "level_0"
        level_0.mkdir()

        # A depends on B
        (level_0 / "a.toml").write_text("""
[concept]
id = "a"
name = "Concept A"
level = 0
prerequisites = ["b"]

[description]
brief = "Test concept A"
detailed = "Depends on B"
""")

        # B depends on C
        (level_0 / "b.toml").write_text("""
[concept]
id = "b"
name = "Concept B"
level = 0
prerequisites = ["c"]

[description]
brief = "Test concept B"
detailed = "Depends on C"
""")

        # C depends on A (creates cycle: A -> B -> C -> A)
        (level_0 / "c.toml").write_text("""
[concept]
id = "c"
name = "Concept C"
level = 0
prerequisites = ["a"]

[description]
brief = "Test concept C"
detailed = "Depends on A, creating cycle"
""")

        yield concepts_dir


# Tests for ConceptLoader


def test_concept_loader_loads_single_concept(temp_concepts_dir):
    """Test loading a single concept by ID."""
    loader = ConceptLoader(temp_concepts_dir)
    concept = loader.load("variables")

    assert concept is not None
    assert concept.id == "variables"
    assert concept.name == "Variables: Storing Values"
    assert concept.level == 0
    assert len(concept.prerequisites) == 0


def test_concept_loader_loads_all_concepts(temp_concepts_dir):
    """Test loading all concepts from all levels."""
    loader = ConceptLoader(temp_concepts_dir)
    concepts = loader.load_all()

    assert len(concepts) == 6
    concept_ids = [c.id for c in concepts]
    assert "variables" in concept_ids
    assert "print" in concept_ids
    assert "if_else" in concept_ids
    assert "for_loops" in concept_ids
    assert "lists" in concept_ids
    assert "functions" in concept_ids


def test_concept_loader_caches_concepts(temp_concepts_dir):
    """Test that loader caches concepts after first load."""
    loader = ConceptLoader(temp_concepts_dir)

    # First load
    concept1 = loader.load("variables")
    # Second load (should be cached)
    concept2 = loader.load("variables")

    assert concept1 is concept2  # Same object


def test_concept_loader_returns_none_for_unknown_concept(temp_concepts_dir):
    """Test that unknown concepts return None."""
    loader = ConceptLoader(temp_concepts_dir)
    concept = loader.load("nonexistent")

    assert concept is None


def test_concept_loader_filters_by_level(temp_concepts_dir):
    """Test getting concepts by level."""
    loader = ConceptLoader(temp_concepts_dir)
    level_0_concepts = loader.get_by_level(0)

    assert len(level_0_concepts) == 2
    concept_ids = [c.id for c in level_0_concepts]
    assert "variables" in concept_ids
    assert "print" in concept_ids


# Tests for ConceptDAG


def test_concept_dag_loads_all_concepts(temp_concepts_dir):
    """Test that DAG loads all concepts."""
    dag = ConceptDAG(temp_concepts_dir)
    concepts = dag.load_all()

    assert len(concepts) == 6
    assert "variables" in concepts
    assert "lists" in concepts


def test_concept_dag_get_concept(temp_concepts_dir):
    """Test getting a concept by ID."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    concept = dag.get_concept("variables")
    assert concept is not None
    assert concept.id == "variables"


def test_concept_dag_get_prerequisites(temp_concepts_dir):
    """Test getting direct prerequisites."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    prereqs = dag.get_prerequisites("lists")
    assert len(prereqs) == 2
    assert "variables" in prereqs
    assert "for_loops" in prereqs


def test_concept_dag_get_all_prerequisites(temp_concepts_dir):
    """Test getting all prerequisites recursively."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    # lists depends on [variables, for_loops]
    # for_loops depends on [variables]
    # So all prereqs for lists: variables, for_loops
    all_prereqs = dag.get_all_prerequisites("lists")

    assert "variables" in all_prereqs
    assert "for_loops" in all_prereqs


def test_concept_dag_get_unlocks(temp_concepts_dir):
    """Test getting directly unlocked concepts."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    # Variables unlocks: if_else, for_loops, lists
    unlocks = dag.get_unlocks("variables")

    assert len(unlocks) >= 2
    assert "if_else" in unlocks or "for_loops" in unlocks


def test_concept_dag_get_all_unlocks(temp_concepts_dir):
    """Test getting all unlocked concepts recursively."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    # Variables unlocks everything downstream
    all_unlocks = dag.get_all_unlocks("variables")

    assert "if_else" in all_unlocks
    assert "for_loops" in all_unlocks
    assert "lists" in all_unlocks  # Transitively unlocked


def test_concept_dag_topological_sort(temp_concepts_dir):
    """Test topological sort returns valid learning order."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    sorted_ids = dag.topological_sort()

    # Check all concepts present
    assert len(sorted_ids) == 6

    # Check prerequisites come before dependents
    var_idx = sorted_ids.index("variables")
    if_idx = sorted_ids.index("if_else")
    for_idx = sorted_ids.index("for_loops")
    lists_idx = sorted_ids.index("lists")

    assert var_idx < if_idx  # variables before if_else
    assert var_idx < for_idx  # variables before for_loops
    assert for_idx < lists_idx  # for_loops before lists


def test_concept_dag_get_unlockable_empty_mastery(temp_concepts_dir):
    """Test unlockable concepts with no mastery."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    unlockable = dag.get_unlockable(set())

    # Only root concepts (no prerequisites) should be unlockable
    assert "variables" in unlockable
    assert "print" in unlockable
    assert "if_else" not in unlockable
    assert "lists" not in unlockable


def test_concept_dag_get_unlockable_partial_mastery(temp_concepts_dir):
    """Test unlockable concepts with partial mastery."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    # Master variables
    unlockable = dag.get_unlockable({"variables"})

    # Should unlock if_else and for_loops (both depend only on variables)
    assert "if_else" in unlockable
    assert "for_loops" in unlockable
    # Should NOT unlock lists (also needs for_loops)
    assert "lists" not in unlockable


def test_concept_dag_get_unlockable_full_mastery(temp_concepts_dir):
    """Test unlockable concepts with sufficient mastery."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    # Master variables and for_loops
    unlockable = dag.get_unlockable({"variables", "for_loops"})

    # Should unlock lists
    assert "lists" in unlockable


def test_concept_dag_validate_valid_dag(temp_concepts_dir):
    """Test validation passes for valid DAG."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    errors = dag.validate_dag()

    assert len(errors) == 0


def test_concept_dag_validate_detects_cycles(cyclic_concepts_dir):
    """Test validation detects cycles."""
    dag = ConceptDAG(cyclic_concepts_dir)
    dag.load_all()

    errors = dag.validate_dag()

    assert len(errors) > 0
    assert any("Cycle detected" in error or "not a DAG" in error for error in errors)


def test_concept_dag_topological_sort_fails_with_cycle(cyclic_concepts_dir):
    """Test topological sort raises error on cyclic graph."""
    dag = ConceptDAG(cyclic_concepts_dir)
    dag.load_all()

    with pytest.raises(Exception):  # networkx raises on cycles
        dag.topological_sort()


def test_concept_dag_get_learning_path(temp_concepts_dir):
    """Test finding learning path between concepts."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    # Path from variables to lists
    path = dag.get_learning_path("variables", "lists")

    assert len(path) > 0
    assert path[0] == "variables"
    assert path[-1] == "lists"
    assert "for_loops" in path  # Must go through for_loops


def test_concept_dag_get_learning_path_no_path(temp_concepts_dir):
    """Test learning path returns empty list when no path exists."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    # No path from lists back to variables (wrong direction)
    path = dag.get_learning_path("lists", "variables")

    assert len(path) == 0


def test_concept_dag_get_root_concepts(temp_concepts_dir):
    """Test getting root concepts (no prerequisites)."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    roots = dag.get_root_concepts()

    assert len(roots) == 2
    assert "variables" in roots
    assert "print" in roots


def test_concept_dag_get_leaf_concepts(temp_concepts_dir):
    """Test getting leaf concepts (don't unlock anything)."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    leaves = dag.get_leaf_concepts()

    # Lists and functions are leaves (nothing depends on them in our test data)
    assert "lists" in leaves or "functions" in leaves


def test_concept_dag_get_concepts_by_level(temp_concepts_dir):
    """Test filtering concepts by level."""
    dag = ConceptDAG(temp_concepts_dir)
    dag.load_all()

    level_2_concepts = dag.get_concepts_by_level(2)

    assert len(level_2_concepts) == 2
    concept_ids = [c.id for c in level_2_concepts]
    assert "lists" in concept_ids
    assert "functions" in concept_ids


# Integration tests


def test_full_workflow_from_load_to_unlock(temp_concepts_dir):
    """Test complete workflow: load -> validate -> unlock progression."""
    dag = ConceptDAG(temp_concepts_dir)

    # Load
    concepts = dag.load_all()
    assert len(concepts) > 0

    # Validate
    errors = dag.validate_dag()
    assert len(errors) == 0

    # Get learning order
    order = dag.topological_sort()
    assert len(order) == 6

    # Simulate learning progression
    mastered = set()
    unlockable = dag.get_unlockable(mastered)
    assert len(unlockable) == 2  # variables, print

    # Master variables
    mastered.add("variables")
    unlockable = dag.get_unlockable(mastered)
    assert "if_else" in unlockable
    assert "for_loops" in unlockable

    # Master for_loops
    mastered.add("for_loops")
    unlockable = dag.get_unlockable(mastered)
    assert "lists" in unlockable


# Self-teaching note:
#
# This file demonstrates:
# - pytest fixtures for test setup (Level 3+)
# - Temporary directories for isolated tests (Professional practice)
# - Testing graph algorithms (Level 4+)
# - Integration tests vs unit tests (Software engineering)
# - Context managers with tempfile (Level 4)
#
# The learner will understand this after mastering:
# - Level 2: Lists, collections
# - Level 3: Functions
# - Level 4: Classes, with statements
