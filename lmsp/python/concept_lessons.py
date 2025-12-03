"""
Concept Lessons - Duolingo-style Micro-lessons
==============================================

Bite-sized lessons that teach ONE concept with no pressure.
Unlike challenges, these are for learning vocabulary before writing code.

Format: TOML files with lesson content and optional "try it" sandbox.
"""

import tomllib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TryIt:
    """Optional interactive sandbox for a concept."""
    prompt: str
    starter: str
    solution: str


@dataclass
class ConceptLesson:
    """A single concept micro-lesson."""
    id: str
    name: str
    level: int
    category: str
    order: int = 0

    # Descriptions (like challenges)
    description_brief: str = ""  # Short desc under title
    description_detailed: str = ""  # Detailed desc for left column

    # The actual lesson content (markdown)
    lesson: str = ""

    # Optional interactive sandbox
    try_it: Optional[TryIt] = None

    # Validation config (like challenges)
    validation_type: str = "legacy"  # "legacy" or "pytest"
    test_file: Optional[str] = None  # e.g., "test_basic_operators.py"

    # Connections
    prerequisites: list[str] = field(default_factory=list)
    enables: list[str] = field(default_factory=list)
    used_in: list[str] = field(default_factory=list)  # Challenge IDs
    see_also: list[str] = field(default_factory=list)

    # Meta
    time_to_read: int = 30  # seconds
    difficulty: str = "beginner"
    tags: list[str] = field(default_factory=list)
    bonus: bool = False  # "Extra credit" concept


class ConceptLessonLoader:
    """Loads concept lessons from TOML files."""

    def __init__(self, concepts_dir: Optional[Path] = None):
        if concepts_dir is None:
            concepts_dir = Path(__file__).parent.parent.parent / "concepts"
        self.concepts_dir = concepts_dir
        self._lessons: dict[str, ConceptLesson] = {}
        self._by_category: dict[str, list[ConceptLesson]] = {}
        self._load_all()

    def _load_all(self):
        """Load all concept lessons from disk."""
        if not self.concepts_dir.exists():
            return

        for toml_file in self.concepts_dir.rglob("*.toml"):
            try:
                lesson = self._load_lesson(toml_file)
                if lesson:
                    self._lessons[lesson.id] = lesson

                    # Index by category
                    if lesson.category not in self._by_category:
                        self._by_category[lesson.category] = []
                    self._by_category[lesson.category].append(lesson)
            except Exception as e:
                print(f"Warning: Failed to load concept lesson {toml_file}: {e}")

        # Sort lessons within each category by order, then level
        for category in self._by_category:
            self._by_category[category].sort(key=lambda l: (l.level, l.order))

    def _load_lesson(self, path: Path) -> Optional[ConceptLesson]:
        """Load a single concept lesson from a TOML file."""
        with open(path, "rb") as f:
            data = tomllib.load(f)

        # Must have [concept] section
        if "concept" not in data:
            return None

        concept = data["concept"]
        content = data.get("content", {})
        connections = data.get("connections", {})
        meta = data.get("meta", {})
        description = data.get("description", {})
        validation = data.get("validation", {})

        # Parse try_it if present
        try_it = None
        if "try_it" in content:
            ti = content["try_it"]
            try_it = TryIt(
                prompt=ti.get("prompt", ""),
                starter=ti.get("starter", ""),
                solution=ti.get("solution", ""),
            )

        return ConceptLesson(
            id=concept.get("id", path.stem),
            name=concept.get("name", path.stem),
            level=concept.get("level", 1),
            category=concept.get("category", "uncategorized"),
            order=concept.get("order", 0),
            description_brief=description.get("brief", ""),
            description_detailed=description.get("detailed", ""),
            lesson=content.get("lesson", ""),
            try_it=try_it,
            validation_type=validation.get("type", "legacy"),
            test_file=validation.get("test_file"),
            prerequisites=connections.get("prerequisites", []),
            enables=connections.get("enables", []),
            used_in=connections.get("used_in", []),
            see_also=connections.get("see_also", []),
            time_to_read=meta.get("time_to_read", 30),
            difficulty=meta.get("difficulty", "beginner"),
            tags=meta.get("tags", []),
            bonus=meta.get("bonus", False),
        )

    def get(self, concept_id: str) -> Optional[ConceptLesson]:
        """Get a concept lesson by ID."""
        return self._lessons.get(concept_id)

    def get_all(self) -> list[ConceptLesson]:
        """Get all concept lessons."""
        return list(self._lessons.values())

    def get_by_category(self, category: str) -> list[ConceptLesson]:
        """Get all lessons in a category, ordered."""
        return self._by_category.get(category, [])

    def get_categories(self) -> list[str]:
        """Get all category names."""
        return list(self._by_category.keys())

    def get_for_challenge(self, challenge_id: str) -> list[ConceptLesson]:
        """Get all concept lessons used by a challenge."""
        return [
            lesson for lesson in self._lessons.values()
            if challenge_id in lesson.used_in
        ]

    def get_summary(self) -> dict:
        """Get a summary of all lessons grouped by category."""
        return {
            category: [
                {
                    "id": l.id,
                    "name": l.name,
                    "level": l.level,
                    "time_to_read": l.time_to_read,
                    "bonus": l.bonus,
                }
                for l in lessons
            ]
            for category, lessons in self._by_category.items()
        }


# Global instance
_lesson_loader: Optional[ConceptLessonLoader] = None


def get_lesson_loader() -> ConceptLessonLoader:
    """Get the global concept lesson loader."""
    global _lesson_loader
    if _lesson_loader is None:
        _lesson_loader = ConceptLessonLoader()
    return _lesson_loader
