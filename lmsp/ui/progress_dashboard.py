"""
Progress Visualization Dashboard

Beautiful progress displays showing:
- XP progress bars with level-up animations
- Concept unlocking tree visualization
- Achievement gallery
- Streak calendars
- Skill radar charts

Self-teaching note:
This file demonstrates:
- Rich library for terminal visuals (Level 5+)
- Data visualization patterns (Level 5+)
- Layout composition (Level 6)
- Dynamic text generation (Level 4+)
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.layout import Layout

from lmsp.ui.themes import ThemeManager, ColorScheme
from lmsp.ui.achievements import AchievementManager, Achievement, AchievementTier
from lmsp.adaptive.engine import LearnerProfile


@dataclass
class ProgressStats:
    """Statistics for progress dashboard."""

    # XP and Leveling
    current_xp: int = 0
    current_level: int = 1
    xp_to_next_level: int = 100

    # Concepts
    concepts_unlocked: int = 0
    concepts_total: int = 52  # From Phase 1
    concepts_mastered: int = 0

    # Challenges
    challenges_completed: int = 0
    challenges_total: int = 60  # Estimated
    tests_passed: int = 0
    tests_attempted: int = 0

    # Streaks
    current_streak: int = 0
    longest_streak: int = 0

    # Achievements
    achievements_unlocked: int = 0
    achievements_total: int = 20  # From achievement system

    # Time
    total_time_hours: float = 0.0
    session_count: int = 0


class ProgressDashboard:
    """
    Renders beautiful progress visualizations.

    Shows player progress in multiple dimensions:
    - XP and leveling
    - Concept mastery
    - Achievement completion
    - Skill development

    Usage:
        dashboard = ProgressDashboard(console, theme_manager)
        dashboard.render(profile, achievement_manager)
    """

    def __init__(
        self,
        console: Console,
        theme_manager: Optional[ThemeManager] = None
    ):
        """
        Create a progress dashboard.

        Args:
            console: Rich console for rendering
            theme_manager: Optional theme manager
        """
        self.console = console
        self.theme_manager = theme_manager

    def get_colors(self) -> ColorScheme:
        """Get current color scheme."""
        if self.theme_manager:
            return self.theme_manager.get_colors()

        # Default colors
        from lmsp.ui.themes import THEMES, ThemeType
        return THEMES[ThemeType.CYBERPUNK]

    def render(
        self,
        profile: LearnerProfile,
        achievement_manager: AchievementManager,
        stats: Optional[ProgressStats] = None
    ):
        """
        Render the complete dashboard.

        Args:
            profile: Player profile
            achievement_manager: Achievement manager
            stats: Optional pre-computed stats
        """
        if stats is None:
            stats = self._compute_stats(profile, achievement_manager)

        colors = self.get_colors()

        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        # Render sections
        layout["header"].update(self._render_header(profile, stats, colors))
        layout["left"].update(self._render_left_column(profile, stats, colors))
        layout["right"].update(self._render_right_column(achievement_manager, stats, colors))
        layout["footer"].update(self._render_footer(stats, colors))

        self.console.print(layout)

    def _compute_stats(
        self,
        profile: LearnerProfile,
        achievement_manager: AchievementManager
    ) -> ProgressStats:
        """Compute statistics from profile and achievements."""

        # Get achievement stats
        ach_stats = achievement_manager.get_achievement_stats()

        return ProgressStats(
            current_xp=profile.total_xp,
            current_level=profile.level,
            xp_to_next_level=profile.xp_for_next_level(),
            concepts_unlocked=len(profile.unlocked_concepts),
            concepts_mastered=len([c for c, mastery in profile.concept_mastery.items() if mastery > 0.8]),
            challenges_completed=profile.challenges_completed,
            tests_passed=profile.tests_passed,
            tests_attempted=profile.tests_attempted,
            current_streak=profile.current_streak,
            longest_streak=profile.longest_streak,
            achievements_unlocked=ach_stats["unlocked"],
            achievements_total=ach_stats["total"],
            total_time_hours=profile.total_time_minutes / 60.0,
            session_count=len(profile.session_history),
        )

    def _render_header(
        self,
        profile: LearnerProfile,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Panel:
        """Render dashboard header."""

        text = Text()
        text.append("LMSP Progress Dashboard", style=f"bold {colors.primary_text}")
        text.append(f" | Player: ", style=colors.secondary_text)
        text.append(profile.player_id, style=f"bold {colors.highlight_text}")
        text.append(f" | Level {stats.current_level}", style=f"bold {colors.xp_bar}")

        return Panel(
            text,
            style=colors.panel,
            border_style=colors.accent_1
        )

    def _render_left_column(
        self,
        profile: LearnerProfile,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Layout:
        """Render left column with XP and concepts."""

        layout = Layout()
        layout.split_column(
            Layout(self._render_xp_progress(stats, colors), size=7),
            Layout(self._render_concept_progress(stats, colors), size=12),
            Layout(self._render_streak_calendar(stats, colors)),
        )

        return layout

    def _render_right_column(
        self,
        achievement_manager: AchievementManager,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Layout:
        """Render right column with achievements and skills."""

        layout = Layout()
        layout.split_column(
            Layout(self._render_achievement_summary(achievement_manager, colors), size=12),
            Layout(self._render_skill_breakdown(stats, colors)),
        )

        return layout

    def _render_xp_progress(
        self,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Panel:
        """Render XP progress bar."""

        # Calculate progress percentage
        progress_pct = (stats.current_xp / stats.xp_to_next_level) * 100

        # Create progress bar
        bar_width = 40
        filled = int((progress_pct / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        text = Text()
        text.append("XP Progress\n", style=f"bold {colors.primary_text}")
        text.append(f"Level {stats.current_level}\n", style=f"bold {colors.xp_bar}")
        text.append(bar, style=colors.xp_bar)
        text.append(f"\n{stats.current_xp} / {stats.xp_to_next_level} XP", style=colors.secondary_text)
        text.append(f" ({progress_pct:.0f}%)", style=colors.dim_text)

        return Panel(
            text,
            title="⭐ Experience",
            style=colors.panel,
            border_style=colors.xp_bar
        )

    def _render_concept_progress(
        self,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Panel:
        """Render concept unlocking progress."""

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Label", style=colors.secondary_text)
        table.add_column("Value", style=colors.primary_text, justify="right")

        # Calculate percentages
        unlocked_pct = (stats.concepts_unlocked / stats.concepts_total) * 100
        mastered_pct = (stats.concepts_mastered / stats.concepts_total) * 100

        table.add_row("Unlocked:", f"{stats.concepts_unlocked}/{stats.concepts_total} ({unlocked_pct:.0f}%)")
        table.add_row("Mastered:", f"{stats.concepts_mastered}/{stats.concepts_total} ({mastered_pct:.0f}%)")
        table.add_row("", "")
        table.add_row("Challenges:", f"{stats.challenges_completed}/{stats.challenges_total}")
        table.add_row("Tests Passed:", f"{stats.tests_passed}/{stats.tests_attempted}")

        return Panel(
            table,
            title="📚 Concepts & Challenges",
            style=colors.panel,
            border_style=colors.accent_2
        )

    def _render_streak_calendar(
        self,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Panel:
        """Render streak calendar visualization."""

        text = Text()
        text.append(f"Current Streak: ", style=colors.secondary_text)
        text.append(f"{stats.current_streak} days", style=f"bold {colors.streak_glow}")

        if stats.current_streak > 0:
            # Show fire emoji for streaks
            fire_count = min(stats.current_streak // 3, 5)
            text.append(" " + "🔥" * fire_count)

        text.append("\n")
        text.append(f"Longest Streak: ", style=colors.secondary_text)
        text.append(f"{stats.longest_streak} days", style=colors.highlight_text)

        # Simple calendar visualization (last 7 days)
        text.append("\n\nLast 7 Days:\n", style=colors.dim_text)

        # Placeholder calendar
        for day in range(7):
            # In real implementation, check if practiced that day
            practiced = day < stats.current_streak
            symbol = "✓" if practiced else "○"
            color = colors.success if practiced else colors.dim_text
            text.append(symbol + " ", style=color)

        return Panel(
            text,
            title="🔥 Practice Streak",
            style=colors.panel,
            border_style=colors.streak_glow
        )

    def _render_achievement_summary(
        self,
        achievement_manager: AchievementManager,
        colors: ColorScheme
    ) -> Panel:
        """Render achievement summary."""

        unlocked = achievement_manager.get_unlocked()
        in_progress = achievement_manager.get_next_achievements(limit=3)

        text = Text()

        # Unlocked count
        total = len(achievement_manager.achievements)
        unlocked_count = len(unlocked)
        text.append(f"Unlocked: {unlocked_count}/{total}\n\n", style=f"bold {colors.primary_text}")

        # Recent unlocks
        if unlocked:
            text.append("Recent Unlocks:\n", style=colors.secondary_text)
            for achievement in unlocked[-3:]:
                tier_color = achievement.tier.color
                text.append(f"{achievement.icon} ", style=tier_color)
                text.append(f"{achievement.name}\n", style=colors.primary_text)

        # Next achievements
        text.append("\nNext Goals:\n", style=colors.secondary_text)
        for achievement, progress in in_progress:
            percent = progress.progress_percent(achievement.required_value)
            text.append(f"{achievement.icon} ", style=achievement.tier.color)
            text.append(f"{achievement.name} ", style=colors.primary_text)
            text.append(f"({percent:.0f}%)\n", style=colors.dim_text)

        return Panel(
            text,
            title="🏆 Achievements",
            style=colors.panel,
            border_style=colors.achievement
        )

    def _render_skill_breakdown(
        self,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Panel:
        """Render skill breakdown stats."""

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Skill", style=colors.secondary_text)
        table.add_column("Value", style=colors.primary_text, justify="right")

        # Calculate success rate
        success_rate = 0.0
        if stats.tests_attempted > 0:
            success_rate = (stats.tests_passed / stats.tests_attempted) * 100

        # Calculate avg time per session
        avg_time = 0.0
        if stats.session_count > 0:
            avg_time = (stats.total_time_hours * 60) / stats.session_count

        table.add_row("Success Rate:", f"{success_rate:.1f}%")
        table.add_row("Total Time:", f"{stats.total_time_hours:.1f}h")
        table.add_row("Sessions:", f"{stats.session_count}")
        table.add_row("Avg Session:", f"{avg_time:.0f}min")

        return Panel(
            table,
            title="📊 Statistics",
            style=colors.panel,
            border_style=colors.info
        )

    def _render_footer(
        self,
        stats: ProgressStats,
        colors: ColorScheme
    ) -> Panel:
        """Render dashboard footer."""

        text = Text()
        text.append("Press ", style=colors.dim_text)
        text.append("[T]", style=f"bold {colors.highlight_text}")
        text.append(" to cycle themes | ", style=colors.dim_text)
        text.append("[A]", style=f"bold {colors.highlight_text}")
        text.append(" for achievements | ", style=colors.dim_text)
        text.append("[Q]", style=f"bold {colors.highlight_text}")
        text.append(" to return", style=colors.dim_text)

        return Panel(
            text,
            style=colors.panel,
            border_style=colors.dim_text
        )

    def render_compact(
        self,
        profile: LearnerProfile,
        achievement_manager: AchievementManager
    ):
        """Render a compact version of the dashboard."""

        stats = self._compute_stats(profile, achievement_manager)
        colors = self.get_colors()

        # Simple single-line progress summary
        text = Text()
        text.append(f"Level {stats.current_level} ", style=f"bold {colors.xp_bar}")
        text.append(f"| {stats.concepts_unlocked}/{stats.concepts_total} concepts ", style=colors.primary_text)
        text.append(f"| {stats.achievements_unlocked}/{stats.achievements_total} achievements ", style=colors.achievement)
        text.append(f"| {stats.current_streak}🔥 streak", style=colors.streak_glow)

        self.console.print(Panel(
            text,
            title="Progress",
            style=colors.panel,
            border_style=colors.accent_1
        ))


# Self-teaching note:
#
# This file demonstrates:
# - Rich library for beautiful terminal UIs
# - Layout composition (splitting screen into regions)
# - Data visualization (progress bars, tables, charts)
# - Color scheme integration
# - Statistics calculation and display
#
# Prerequisites:
# - Level 4: Calculations, percentages
# - Level 5: Classes, dataclasses
# - Level 6: Rich library, composition
#
# Progress dashboards like this are common in:
# - Learning platforms (Duolingo, Khan Academy)
# - Games (RPGs with character stats)
# - Fitness apps (Apple Fitness, Strava)
# - Developer tools (GitHub contribution graphs)
