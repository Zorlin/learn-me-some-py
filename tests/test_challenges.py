"""
Tests for challenge loader and TOML parser.

Following TDD: These tests define the behavior before implementation.
"""
from pathlib import Path
import pytest
from lmsp.python.challenges import (
    Challenge,
    TestCase,
    ChallengeLoader,
)


@pytest.fixture
def challenges_dir(tmp_path):
    """Create a temporary challenges directory with test data."""
    challenges = tmp_path / "challenges"
    challenges.mkdir()

    # Create a simple challenge TOML
    simple_dir = challenges / "simple"
    simple_dir.mkdir()
    simple_toml = simple_dir / "test_challenge.toml"
    simple_toml.write_text("""
[challenge]
id = "test_basic"
name = "Test Basic Challenge"
level = 1
prerequisites = []

[description]
brief = "A simple test"
detailed = "Test detailed description"

[skeleton]
code = 'def solution(): pass'

[tests]
[[tests.case]]
name = "test1"
input = 5
expected = 10

[[tests.case]]
name = "test2"
input = 3
expected = 6

[hints]
level_1 = "First hint"
level_2 = "Second hint"

[gamepad_hints]
easy_mode = "Press A to win"

[solution]
code = 'def solution(x): return x * 2'

[meta]
time_limit_seconds = 60
speed_run_target = 30
points = 50

[adaptive]
fun_factor = "puzzle"
weakness_signals = ["forgot_return", "syntax_error"]
""")

    # Create a challenge with optional fields missing
    minimal_dir = challenges / "minimal"
    minimal_dir.mkdir()
    minimal_toml = minimal_dir / "minimal.toml"
    minimal_toml.write_text("""
[challenge]
id = "test_minimal"
name = "Minimal Challenge"
level = 0
prerequisites = []

[description]
brief = "Minimal"
detailed = "Minimal description"

[skeleton]
code = 'pass'

[tests]
[[tests.case]]
name = "test"
input = 1
expected = 1

[solution]
code = 'def solution(x): return x'

[meta]
time_limit_seconds = 30
speed_run_target = 15
points = 10
""")

    return challenges


def test_testcase_creation():
    """TestCase dataclass should hold test data."""
    tc = TestCase(
        name="example",
        input=5,
        expected=10
    )
    assert tc.name == "example"
    assert tc.input == 5
    assert tc.expected == 10


def test_challenge_creation():
    """Challenge dataclass should hold all challenge data."""
    challenge = Challenge(
        id="test_id",
        name="Test Challenge",
        level=1,
        prerequisites=["prereq1"],
        description_brief="Brief",
        description_detailed="Detailed",
        skeleton_code="code here",
        test_cases=[
            TestCase(name="t1", input=1, expected=2)
        ],
        hints={1: "hint1", 2: "hint2"},
        gamepad_hints={"easy": "press A"},
        solution_code="solution",
        time_limit_seconds=60,
        speed_run_target=30,
        points=100,
        fun_factor="puzzle",
        weakness_signals=["signal1"]
    )

    assert challenge.id == "test_id"
    assert challenge.level == 1
    assert len(challenge.test_cases) == 1
    assert challenge.hints[1] == "hint1"
    assert challenge.points == 100


def test_challenge_loader_init(challenges_dir):
    """ChallengeLoader should initialize with a directory."""
    loader = ChallengeLoader(challenges_dir)
    assert loader.challenges_dir == challenges_dir


def test_challenge_loader_list_challenges(challenges_dir):
    """ChallengeLoader should list all available challenge IDs."""
    loader = ChallengeLoader(challenges_dir)
    challenge_ids = loader.list_challenges()

    assert "test_basic" in challenge_ids
    assert "test_minimal" in challenge_ids
    assert len(challenge_ids) == 2


def test_challenge_loader_load_basic(challenges_dir):
    """ChallengeLoader should load a complete challenge from TOML."""
    loader = ChallengeLoader(challenges_dir)
    challenge = loader.load("test_basic")

    # Check basic fields
    assert challenge.id == "test_basic"
    assert challenge.name == "Test Basic Challenge"
    assert challenge.level == 1
    assert challenge.prerequisites == []

    # Check descriptions
    assert challenge.description_brief == "A simple test"
    assert challenge.description_detailed == "Test detailed description"

    # Check skeleton code
    assert challenge.skeleton_code == 'def solution(): pass'

    # Check test cases
    assert len(challenge.test_cases) == 2
    assert challenge.test_cases[0].name == "test1"
    assert challenge.test_cases[0].input == 5
    assert challenge.test_cases[0].expected == 10

    # Check hints
    assert challenge.hints[1] == "First hint"
    assert challenge.hints[2] == "Second hint"

    # Check gamepad hints
    assert challenge.gamepad_hints["easy_mode"] == "Press A to win"

    # Check solution
    assert challenge.solution_code == 'def solution(x): return x * 2'

    # Check meta
    assert challenge.time_limit_seconds == 60
    assert challenge.speed_run_target == 30
    assert challenge.points == 50

    # Check adaptive
    assert challenge.fun_factor == "puzzle"
    assert "forgot_return" in challenge.weakness_signals


def test_challenge_loader_load_minimal(challenges_dir):
    """ChallengeLoader should handle missing optional fields gracefully."""
    loader = ChallengeLoader(challenges_dir)
    challenge = loader.load("test_minimal")

    assert challenge.id == "test_minimal"
    assert challenge.name == "Minimal Challenge"

    # Optional fields should have defaults
    assert challenge.hints == {}
    assert challenge.gamepad_hints == {}
    assert challenge.fun_factor == ""
    assert challenge.weakness_signals == []


def test_challenge_loader_load_nonexistent(challenges_dir):
    """ChallengeLoader should raise error for nonexistent challenge."""
    loader = ChallengeLoader(challenges_dir)

    with pytest.raises(FileNotFoundError):
        loader.load("nonexistent_challenge")


def test_challenge_loader_caching(challenges_dir):
    """ChallengeLoader should cache loaded challenges."""
    loader = ChallengeLoader(challenges_dir)

    # Load once
    challenge1 = loader.load("test_basic")

    # Load again - should be same object (cached)
    challenge2 = loader.load("test_basic")

    assert challenge1 is challenge2


def test_challenge_loader_get_by_level(challenges_dir):
    """ChallengeLoader should filter challenges by level."""
    loader = ChallengeLoader(challenges_dir)

    level_0 = loader.get_by_level(0)
    level_1 = loader.get_by_level(1)

    assert len(level_0) == 1
    assert level_0[0].id == "test_minimal"

    assert len(level_1) == 1
    assert level_1[0].id == "test_basic"


def test_challenge_loader_get_by_prerequisite(challenges_dir):
    """ChallengeLoader should filter challenges by prerequisite."""
    # Create a challenge with prerequisites
    prereq_dir = challenges_dir / "prereq_test"
    prereq_dir.mkdir()
    prereq_toml = prereq_dir / "advanced.toml"
    prereq_toml.write_text("""
[challenge]
id = "test_advanced"
name = "Advanced Challenge"
level = 2
prerequisites = ["test_basic"]

[description]
brief = "Advanced"
detailed = "Requires test_basic"

[skeleton]
code = 'pass'

[tests]
[[tests.case]]
name = "test"
input = 1
expected = 1

[solution]
code = 'pass'

[meta]
time_limit_seconds = 60
speed_run_target = 30
points = 100
""")

    loader = ChallengeLoader(challenges_dir)

    # Get challenges that require test_basic
    requiring_basic = loader.get_by_prerequisite("test_basic")

    assert len(requiring_basic) == 1
    assert requiring_basic[0].id == "test_advanced"


def test_challenge_loader_invalid_toml(challenges_dir):
    """ChallengeLoader should handle invalid TOML gracefully."""
    invalid_dir = challenges_dir / "invalid"
    invalid_dir.mkdir()
    invalid_toml = invalid_dir / "bad.toml"
    invalid_toml.write_text("this is not valid TOML {{{")

    loader = ChallengeLoader(challenges_dir)

    with pytest.raises(Exception):  # tomli will raise on invalid TOML
        loader.load("bad")


def test_challenge_prerequisites_as_list(challenges_dir):
    """Prerequisites should be parsed as a list even if empty."""
    loader = ChallengeLoader(challenges_dir)
    challenge = loader.load("test_basic")

    assert isinstance(challenge.prerequisites, list)
    assert challenge.prerequisites == []


def test_challenge_test_cases_preserve_order(challenges_dir):
    """Test cases should be in the same order as defined in TOML."""
    loader = ChallengeLoader(challenges_dir)
    challenge = loader.load("test_basic")

    # First test case should be test1 with input 5
    assert challenge.test_cases[0].name == "test1"
    assert challenge.test_cases[0].input == 5

    # Second test case should be test2 with input 3
    assert challenge.test_cases[1].name == "test2"
    assert challenge.test_cases[1].input == 3


# Self-teaching note:
#
# This test file demonstrates:
# - pytest fixtures (tmp_path, custom fixtures)
# - Test-Driven Development (tests before implementation)
# - Testing file I/O and TOML parsing
# - Testing error handling (pytest.raises)
# - Testing caching behavior
# - Testing filtering and searching
# - Using pathlib for cross-platform paths
#
# Prerequisites: Level 4
# - pytest framework
# - fixtures
# - temporary file handling
# - exception testing
