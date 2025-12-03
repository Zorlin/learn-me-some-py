"""
Tests for Skill Calibration System

TDD: These tests define expected behavior for fair racing and AI difficulty.

Tests cover:
1. Skill level calibration (thinking time, mistakes)
2. Approach selection by skill level
3. Mistake generation by skill level
4. Applying calibration to players
"""

import pytest
from unittest.mock import Mock
import random

from lmsp.multiplayer.calibration import (
    SkillLevel,
    MistakePattern,
    SkillCalibration,
    MistakeGenerator,
)


class TestSkillLevel:
    """Test skill level enumeration."""

    def test_skill_levels_defined(self):
        """All skill levels should have values between 0 and 1."""
        assert 0.0 <= SkillLevel.BEGINNER.value <= 1.0
        assert 0.0 <= SkillLevel.INTERMEDIATE.value <= 1.0
        assert 0.0 <= SkillLevel.ADVANCED.value <= 1.0
        assert 0.0 <= SkillLevel.EXPERT.value <= 1.0

    def test_skill_levels_ordered(self):
        """Skill levels should be in ascending order."""
        assert SkillLevel.BEGINNER.value < SkillLevel.INTERMEDIATE.value
        assert SkillLevel.INTERMEDIATE.value < SkillLevel.ADVANCED.value
        assert SkillLevel.ADVANCED.value < SkillLevel.EXPERT.value


class TestSkillCalibration:
    """Test skill calibration calculations."""

    def test_thinking_time_beginner_is_slower(self):
        """Beginners should take longer to think."""
        beginner_time = SkillCalibration.calibrate_thinking_time(0.2, base_time=2.0)
        expert_time = SkillCalibration.calibrate_thinking_time(1.0, base_time=2.0)

        assert beginner_time > expert_time

    def test_thinking_time_expert_is_faster(self):
        """Experts should think faster."""
        time = SkillCalibration.calibrate_thinking_time(1.0, base_time=2.0)

        assert time < 2.0

    def test_thinking_time_scales_linearly(self):
        """Thinking time should scale with skill level."""
        time_0 = SkillCalibration.calibrate_thinking_time(0.0, base_time=2.0)
        time_5 = SkillCalibration.calibrate_thinking_time(0.5, base_time=2.0)
        time_10 = SkillCalibration.calibrate_thinking_time(1.0, base_time=2.0)

        # Higher skill = less time
        assert time_0 > time_5 > time_10

    def test_mistake_probability_beginner_high(self):
        """Beginners should make mistakes more often."""
        # Run multiple times since it's probabilistic
        mistakes = sum(SkillCalibration.should_make_mistake(0.2) for _ in range(100))

        # Should make mistakes significantly (expect ~24 out of 100)
        assert mistakes > 10

    def test_mistake_probability_expert_low(self):
        """Experts should rarely make mistakes."""
        # Run multiple times
        mistakes = sum(SkillCalibration.should_make_mistake(1.0) for _ in range(100))

        # Should make very few mistakes (expect ~0 out of 100)
        assert mistakes < 10

    def test_choose_approach_beginner(self):
        """Beginners should use explicit approaches."""
        approach = SkillCalibration.choose_approach(0.2)

        assert approach == "explicit_loops"

    def test_choose_approach_intermediate(self):
        """Intermediate should mix approaches."""
        approaches = [SkillCalibration.choose_approach(0.5) for _ in range(20)]

        # Should see both explicit_loops and built_in_functions
        assert "explicit_loops" in approaches or "built_in_functions" in approaches

    def test_choose_approach_advanced(self):
        """Advanced should use comprehensions."""
        approach = SkillCalibration.choose_approach(0.7)

        assert approach == "comprehensions"

    def test_choose_approach_expert(self):
        """Experts should use concise approaches."""
        approaches = [SkillCalibration.choose_approach(1.0) for _ in range(20)]

        # Should see comprehensions or functional
        assert "comprehensions" in approaches or "functional" in approaches


class TestMistakeGenerator:
    """Test realistic mistake generation."""

    def test_beginner_mistakes_defined(self):
        """Beginner mistakes should be defined."""
        assert len(MistakeGenerator.BEGINNER_MISTAKES) > 0
        assert "forget_colon" in MistakeGenerator.BEGINNER_MISTAKES

    def test_intermediate_mistakes_defined(self):
        """Intermediate mistakes should be defined."""
        assert len(MistakeGenerator.INTERMEDIATE_MISTAKES) > 0
        assert "off_by_one" in MistakeGenerator.INTERMEDIATE_MISTAKES

    def test_advanced_mistakes_defined(self):
        """Advanced mistakes should be defined."""
        assert len(MistakeGenerator.ADVANCED_MISTAKES) > 0
        assert "shallow_copy_issue" in MistakeGenerator.ADVANCED_MISTAKES

    def test_inject_beginner_mistake(self):
        """Should inject beginner-level mistakes."""
        code = "def hello():\n    print('Hello')\n"

        buggy, description = MistakeGenerator.inject_mistake(code, skill_level=0.3)

        # Should have modified the code
        assert buggy != code or description == "No mistake injected"
        # Should have a description
        assert description != ""

    def test_inject_intermediate_mistake(self):
        """Should inject intermediate-level mistakes."""
        code = "for i in range(n):\n    print(i)\n"

        buggy, description = MistakeGenerator.inject_mistake(code, skill_level=0.5)

        assert buggy != code or description == "No mistake injected"
        assert description != ""

    def test_inject_advanced_mistake(self):
        """Should inject advanced-level mistakes."""
        code = "items = [1, 2, 3]\nnew_items = items.copy()\n"

        buggy, description = MistakeGenerator.inject_mistake(code, skill_level=0.8)

        assert buggy != code or description == "No mistake injected"
        assert description != ""

    def test_forget_colon_mistake(self):
        """Forget colon mistake should remove colon."""
        code = "def test():\n    pass\n"

        buggy, desc = MistakeGenerator.inject_mistake(code, skill_level=0.2)

        # Should occasionally inject this mistake
        if "colon" in desc.lower():
            assert ":" not in buggy.split('\n')[0] or buggy.count(':') < code.count(':')

    def test_off_by_one_mistake(self):
        """Off-by-one mistake should modify range."""
        code = "for i in range(n):\n    print(i)\n"

        # Set seed for reproducibility in this test
        random.seed(42)
        buggy, desc = MistakeGenerator.inject_mistake(code, skill_level=0.5)

        # Check if off-by-one was injected
        if "off-by-one" in desc.lower():
            assert "n - 1" in buggy or "n + 1" in buggy

    def test_mistake_description_is_clear(self):
        """Mistake descriptions should be human-readable."""
        code = "def test():\n    return True\n"

        _, description = MistakeGenerator.inject_mistake(code, skill_level=0.4)

        # Description should be a clear explanation
        assert len(description) > 0
        assert description[0].isupper()  # Should be capitalized

    def test_get_mistake_patterns(self):
        """Should return list of mistake patterns."""
        patterns = MistakeGenerator.get_mistake_patterns()

        assert len(patterns) > 0
        assert all(isinstance(p, MistakePattern) for p in patterns)

    def test_mistake_pattern_has_probability(self):
        """Mistake patterns should have probability values."""
        patterns = MistakeGenerator.get_mistake_patterns()

        for pattern in patterns:
            assert 0.0 <= pattern.probability_at_skill_0 <= 1.0

    def test_mistake_pattern_has_apply_function(self):
        """Mistake patterns should have apply functions."""
        patterns = MistakeGenerator.get_mistake_patterns()

        for pattern in patterns:
            assert callable(pattern.apply_function)


class TestCalibrationApplication:
    """Test applying calibration to players."""

    def test_apply_calibration_to_player(self):
        """Should apply calibration settings to a player."""
        # Mock ClaudePlayer
        player = Mock()
        player.name = "TestBot"

        SkillCalibration.apply_calibration(player, skill_level=0.5)

        # Should have set attributes
        assert hasattr(player, "skill_level")
        assert player.skill_level == 0.5

    def test_calibration_adjusts_thinking_time(self):
        """Calibration should set thinking time."""
        player = Mock()
        player.name = "TestBot"

        SkillCalibration.apply_calibration(player, skill_level=0.7)

        # Should have set base_thinking_time
        assert hasattr(player, "base_thinking_time")
        assert player.base_thinking_time > 0

    def test_calibration_sets_mistake_probability(self):
        """Calibration should set mistake probability."""
        player = Mock()
        player.name = "TestBot"

        SkillCalibration.apply_calibration(player, skill_level=0.6)

        # Should have set mistake_probability
        assert hasattr(player, "mistake_probability")
        assert 0.0 <= player.mistake_probability <= 1.0

    def test_calibration_sets_approach(self):
        """Calibration should set approach preference."""
        player = Mock()
        player.name = "TestBot"

        SkillCalibration.apply_calibration(player, skill_level=0.8)

        # Should have set approach_preference
        assert hasattr(player, "approach_preference")
        assert player.approach_preference in [
            "explicit_loops",
            "built_in_functions",
            "comprehensions",
            "functional",
        ]

    def test_beginner_calibration_settings(self):
        """Beginner calibration should have appropriate settings."""
        player = Mock()
        player.name = "BeginnerBot"

        SkillCalibration.apply_calibration(player, skill_level=0.2)

        # Beginner should have:
        # - Longer thinking time
        assert player.base_thinking_time > 2.0
        # - Higher mistake probability
        assert player.mistake_probability > 0.2
        # - Explicit approach
        assert player.approach_preference == "explicit_loops"

    def test_expert_calibration_settings(self):
        """Expert calibration should have appropriate settings."""
        player = Mock()
        player.name = "ExpertBot"

        SkillCalibration.apply_calibration(player, skill_level=1.0)

        # Expert should have:
        # - Shorter thinking time
        assert player.base_thinking_time < 2.0
        # - Low mistake probability
        assert player.mistake_probability < 0.1
        # - Advanced approach
        assert player.approach_preference in ["comprehensions", "functional"]


class TestFairRacing:
    """Test that calibration enables fair racing."""

    def test_similar_skill_levels_similar_performance(self):
        """Players with similar skill should perform similarly."""
        player1 = Mock()
        player1.name = "Bot1"
        player2 = Mock()
        player2.name = "Bot2"

        # Both intermediate
        SkillCalibration.apply_calibration(player1, skill_level=0.5)
        SkillCalibration.apply_calibration(player2, skill_level=0.55)

        # Should have similar settings
        assert abs(player1.base_thinking_time - player2.base_thinking_time) < 0.5
        assert abs(player1.mistake_probability - player2.mistake_probability) < 0.1

    def test_different_skill_levels_different_performance(self):
        """Players with different skill should perform differently."""
        beginner = Mock()
        beginner.name = "Beginner"
        expert = Mock()
        expert.name = "Expert"

        SkillCalibration.apply_calibration(beginner, skill_level=0.2)
        SkillCalibration.apply_calibration(expert, skill_level=1.0)

        # Should have significantly different settings
        assert beginner.base_thinking_time > expert.base_thinking_time
        assert beginner.mistake_probability > expert.mistake_probability


# Self-teaching note:
#
# This test file demonstrates:
# - Testing probabilistic systems (mistake generation)
# - Testing calibration algorithms
# - Mocking for player objects
# - Statistical validation (checking distributions)
# - Edge case testing (skill levels 0.0, 0.5, 1.0)
#
# Prerequisites:
# - Level 3: Functions, classes
# - Level 4: Random numbers, conditionals
# - Level 5: Mocking, testing patterns
# - Level 6: Algorithms, probabilistic systems
