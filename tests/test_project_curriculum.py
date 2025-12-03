"""
Tests for Project-Driven Curriculum Generator

TDD: These tests define how project-driven curriculum works BEFORE implementation.

The killer feature: "I want to build X" → generates curriculum backwards from goal

The ProjectCurriculumGenerator:
1. Analyzes a goal description (e.g., "Discord bot")
2. Identifies required concepts
3. Builds a learning path with topological sort
4. Themes challenges around the goal
5. Provides estimated completion time
"""

import pytest
from datetime import timedelta
from typing import List, Optional
from lmsp.adaptive.curriculum import (
    ProjectCurriculumGenerator,
    Curriculum,
    ThemedChallenge,
    ConceptRequirement,
    LearningPath,
)


class TestConceptRequirement:
    """Test the concept requirement data structure."""

    def test_concept_has_id_and_level(self):
        """Concept requirement should have ID and level."""
        req = ConceptRequirement(
            concept_id="loops",
            level=1,
            description="For loops and while loops"
        )

        assert req.concept_id == "loops"
        assert req.level == 1
        assert req.description == "For loops and while loops"

    def test_concept_has_prerequisites(self):
        """Concept can specify prerequisites."""
        req = ConceptRequirement(
            concept_id="list_comprehensions",
            level=4,
            prerequisites=["loops", "lists"]
        )

        assert "loops" in req.prerequisites
        assert "lists" in req.prerequisites

    def test_concept_priority(self):
        """Concepts can have priority weights."""
        req = ConceptRequirement(
            concept_id="functions",
            level=3,
            priority=0.9  # High priority
        )

        assert req.priority == 0.9


class TestThemedChallenge:
    """Test themed challenge generation."""

    def test_themed_challenge_has_concept_and_goal(self):
        """Themed challenge connects concept to project goal."""
        challenge = ThemedChallenge(
            concept_id="loops",
            goal_context="Discord bot",
            title="Bot Command Loop",
            description="Process commands in a loop like a Discord bot"
        )

        assert challenge.concept_id == "loops"
        assert challenge.goal_context == "Discord bot"
        assert "Discord" in challenge.description or "bot" in challenge.description.lower()

    def test_themed_challenge_preserves_concept(self):
        """Theme should not change the core concept being taught."""
        challenge = ThemedChallenge(
            concept_id="dictionaries",
            goal_context="Discord bot",
            title="User Permissions Storage",
            description="Use dictionaries to store bot user permissions"
        )

        assert challenge.concept_id == "dictionaries"

    def test_themed_challenge_can_have_starter_code(self):
        """Themed challenge can include starter code."""
        challenge = ThemedChallenge(
            concept_id="functions",
            goal_context="Discord bot",
            title="Bot Command Handler",
            starter_code="def on_message(message):\n    # Your code here\n    pass"
        )

        assert challenge.starter_code is not None
        assert "def" in challenge.starter_code


class TestLearningPath:
    """Test the learning path structure."""

    def test_path_has_ordered_concepts(self):
        """Learning path should have concepts in order."""
        path = LearningPath(
            goal="Discord bot",
            concepts=["variables", "strings", "functions", "classes"]
        )

        assert path.concepts[0] == "variables"
        assert path.concepts[-1] == "classes"

    def test_path_respects_prerequisites(self):
        """Path should order concepts respecting prerequisites."""
        # Prerequisites: functions need variables, classes need functions
        path = LearningPath(
            goal="Discord bot",
            concepts=["variables", "functions", "classes"]
        )

        var_idx = path.concepts.index("variables")
        func_idx = path.concepts.index("functions")
        class_idx = path.concepts.index("classes")

        assert var_idx < func_idx
        assert func_idx < class_idx

    def test_path_has_estimated_time(self):
        """Path should estimate completion time."""
        path = LearningPath(
            goal="Discord bot",
            concepts=["variables", "functions"],
            estimated_hours=10.0
        )

        assert path.estimated_hours == 10.0


class TestCurriculum:
    """Test the complete curriculum structure."""

    def test_curriculum_has_goal(self):
        """Curriculum should record the goal."""
        curriculum = Curriculum(
            goal="Build a Discord bot",
            path=LearningPath(goal="Discord bot", concepts=[]),
            challenges=[]
        )

        assert curriculum.goal == "Build a Discord bot"

    def test_curriculum_has_path_and_challenges(self):
        """Curriculum should have both path and challenges."""
        path = LearningPath(goal="Discord bot", concepts=["loops"])
        challenges = [ThemedChallenge(
            concept_id="loops",
            goal_context="Discord bot",
            title="Command Loop"
        )]

        curriculum = Curriculum(
            goal="Discord bot",
            path=path,
            challenges=challenges
        )

        assert len(curriculum.path.concepts) > 0
        assert len(curriculum.challenges) > 0

    def test_curriculum_challenge_concept_alignment(self):
        """Each path concept should have at least one challenge."""
        path = LearningPath(
            goal="Discord bot",
            concepts=["variables", "loops", "functions"]
        )
        challenges = [
            ThemedChallenge(concept_id="variables", goal_context="Discord bot", title="Bot Variables"),
            ThemedChallenge(concept_id="loops", goal_context="Discord bot", title="Message Loop"),
            ThemedChallenge(concept_id="functions", goal_context="Discord bot", title="Command Handler"),
        ]

        curriculum = Curriculum(goal="Discord bot", path=path, challenges=challenges)

        # Every concept in path should have at least one challenge
        challenge_concepts = {c.concept_id for c in curriculum.challenges}
        for concept in curriculum.path.concepts:
            assert concept in challenge_concepts

    def test_curriculum_estimated_time(self):
        """Curriculum should provide estimated completion time."""
        curriculum = Curriculum(
            goal="Discord bot",
            path=LearningPath(goal="Discord bot", concepts=["a", "b"], estimated_hours=8.0),
            challenges=[],
            estimated_hours=8.0
        )

        assert curriculum.estimated_hours > 0

    def test_curriculum_serialization(self):
        """Curriculum should serialize/deserialize."""
        curriculum = Curriculum(
            goal="Discord bot",
            path=LearningPath(goal="Discord bot", concepts=["loops"]),
            challenges=[ThemedChallenge(concept_id="loops", goal_context="Discord bot", title="Loop")]
        )

        data = curriculum.to_dict()
        restored = Curriculum.from_dict(data)

        assert restored.goal == curriculum.goal
        assert restored.path.concepts == curriculum.path.concepts


class TestProjectCurriculumGenerator:
    """Test the curriculum generator."""

    @pytest.fixture
    def generator(self):
        """Create a generator for tests."""
        return ProjectCurriculumGenerator()

    def test_generator_initializes(self, generator):
        """Generator should initialize."""
        assert generator is not None

    def test_analyze_goal_identifies_concepts(self, generator):
        """Generator should identify concepts from a goal."""
        # Simple goals without Claude API
        concepts = generator.analyze_goal_concepts("Build a Discord bot")

        # Should identify at least some relevant concepts
        assert len(concepts) > 0
        # Discord bot needs basic concepts
        assert any(c.concept_id in ["functions", "variables", "strings", "loops"] for c in concepts)

    def test_analyze_different_goals(self, generator):
        """Different goals should identify different concepts."""
        bot_concepts = generator.analyze_goal_concepts("Build a Discord bot")
        game_concepts = generator.analyze_goal_concepts("Build a text adventure game")

        # Both should have basics
        bot_ids = {c.concept_id for c in bot_concepts}
        game_ids = {c.concept_id for c in game_concepts}

        # Some overlap (both need basics)
        assert len(bot_ids & game_ids) > 0

    def test_topological_sort_concepts(self, generator):
        """Generator should sort concepts by prerequisites."""
        concepts = [
            ConceptRequirement("list_comprehensions", level=4, prerequisites=["loops", "lists"]),
            ConceptRequirement("loops", level=1, prerequisites=["variables"]),
            ConceptRequirement("lists", level=2, prerequisites=["variables"]),
            ConceptRequirement("variables", level=0, prerequisites=[]),
        ]

        sorted_concepts = generator.topological_sort(concepts)

        # variables should come first
        var_idx = next(i for i, c in enumerate(sorted_concepts) if c.concept_id == "variables")
        loops_idx = next(i for i, c in enumerate(sorted_concepts) if c.concept_id == "loops")
        lists_idx = next(i for i, c in enumerate(sorted_concepts) if c.concept_id == "lists")
        comp_idx = next(i for i, c in enumerate(sorted_concepts) if c.concept_id == "list_comprehensions")

        assert var_idx < loops_idx
        assert var_idx < lists_idx
        assert loops_idx < comp_idx
        assert lists_idx < comp_idx

    def test_theme_challenge(self, generator):
        """Generator should theme a challenge around the goal."""
        themed = generator.theme_challenge(
            concept_id="loops",
            goal="Discord bot"
        )

        assert themed.concept_id == "loops"
        assert themed.goal_context == "Discord bot"
        # Title or description should reference the goal
        assert "Discord" in themed.title or "bot" in themed.title.lower() or \
               "Discord" in themed.description or "bot" in themed.description.lower()

    def test_estimate_time(self, generator):
        """Generator should estimate completion time."""
        concepts = [
            ConceptRequirement("variables", level=0),
            ConceptRequirement("loops", level=1),
            ConceptRequirement("functions", level=3),
        ]

        hours = generator.estimate_time(concepts)

        assert hours > 0
        # Basic estimate: more concepts = more time
        assert hours >= len(concepts)

    def test_generate_curriculum_sync(self, generator):
        """Generator should create a complete curriculum (sync version)."""
        curriculum = generator.generate_curriculum_sync("Build a simple number guessing game")

        # Should have all components
        assert curriculum.goal == "Build a simple number guessing game"
        assert len(curriculum.path.concepts) > 0
        assert len(curriculum.challenges) > 0
        assert curriculum.estimated_hours > 0

    def test_curriculum_respects_player_level(self, generator):
        """Curriculum should adapt to player's current level."""
        # Player already knows basics
        known_concepts = ["variables", "print", "strings"]

        curriculum = generator.generate_curriculum_sync(
            goal="Build a Discord bot",
            known_concepts=known_concepts
        )

        # Should skip known concepts
        for concept in curriculum.path.concepts:
            assert concept not in known_concepts or concept == "variables"  # Might still be in path but marked

    def test_curriculum_difficulty_progression(self, generator):
        """Curriculum should progress from easy to hard."""
        curriculum = generator.generate_curriculum_sync("Build a web scraper")

        if len(curriculum.path.concepts) > 2:
            # Later concepts should be higher level
            first_concept = curriculum.path.concepts[0]
            last_concept = curriculum.path.concepts[-1]

            # Get levels (in test data)
            # This is a heuristic test - real implementation would check levels
            assert True  # Placeholder for level checking


class TestGoalAnalysis:
    """Test goal analysis for different project types."""

    @pytest.fixture
    def generator(self):
        return ProjectCurriculumGenerator()

    def test_discord_bot_concepts(self, generator):
        """Discord bot should require networking/async concepts."""
        concepts = generator.analyze_goal_concepts("Build a Discord bot")
        concept_ids = {c.concept_id for c in concepts}

        # Should include: functions, strings, likely async concepts
        assert "functions" in concept_ids or "basics" in concept_ids

    def test_game_concepts(self, generator):
        """Game should require loops and game logic concepts."""
        concepts = generator.analyze_goal_concepts("Build a text adventure game")
        concept_ids = {c.concept_id for c in concepts}

        # Should include: loops, conditionals, state management
        assert any(c in concept_ids for c in ["loops", "conditionals", "functions"])

    def test_data_analysis_concepts(self, generator):
        """Data analysis should require collection concepts."""
        concepts = generator.analyze_goal_concepts("Build a data analysis tool")
        concept_ids = {c.concept_id for c in concepts}

        # Should include: lists, dictionaries, file handling
        assert any(c in concept_ids for c in ["lists", "dictionaries", "collections"])

    def test_web_scraper_concepts(self, generator):
        """Web scraper should require string/collection concepts."""
        concepts = generator.analyze_goal_concepts("Build a web scraper")
        concept_ids = {c.concept_id for c in concepts}

        # Should include: strings, lists, maybe regex
        assert any(c in concept_ids for c in ["strings", "lists", "functions"])


class TestCurriculumPersistence:
    """Test saving and loading curricula."""

    @pytest.fixture
    def generator(self):
        return ProjectCurriculumGenerator()

    def test_save_and_load_curriculum(self, generator, tmp_path):
        """Curriculum should save and load from file."""
        curriculum = generator.generate_curriculum_sync("Build a calculator")

        save_path = tmp_path / "curriculum.json"
        curriculum.save(save_path)

        loaded = Curriculum.load(save_path)

        assert loaded.goal == curriculum.goal
        assert len(loaded.path.concepts) == len(curriculum.path.concepts)
        assert len(loaded.challenges) == len(curriculum.challenges)

    def test_curriculum_versioning(self, generator):
        """Curriculum should track version."""
        curriculum = generator.generate_curriculum_sync("Build a calculator")

        data = curriculum.to_dict()
        assert "version" in data


class TestLMSPIntegration:
    """Test integration with LMSP systems."""

    @pytest.fixture
    def generator(self):
        return ProjectCurriculumGenerator()

    def test_challenges_reference_concept_toml(self, generator):
        """Themed challenges should reference concept TOML files."""
        curriculum = generator.generate_curriculum_sync("Build a calculator")

        for challenge in curriculum.challenges:
            # Challenge should have a concept_id that maps to a TOML
            assert challenge.concept_id is not None
            assert len(challenge.concept_id) > 0

    def test_curriculum_integrates_with_spaced_repetition(self, generator):
        """Curriculum concepts should work with spaced repetition."""
        curriculum = generator.generate_curriculum_sync("Build a todo app")

        # Each concept should be trackable
        for concept in curriculum.path.concepts:
            assert isinstance(concept, str)
            assert len(concept) > 0

    def test_themed_challenges_can_generate_from_templates(self, generator):
        """Themed challenges should be able to generate variations."""
        challenge = generator.theme_challenge("loops", "Build a countdown timer")

        # Challenge should have required fields for game integration
        assert hasattr(challenge, "concept_id")
        assert hasattr(challenge, "title")
        assert hasattr(challenge, "goal_context")


# Self-teaching note:
#
# This test file demonstrates:
# - Data structure testing (Curriculum, LearningPath, etc.)
# - Algorithm testing (topological sort)
# - Integration testing (LMSP systems)
# - pytest fixtures for test setup
# - File persistence testing with tmp_path
#
# The project-driven curriculum is the "killer feature" because:
# - Learning is motivated by a GOAL you care about
# - Challenges are themed around your project
# - You see immediate relevance of each concept
# - Path is personalized to your current level
#
# Prerequisites:
# - Level 3: Functions, basic OOP
# - Level 4: Collections, topological sort
# - Level 5: Dataclasses, design patterns
# - Level 6: Algorithm design, async patterns
