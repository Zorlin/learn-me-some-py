"""
Tests for the Achievement System with Unlockable Badges.

Tests achievement unlocking, progress tracking, and XP rewards.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from lmsp.ui.achievements import (
    Achievement,
    AchievementType,
    AchievementTier,
    AchievementProgress,
    AchievementManager,
    achievement_manager,
)


class TestAchievementType:
    """Test achievement type enumeration."""

    def test_all_types_defined(self):
        """All achievement types should be defined."""
        required_types = [
            "MILESTONE",
            "STREAK",
            "MASTERY",
            "SPEED",
            "EXPLORATION",
            "DEDICATION",
            "COLLABORATION",
            "TEACHING",
            "PERFECTIONIST",
            "RESILIENCE",
        ]

        for type_name in required_types:
            assert hasattr(AchievementType, type_name)


class TestAchievementTier:
    """Test achievement tier system."""

    def test_all_tiers_defined(self):
        """All tiers should be defined."""
        assert hasattr(AchievementTier, "BRONZE")
        assert hasattr(AchievementTier, "SILVER")
        assert hasattr(AchievementTier, "GOLD")
        assert hasattr(AchievementTier, "PLATINUM")
        assert hasattr(AchievementTier, "DIAMOND")

    def test_tier_points_increase(self):
        """Higher tiers should have more points."""
        assert AchievementTier.BRONZE.points < AchievementTier.SILVER.points
        assert AchievementTier.SILVER.points < AchievementTier.GOLD.points
        assert AchievementTier.GOLD.points < AchievementTier.PLATINUM.points
        assert AchievementTier.PLATINUM.points < AchievementTier.DIAMOND.points

    def test_tier_has_color(self):
        """Each tier should have a color."""
        assert AchievementTier.BRONZE.color.startswith("#")
        assert AchievementTier.GOLD.color == "#FFD700"  # Gold color


class TestAchievement:
    """Test achievement dataclass."""

    def test_achievement_creation(self):
        """Should create achievement with all fields."""
        achievement = Achievement(
            id="test_achievement",
            name="Test Achievement",
            description="Test description",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=10,
            xp_reward=100,
        )

        assert achievement.id == "test_achievement"
        assert achievement.name == "Test Achievement"
        assert achievement.required_value == 10
        assert achievement.xp_reward == 100

    def test_achievement_hashable(self):
        """Achievements should be hashable for use in sets/dicts."""
        achievement = Achievement(
            id="test",
            name="Test",
            description="Test",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=1,
        )

        # Should be able to add to set
        achievement_set = {achievement}
        assert achievement in achievement_set


class TestAchievementProgress:
    """Test achievement progress tracking."""

    def test_initial_progress(self):
        """New progress should start unlocked=False."""
        progress = AchievementProgress(achievement_id="test")

        assert progress.current_value == 0
        assert progress.unlocked is False
        assert progress.unlock_date is None

    def test_progress_percent_calculation(self):
        """Should calculate progress percentage correctly."""
        progress = AchievementProgress(achievement_id="test")
        progress.current_value = 5

        percent = progress.progress_percent(required=10)
        assert percent == 50.0

    def test_progress_percent_caps_at_100(self):
        """Progress should not exceed 100%."""
        progress = AchievementProgress(achievement_id="test")
        progress.current_value = 15

        percent = progress.progress_percent(required=10)
        assert percent == 100.0


class TestAchievementManager:
    """Test achievement manager."""

    @pytest.fixture
    def manager(self):
        """Create fresh manager for each test."""
        return AchievementManager()

    def test_manager_initializes_achievements(self, manager):
        """Manager should load all achievements."""
        assert len(manager.achievements) > 0
        assert "first_steps" in manager.achievements
        assert "python_master" in manager.achievements

    def test_register_achievement(self, manager):
        """Should register new achievement."""
        custom = Achievement(
            id="custom_achievement",
            name="Custom",
            description="Test",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=1,
        )

        manager.register(custom)

        assert "custom_achievement" in manager.achievements
        assert "custom_achievement" in manager.player_progress

    def test_update_progress_increments(self, manager):
        """Should increment achievement progress."""
        # Create simple achievement
        manager.register(Achievement(
            id="test",
            name="Test",
            description="Test",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=5,
        ))

        manager.update_progress("test", increment=1)
        progress = manager.player_progress["test"]

        assert progress.current_value == 1

    def test_update_progress_unlocks_achievement(self, manager):
        """Should unlock achievement when threshold reached."""
        # Create simple achievement
        manager.register(Achievement(
            id="test",
            name="Test",
            description="Test",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=3,
        ))

        # Progress towards it
        manager.update_progress("test", increment=1)
        manager.update_progress("test", increment=1)
        result = manager.update_progress("test", increment=1)

        # Should unlock
        assert result is not None
        assert result.id == "test"
        assert manager.player_progress["test"].unlocked

    def test_update_progress_returns_none_if_unlocked(self, manager):
        """Should not unlock same achievement twice."""
        manager.register(Achievement(
            id="test",
            name="Test",
            description="Test",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=1,
        ))

        # Unlock it
        result1 = manager.update_progress("test", increment=1)
        assert result1 is not None

        # Try again
        result2 = manager.update_progress("test", increment=1)
        assert result2 is None

    def test_check_achievement_with_value(self, manager):
        """Should check achievement with absolute value."""
        manager.register(Achievement(
            id="test",
            name="Test",
            description="Test",
            type=AchievementType.STREAK,
            tier=AchievementTier.BRONZE,
            required_value=7,
        ))

        # Check with streak of 7
        result = manager.check_achievement("test", current_value=7)

        assert result is not None
        assert result.id == "test"
        assert manager.player_progress["test"].current_value == 7
        assert manager.player_progress["test"].unlocked

    def test_get_unlocked_achievements(self, manager):
        """Should return list of unlocked achievements."""
        # Unlock one
        manager.update_progress("first_steps", increment=1)

        unlocked = manager.get_unlocked()

        assert len(unlocked) == 1
        assert unlocked[0].id == "first_steps"

    def test_get_in_progress_achievements(self, manager):
        """Should return achievements with progress but not unlocked."""
        # Make some progress
        manager.update_progress("getting_started", increment=2)

        in_progress = manager.get_in_progress()

        assert len(in_progress) > 0
        achievement, progress = in_progress[0]
        assert achievement.id == "getting_started"
        assert progress.current_value == 2
        assert not progress.unlocked

    def test_get_in_progress_excludes_hidden(self, manager):
        """Should not show hidden achievements in progress."""
        # Progress a hidden achievement
        manager.update_progress("hello_world", increment=1)

        in_progress = manager.get_in_progress()

        # Should not appear
        assert not any(a.id == "hello_world" for a, p in in_progress)

    def test_get_next_achievements_sorts_by_progress(self, manager):
        """Should return closest-to-completion achievements first."""
        # Progress multiple achievements
        manager.update_progress("getting_started", increment=4)  # 4/5 = 80%
        manager.update_progress("python_apprentice", increment=5)  # 5/25 = 20%

        next_achievements = manager.get_next_achievements(limit=2)

        # getting_started should be first (higher %)
        assert next_achievements[0][0].id == "getting_started"

    def test_get_total_xp_earned(self, manager):
        """Should sum XP from unlocked achievements."""
        # Unlock a few
        manager.update_progress("first_steps", increment=1)  # 50 XP
        manager.update_progress("getting_started", increment=5)  # 100 XP

        total_xp = manager.get_total_xp_earned()

        assert total_xp == 150

    def test_get_achievement_stats(self, manager):
        """Should return statistics about achievements."""
        # Unlock one
        manager.update_progress("first_steps", increment=1)

        stats = manager.get_achievement_stats()

        assert "total" in stats
        assert "unlocked" in stats
        assert stats["unlocked"] == 1
        assert "percent" in stats
        assert "by_tier" in stats
        assert "total_xp" in stats

    def test_achievement_stats_by_tier(self, manager):
        """Should track unlocks by tier."""
        # Unlock some bronze
        manager.update_progress("first_steps", increment=1)  # Bronze

        stats = manager.get_achievement_stats()

        bronze_stats = stats["by_tier"]["bronze"]
        assert bronze_stats["unlocked"] >= 1
        assert bronze_stats["percent"] > 0

    def test_save_and_load_progress(self, manager, tmp_path):
        """Should persist achievement progress."""
        # Make progress
        manager.update_progress("first_steps", increment=1)
        manager.update_progress("getting_started", increment=3)

        # Save
        save_path = tmp_path / "achievements.json"
        manager.save(str(save_path))

        # Create new manager and load
        new_manager = AchievementManager()
        new_manager.load(str(save_path))

        # Check progress restored
        assert new_manager.player_progress["first_steps"].unlocked
        assert new_manager.player_progress["getting_started"].current_value == 3

    def test_load_nonexistent_file_gracefully(self, manager):
        """Should handle missing save file gracefully."""
        # Should not raise
        manager.load("/nonexistent/path.json")

    def test_unlock_date_recorded(self, manager):
        """Should record when achievement was unlocked."""
        before = datetime.now()

        manager.update_progress("first_steps", increment=1)

        after = datetime.now()

        progress = manager.player_progress["first_steps"]
        assert progress.unlock_date is not None
        assert before <= progress.unlock_date <= after


class TestGlobalAchievementManager:
    """Test the global achievement manager instance."""

    def test_global_instance_exists(self):
        """Should have global achievement_manager instance."""
        assert achievement_manager is not None
        assert isinstance(achievement_manager, AchievementManager)

    def test_global_instance_has_achievements(self):
        """Global instance should be initialized."""
        assert len(achievement_manager.achievements) > 0


class TestAchievementRewards:
    """Test achievement reward systems."""

    @pytest.fixture
    def manager(self):
        return AchievementManager()

    def test_xp_reward_given_on_unlock(self, manager):
        """Should give XP when unlocking."""
        manager.update_progress("first_steps", increment=1)

        total_xp = manager.get_total_xp_earned()
        assert total_xp == 50  # first_steps gives 50 XP

    def test_concept_unlock_reward(self, manager):
        """Some achievements unlock concepts."""
        # legendary_streak unlocks a concept
        achievement = manager.achievements["legendary_streak"]
        assert achievement.unlocks_concept == "async_mastery"

    def test_theme_unlock_reward(self, manager):
        """Some achievements unlock themes."""
        # python_master unlocks a theme
        achievement = manager.achievements["python_master"]
        assert achievement.unlocks_theme == "master"


class TestHiddenAchievements:
    """Test secret/hidden achievements."""

    @pytest.fixture
    def manager(self):
        return AchievementManager()

    def test_hidden_achievements_exist(self, manager):
        """Should have some hidden achievements."""
        hidden = [a for a in manager.achievements.values() if a.hidden]
        assert len(hidden) > 0

    def test_hidden_achievement_is_hello_world(self, manager):
        """hello_world should be hidden."""
        hello = manager.achievements["hello_world"]
        assert hello.hidden

    def test_hidden_achievements_not_in_progress_list(self, manager):
        """Hidden achievements should not show in get_in_progress."""
        # Make progress on hidden
        manager.update_progress("hello_world", increment=1)

        in_progress = manager.get_in_progress()

        # Should not appear
        assert not any(a.id == "hello_world" for a, p in in_progress)

    def test_hidden_achievement_still_counts_in_stats(self, manager):
        """Hidden achievements should count toward total."""
        # Unlock hidden
        manager.update_progress("hello_world", increment=1)

        stats = manager.get_achievement_stats()
        assert stats["unlocked"] >= 1


# Self-teaching note:
#
# This file demonstrates:
# - pytest fixtures for test setup
# - tmp_path fixture for file operations
# - Testing dataclasses and enums
# - Testing manager/registry patterns
# - Testing persistence (save/load)
# - Testing calculated properties
# - Testing hidden/optional features
#
# Prerequisites:
# - Level 3: Functions and classes
# - Level 4: Collections and JSON
# - Level 5: Dataclasses and enums
# - Level 6: Design patterns and testing
#
# Achievement systems like this are common in:
# - Games (Steam achievements, Xbox achievements)
# - Learning platforms (Duolingo streaks, Khan Academy badges)
# - Fitness apps (Apple Watch rings, Strava challenges)
# - Professional tools (GitHub contribution graphs)
