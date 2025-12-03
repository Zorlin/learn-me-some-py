"""
Challenge loader and TOML parser for LMSP.

This module loads challenge definitions from TOML files and provides
filtering/searching capabilities.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions


@dataclass
class TestCase:
    """
    A single test case for a challenge.

    Attributes:
        name: Test case identifier (e.g., "basic", "edge_case")
        input: Input value(s) for the test
        expected: Expected output value(s)
    """
    name: str
    input: Any
    expected: Any


@dataclass
class Challenge:
    """
    A complete challenge definition.

    This represents everything needed to present and evaluate a coding challenge,
    including descriptions, test cases, hints, and metadata for adaptive learning.
    """
    # Identity
    id: str
    name: str
    level: int
    prerequisites: list[str]

    # Content
    description_brief: str
    description_detailed: str
    skeleton_code: str
    test_cases: list[TestCase]

    # Help system
    hints: dict[int, str] = field(default_factory=dict)
    gamepad_hints: dict[str, str] = field(default_factory=dict)

    # Solution (hidden from player)
    solution_code: str = ""

    # Metadata
    time_limit_seconds: int = 300
    speed_run_target: int = 60
    points: int = 100

    # Adaptive learning
    fun_factor: str = ""
    weakness_signals: list[str] = field(default_factory=list)

    # Validation config
    validation_type: str = "legacy"  # "legacy" or "pytest"
    test_file: str | None = None  # e.g., "test_simple_math.py" for pytest validation


class ChallengeLoader:
    """
    Loads and caches challenge definitions from TOML files.

    The loader scans a directory tree for .toml files, parses them,
    and provides methods to search and filter challenges.

    Challenges are cached after first load for performance.
    """

    def __init__(self, challenges_dir: Path) -> None:
        """
        Initialize the challenge loader.

        Args:
            challenges_dir: Path to the root directory containing challenge TOML files
        """
        self.challenges_dir = Path(challenges_dir)
        self._cache: dict[str, Challenge] = {}
        self._all_challenges: list[str] | None = None

    def list_challenges(self) -> list[str]:
        """
        List all available challenge IDs.

        Scans the challenges directory for .toml files and extracts challenge IDs.

        Returns:
            List of challenge IDs
        """
        if self._all_challenges is not None:
            return self._all_challenges

        challenge_ids = []

        # Recursively find all .toml files
        for toml_file in self.challenges_dir.rglob("*.toml"):
            try:
                with open(toml_file, "rb") as f:
                    data = tomllib.load(f)
                    if "challenge" in data and "id" in data["challenge"]:
                        challenge_ids.append(data["challenge"]["id"])
            except Exception:
                # Skip files that can't be parsed
                continue

        self._all_challenges = challenge_ids
        return challenge_ids

    def load(self, challenge_id: str) -> Challenge:
        """
        Load a challenge by ID.

        Args:
            challenge_id: The challenge ID to load

        Returns:
            Challenge object

        Raises:
            FileNotFoundError: If challenge TOML file doesn't exist
            ValueError: If TOML is missing required fields
        """
        # Check cache first
        if challenge_id in self._cache:
            return self._cache[challenge_id]

        # Find the TOML file
        toml_file = self._find_challenge_file(challenge_id)
        if not toml_file:
            raise FileNotFoundError(f"Challenge '{challenge_id}' not found")

        # Parse TOML
        with open(toml_file, "rb") as f:
            data = tomllib.load(f)

        # Extract and validate required fields
        challenge_data = data.get("challenge", {})
        description_data = data.get("description", {})
        skeleton_data = data.get("skeleton", {})
        tests_data = data.get("tests", {})
        validation_data = data.get("validation", {})
        solution_data = data.get("solution", {})
        meta_data = data.get("meta", {})
        adaptive_data = data.get("adaptive", {})

        # Parse test cases
        test_cases = []
        for case_data in tests_data.get("case", []):
            test_cases.append(TestCase(
                name=case_data["name"],
                input=case_data["input"],
                expected=case_data["expected"]
            ))

        # Parse hints (convert level_N keys to integer keys)
        hints = {}
        hints_data = data.get("hints", {})
        for key, value in hints_data.items():
            if key.startswith("level_"):
                try:
                    level = int(key.split("_")[1])
                    hints[level] = value
                except (IndexError, ValueError):
                    pass

        # Parse gamepad hints
        gamepad_hints = data.get("gamepad_hints", {})

        # Create Challenge object
        challenge = Challenge(
            id=challenge_data["id"],
            name=challenge_data["name"],
            level=challenge_data["level"],
            prerequisites=challenge_data.get("prerequisites", []),
            description_brief=description_data["brief"],
            description_detailed=description_data["detailed"],
            skeleton_code=skeleton_data["code"],
            test_cases=test_cases,
            hints=hints,
            gamepad_hints=gamepad_hints,
            solution_code=solution_data.get("code", ""),
            time_limit_seconds=meta_data.get("time_limit_seconds", 300),
            speed_run_target=meta_data.get("speed_run_target", 60),
            points=meta_data.get("points", 100),
            fun_factor=adaptive_data.get("fun_factor", ""),
            weakness_signals=adaptive_data.get("weakness_signals", []),
            validation_type=validation_data.get("type", "legacy"),
            test_file=validation_data.get("test_file")
        )

        # Cache and return
        self._cache[challenge_id] = challenge
        return challenge

    def get_by_level(self, level: int) -> list[Challenge]:
        """
        Get all challenges at a specific level.

        Args:
            level: The level to filter by

        Returns:
            List of challenges at the specified level
        """
        challenges = []
        for challenge_id in self.list_challenges():
            challenge = self.load(challenge_id)
            if challenge.level == level:
                challenges.append(challenge)
        return challenges

    def get_by_prerequisite(self, prereq: str) -> list[Challenge]:
        """
        Get all challenges that require a specific prerequisite.

        Args:
            prereq: The prerequisite challenge ID

        Returns:
            List of challenges that require this prerequisite
        """
        challenges = []
        for challenge_id in self.list_challenges():
            challenge = self.load(challenge_id)
            if prereq in challenge.prerequisites:
                challenges.append(challenge)
        return challenges

    def _find_challenge_file(self, challenge_id: str) -> Path | None:
        """
        Find the TOML file for a challenge ID.

        Args:
            challenge_id: The challenge ID to find

        Returns:
            Path to the TOML file, or None if not found
        """
        for toml_file in self.challenges_dir.rglob("*.toml"):
            try:
                with open(toml_file, "rb") as f:
                    data = tomllib.load(f)
                    if data.get("challenge", {}).get("id") == challenge_id:
                        return toml_file
            except Exception:
                continue
        return None


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses (modern Python data containers) - Level 5
# - Type hints with generics (list[str], dict[int, str]) - Level 4
# - File I/O with pathlib (cross-platform paths) - Level 3
# - TOML parsing with tomllib/tomli - Level 4
# - Caching pattern (storing results for reuse) - Level 4
# - Recursion (rglob for nested directories) - Level 4
# - Exception handling (try/except for file errors) - Level 3
# - Default values with field(default_factory=...) - Level 5
# - Type unions with | (Python 3.10+) - Level 4
# - Private methods (methods starting with _) - Level 3
#
# The learner will build this AFTER mastering:
# - Basic file reading/writing
# - Dictionaries and lists
# - Functions and classes
# - Error handling
#
# This file is part of the game engine, so the learner encounters it
# when they're ready to understand how LMSP loads its own challenges.
# Meta-learning: "How does the game know what challenges exist?"
