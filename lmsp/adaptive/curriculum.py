"""
Project-Driven Curriculum Generator

The killer feature: "I want to build X" → generates curriculum backwards from goal.

How it works:
1. Analyze goal description to identify required concepts
2. Build learning path respecting prerequisites (topological sort)
3. Theme challenges around the goal (Discord bot, game, etc.)
4. Estimate completion time
5. Skip already-mastered concepts

Self-teaching note:
This file demonstrates:
- Graph algorithms (topological sort) (Level 6)
- Dataclasses with methods (Level 5)
- String analysis for goal parsing (Level 4)
- JSON persistence (Level 4)
- Collection comprehensions (Level 4)
- Design patterns (Level 6)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Any
from datetime import datetime
from pathlib import Path
import json


@dataclass
class ConceptRequirement:
    """
    A concept required to achieve a goal.

    Each concept has:
    - ID matching concept TOML file
    - Level (0-6)
    - Prerequisites (other concepts)
    - Priority (how important for the goal)
    """

    concept_id: str
    level: int = 0
    description: str = ""
    prerequisites: List[str] = field(default_factory=list)
    priority: float = 0.5  # 0-1, how important for goal

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "concept_id": self.concept_id,
            "level": self.level,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConceptRequirement":
        """Deserialize from dictionary."""
        return cls(
            concept_id=data["concept_id"],
            level=data.get("level", 0),
            description=data.get("description", ""),
            prerequisites=data.get("prerequisites", []),
            priority=data.get("priority", 0.5),
        )


@dataclass
class ThemedChallenge:
    """
    A challenge themed around the player's goal.

    The same concept (e.g., "loops") can be taught differently
    depending on whether the goal is "Discord bot" vs "text game".
    """

    concept_id: str
    goal_context: str
    title: str = ""
    description: str = ""
    starter_code: Optional[str] = None
    expected_output: Optional[str] = None
    hints: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "concept_id": self.concept_id,
            "goal_context": self.goal_context,
            "title": self.title,
            "description": self.description,
            "starter_code": self.starter_code,
            "expected_output": self.expected_output,
            "hints": self.hints,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThemedChallenge":
        """Deserialize from dictionary."""
        return cls(
            concept_id=data["concept_id"],
            goal_context=data["goal_context"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            starter_code=data.get("starter_code"),
            expected_output=data.get("expected_output"),
            hints=data.get("hints", []),
        )


@dataclass
class LearningPath:
    """
    Ordered list of concepts to learn for a goal.

    Respects prerequisites so player learns in optimal order.
    """

    goal: str
    concepts: List[str] = field(default_factory=list)
    estimated_hours: float = 0.0

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "goal": self.goal,
            "concepts": self.concepts,
            "estimated_hours": self.estimated_hours,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LearningPath":
        """Deserialize from dictionary."""
        return cls(
            goal=data["goal"],
            concepts=data.get("concepts", []),
            estimated_hours=data.get("estimated_hours", 0.0),
        )


@dataclass
class Curriculum:
    """
    Complete curriculum for a project goal.

    Contains:
    - Goal description
    - Learning path (ordered concepts)
    - Themed challenges
    - Estimated completion time
    """

    goal: str
    path: LearningPath
    challenges: List[ThemedChallenge] = field(default_factory=list)
    estimated_hours: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "version": "1.0",
            "goal": self.goal,
            "path": self.path.to_dict(),
            "challenges": [c.to_dict() for c in self.challenges],
            "estimated_hours": self.estimated_hours,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Curriculum":
        """Deserialize from dictionary."""
        return cls(
            goal=data["goal"],
            path=LearningPath.from_dict(data["path"]),
            challenges=[ThemedChallenge.from_dict(c) for c in data.get("challenges", [])],
            estimated_hours=data.get("estimated_hours", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )

    def save(self, path: Path) -> None:
        """Save curriculum to JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> "Curriculum":
        """Load curriculum from JSON file."""
        data = json.loads(path.read_text())
        return cls.from_dict(data)


class ProjectCurriculumGenerator:
    """
    Generates personalized curricula from project goals.

    Usage:
        generator = ProjectCurriculumGenerator()

        # Generate curriculum for a goal
        curriculum = generator.generate_curriculum_sync("Build a Discord bot")

        # Or with known concepts skipped
        curriculum = generator.generate_curriculum_sync(
            "Build a Discord bot",
            known_concepts=["variables", "strings"]
        )

    The generator:
    1. Analyzes the goal to identify concepts
    2. Orders concepts by prerequisites (topological sort)
    3. Themes challenges around the goal
    4. Estimates time based on complexity
    """

    # Concept database (in real implementation, load from TOMLs)
    CONCEPT_LIBRARY = {
        "variables": ConceptRequirement("variables", level=0, description="Store values"),
        "print": ConceptRequirement("print", level=0, description="Output text"),
        "strings": ConceptRequirement("strings", level=0, description="Text manipulation"),
        "numbers": ConceptRequirement("numbers", level=0, description="Numeric operations"),
        "input": ConceptRequirement("input", level=0, description="User input"),
        "conditionals": ConceptRequirement("conditionals", level=1, description="If/else decisions", prerequisites=["variables"]),
        "loops": ConceptRequirement("loops", level=1, description="Repeat actions", prerequisites=["variables"]),
        "lists": ConceptRequirement("lists", level=2, description="Collections of items", prerequisites=["variables"]),
        "dictionaries": ConceptRequirement("dictionaries", level=2, description="Key-value pairs", prerequisites=["variables"]),
        "functions": ConceptRequirement("functions", level=3, description="Reusable code", prerequisites=["variables"]),
        "parameters": ConceptRequirement("parameters", level=3, description="Function inputs", prerequisites=["functions"]),
        "return_values": ConceptRequirement("return_values", level=3, description="Function outputs", prerequisites=["functions"]),
        "list_comprehensions": ConceptRequirement("list_comprehensions", level=4, description="Concise list creation", prerequisites=["loops", "lists"]),
        "file_io": ConceptRequirement("file_io", level=4, description="Read/write files", prerequisites=["strings"]),
        "exceptions": ConceptRequirement("exceptions", level=4, description="Error handling", prerequisites=["conditionals"]),
        "classes": ConceptRequirement("classes", level=5, description="Object-oriented programming", prerequisites=["functions"]),
        "methods": ConceptRequirement("methods", level=5, description="Class functions", prerequisites=["classes"]),
        "async": ConceptRequirement("async", level=6, description="Asynchronous programming", prerequisites=["functions"]),
        "decorators": ConceptRequirement("decorators", level=6, description="Function modifiers", prerequisites=["functions"]),
    }

    # Goal → required concepts mapping
    GOAL_CONCEPT_MAP = {
        "discord bot": ["variables", "strings", "functions", "async", "classes", "dictionaries"],
        "text adventure": ["variables", "strings", "conditionals", "loops", "functions", "dictionaries"],
        "calculator": ["variables", "numbers", "conditionals", "functions", "input"],
        "web scraper": ["strings", "lists", "loops", "functions", "file_io"],
        "data analysis": ["lists", "dictionaries", "functions", "file_io", "list_comprehensions"],
        "game": ["variables", "conditionals", "loops", "functions", "lists", "classes"],
        "todo app": ["variables", "strings", "lists", "functions", "file_io"],
        "number guessing": ["variables", "numbers", "conditionals", "loops", "input"],
        "countdown timer": ["variables", "numbers", "loops", "functions"],
    }

    # Themed challenge templates
    CHALLENGE_THEMES = {
        "loops": {
            "discord bot": ("Bot Command Loop", "Process incoming commands in a loop"),
            "game": ("Game Loop", "Keep the game running until player quits"),
            "data analysis": ("Data Iterator", "Process each item in your dataset"),
            "default": ("Repeat Actions", "Use a loop to repeat actions"),
        },
        "functions": {
            "discord bot": ("Command Handler", "Create a function to handle bot commands"),
            "game": ("Action Functions", "Create functions for player actions"),
            "calculator": ("Calculator Operations", "Create functions for math operations"),
            "default": ("Reusable Code", "Create a function you can call multiple times"),
        },
        "conditionals": {
            "discord bot": ("Permission Check", "Check if user has permission"),
            "game": ("Player Choices", "Handle different player choices"),
            "calculator": ("Operation Selection", "Choose the right math operation"),
            "default": ("Making Decisions", "Use if/else to make decisions"),
        },
        "lists": {
            "discord bot": ("Server Members", "Track members in a list"),
            "game": ("Inventory System", "Store player items in a list"),
            "data analysis": ("Data Collection", "Store your data in a list"),
            "default": ("Collection of Items", "Store multiple items in a list"),
        },
        "dictionaries": {
            "discord bot": ("User Settings", "Store user preferences in a dictionary"),
            "game": ("Player Stats", "Track player attributes with a dictionary"),
            "data analysis": ("Data Records", "Organize data with dictionaries"),
            "default": ("Key-Value Storage", "Associate values with keys"),
        },
    }

    def __init__(self):
        pass

    def analyze_goal_concepts(self, goal: str) -> List[ConceptRequirement]:
        """
        Analyze a goal and identify required concepts.

        Args:
            goal: Description of what player wants to build

        Returns:
            List of required concepts
        """
        goal_lower = goal.lower()

        # Find matching goal pattern
        matching_concepts: Set[str] = set()

        for pattern, concepts in self.GOAL_CONCEPT_MAP.items():
            if pattern in goal_lower:
                matching_concepts.update(concepts)

        # If no specific match, provide basics
        if not matching_concepts:
            matching_concepts = {"variables", "strings", "functions", "loops", "conditionals"}

        # Add prerequisites
        all_concepts = set()
        for concept_id in matching_concepts:
            all_concepts.add(concept_id)
            if concept_id in self.CONCEPT_LIBRARY:
                all_concepts.update(self.CONCEPT_LIBRARY[concept_id].prerequisites)

        # Convert to ConceptRequirement list
        requirements = []
        for concept_id in all_concepts:
            if concept_id in self.CONCEPT_LIBRARY:
                requirements.append(self.CONCEPT_LIBRARY[concept_id])
            else:
                requirements.append(ConceptRequirement(concept_id=concept_id))

        return requirements

    def topological_sort(self, concepts: List[ConceptRequirement]) -> List[ConceptRequirement]:
        """
        Sort concepts respecting prerequisites.

        Uses Kahn's algorithm for topological sorting.

        Args:
            concepts: List of concepts to sort

        Returns:
            Sorted list (prerequisites first)
        """
        # Build adjacency list and in-degree count
        concept_map = {c.concept_id: c for c in concepts}
        in_degree: Dict[str, int] = {c.concept_id: 0 for c in concepts}
        graph: Dict[str, List[str]] = {c.concept_id: [] for c in concepts}

        for concept in concepts:
            for prereq in concept.prerequisites:
                if prereq in concept_map:
                    graph[prereq].append(concept.concept_id)
                    in_degree[concept.concept_id] += 1

        # Find all concepts with no prerequisites (in-degree 0)
        queue = [cid for cid, deg in in_degree.items() if deg == 0]
        sorted_ids = []

        while queue:
            # Sort queue by level (lower level first)
            queue.sort(key=lambda cid: concept_map[cid].level)

            current = queue.pop(0)
            sorted_ids.append(current)

            # Reduce in-degree of dependents
            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Return sorted concepts
        return [concept_map[cid] for cid in sorted_ids if cid in concept_map]

    def theme_challenge(
        self,
        concept_id: str,
        goal: str
    ) -> ThemedChallenge:
        """
        Create a themed challenge for a concept.

        Args:
            concept_id: Concept to teach
            goal: Project goal to theme around

        Returns:
            ThemedChallenge with goal-relevant content
        """
        goal_lower = goal.lower()

        # Find theme for this concept/goal combination
        if concept_id in self.CHALLENGE_THEMES:
            themes = self.CHALLENGE_THEMES[concept_id]

            # Find matching goal theme
            title, description = themes.get("default", ("Challenge", "Complete the challenge"))

            for pattern, theme_data in themes.items():
                if pattern != "default" and pattern in goal_lower:
                    title, description = theme_data
                    break
        else:
            # Default theme
            title = f"Learn {concept_id.replace('_', ' ').title()}"
            description = f"Practice {concept_id.replace('_', ' ')}"

        return ThemedChallenge(
            concept_id=concept_id,
            goal_context=goal,
            title=title,
            description=description,
        )

    def estimate_time(self, concepts: List[ConceptRequirement]) -> float:
        """
        Estimate hours to complete curriculum.

        Uses simple heuristic: 1-2 hours per concept based on level.

        Args:
            concepts: List of concepts

        Returns:
            Estimated hours
        """
        hours = 0.0
        for concept in concepts:
            # Higher level = more time
            level_multiplier = 1 + (concept.level * 0.5)
            hours += level_multiplier

        return round(hours, 1)

    def generate_curriculum_sync(
        self,
        goal: str,
        known_concepts: Optional[List[str]] = None
    ) -> Curriculum:
        """
        Generate a complete curriculum for a goal.

        Args:
            goal: Description of what player wants to build
            known_concepts: Optional list of already-mastered concepts

        Returns:
            Complete Curriculum
        """
        known_concepts = known_concepts or []
        known_set = set(known_concepts)

        # 1. Analyze goal to get required concepts
        requirements = self.analyze_goal_concepts(goal)

        # 2. Filter out known concepts (keep prerequisites for structure)
        filtered_requirements = [
            r for r in requirements
            if r.concept_id not in known_set
        ]

        # 3. Topological sort
        sorted_concepts = self.topological_sort(filtered_requirements)

        # 4. Create learning path
        concept_ids = [c.concept_id for c in sorted_concepts]
        path = LearningPath(
            goal=goal,
            concepts=concept_ids,
            estimated_hours=self.estimate_time(sorted_concepts)
        )

        # 5. Theme challenges
        challenges = [
            self.theme_challenge(c.concept_id, goal)
            for c in sorted_concepts
        ]

        # 6. Build curriculum
        return Curriculum(
            goal=goal,
            path=path,
            challenges=challenges,
            estimated_hours=path.estimated_hours
        )


# Self-teaching note:
#
# This file demonstrates:
# - Graph algorithms (topological sort using Kahn's algorithm)
# - Data structure design (Curriculum, LearningPath, etc.)
# - String pattern matching for goal analysis
# - JSON persistence with versioning
# - Design pattern: builder/generator pattern
#
# The project-driven curriculum is powerful because:
# 1. Learning is MOTIVATED - player cares about the goal
# 2. Challenges are RELEVANT - themed around their project
# 3. Order is OPTIMAL - respects prerequisites
# 4. Progress is MEASURABLE - estimated completion time
# 5. Personalization - skips known concepts
#
# Real implementation would:
# - Use Claude API to analyze arbitrary goals
# - Load concept library from TOML files
# - Generate richer themed challenges
# - Adapt based on player performance
#
# Prerequisites:
# - Level 4: Collections, comprehensions
# - Level 5: Dataclasses, JSON, pathlib
# - Level 6: Graph algorithms, design patterns
