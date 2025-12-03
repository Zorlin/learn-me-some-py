"""
Achievement System with Unlockable Badges.

Provides progression motivation through achievements, badges, and rewards.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime
import json


class AchievementType(Enum):
    """Types of achievements."""
    MILESTONE = "milestone"  # Complete X challenges
    STREAK = "streak"  # X days in a row
    MASTERY = "mastery"  # Perfect score on X challenges
    SPEED = "speed"  # Complete challenge in under X seconds
    EXPLORATION = "exploration"  # Unlock X concepts
    DEDICATION = "dedication"  # Total time spent
    COLLABORATION = "collaboration"  # Multiplayer achievements
    TEACHING = "teaching"  # Help others (multiplayer)
    PERFECTIONIST = "perfectionist"  # No hints/attempts
    RESILIENCE = "resilience"  # Complete after many failures


class AchievementTier(Enum):
    """Achievement difficulty tiers."""
    BRONZE = ("bronze", "#CD7F32", 1)
    SILVER = ("silver", "#C0C0C0", 2)
    GOLD = ("gold", "#FFD700", 3)
    PLATINUM = ("platinum", "#E5E4E2", 4)
    DIAMOND = ("diamond", "#B9F2FF", 5)

    def __init__(self, tier_name: str, color: str, points: int):
        self.tier_name = tier_name
        self.color = color
        self.points = points


@dataclass
class Achievement:
    """An unlockable achievement."""
    id: str
    name: str
    description: str
    type: AchievementType
    tier: AchievementTier

    # Requirements
    required_value: int  # What to reach (e.g., 10 challenges, 7 days streak)
    hidden: bool = False  # Secret achievements

    # Rewards
    xp_reward: int = 0
    unlocks_concept: Optional[str] = None  # Unlock special concept
    unlocks_theme: Optional[str] = None  # Unlock special theme

    # Display
    icon: str = "🏆"
    emoji: str = "⭐"

    def __hash__(self):
        return hash(self.id)


@dataclass
class AchievementProgress:
    """Progress toward an achievement."""
    achievement_id: str
    current_value: int = 0
    unlocked: bool = False
    unlock_date: Optional[datetime] = None

    def progress_percent(self, required: int) -> float:
        """Calculate progress percentage."""
        return min(100.0, (self.current_value / required) * 100.0)


class AchievementManager:
    """Manages achievements, progress tracking, and rewards."""

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.player_progress: Dict[str, AchievementProgress] = {}
        self._initialize_achievements()

    def _initialize_achievements(self):
        """Initialize all achievement definitions."""

        # Milestone achievements
        self.register(Achievement(
            id="first_steps",
            name="First Steps",
            description="Complete your first challenge",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=1,
            icon="👣",
            emoji="🎯",
            xp_reward=50,
        ))

        self.register(Achievement(
            id="getting_started",
            name="Getting Started",
            description="Complete 5 challenges",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=5,
            icon="🚀",
            xp_reward=100,
        ))

        self.register(Achievement(
            id="python_apprentice",
            name="Python Apprentice",
            description="Complete 25 challenges",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.SILVER,
            required_value=25,
            icon="🐍",
            xp_reward=250,
        ))

        self.register(Achievement(
            id="python_journeyman",
            name="Python Journeyman",
            description="Complete 100 challenges",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.GOLD,
            required_value=100,
            icon="🐉",
            xp_reward=1000,
        ))

        self.register(Achievement(
            id="python_master",
            name="Python Master",
            description="Complete 500 challenges",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.PLATINUM,
            required_value=500,
            icon="👑",
            xp_reward=5000,
            unlocks_theme="master",
        ))

        # Streak achievements
        self.register(Achievement(
            id="consistent",
            name="Consistent",
            description="Practice 3 days in a row",
            type=AchievementType.STREAK,
            tier=AchievementTier.BRONZE,
            required_value=3,
            icon="📅",
            xp_reward=150,
        ))

        self.register(Achievement(
            id="dedicated",
            name="Dedicated",
            description="Practice 7 days in a row",
            type=AchievementType.STREAK,
            tier=AchievementTier.SILVER,
            required_value=7,
            icon="🔥",
            xp_reward=350,
        ))

        self.register(Achievement(
            id="unstoppable",
            name="Unstoppable",
            description="Practice 30 days in a row",
            type=AchievementType.STREAK,
            tier=AchievementTier.GOLD,
            required_value=30,
            icon="⚡",
            xp_reward=1500,
            unlocks_theme="fire",
        ))

        self.register(Achievement(
            id="legendary_streak",
            name="Legendary Streak",
            description="Practice 100 days in a row",
            type=AchievementType.STREAK,
            tier=AchievementTier.DIAMOND,
            required_value=100,
            icon="💎",
            xp_reward=10000,
            unlocks_concept="async_mastery",
        ))

        # Mastery achievements
        self.register(Achievement(
            id="perfectionist",
            name="Perfectionist",
            description="Get perfect score on 10 challenges",
            type=AchievementType.MASTERY,
            tier=AchievementTier.SILVER,
            required_value=10,
            icon="💯",
            xp_reward=500,
        ))

        self.register(Achievement(
            id="flawless_victory",
            name="Flawless Victory",
            description="Get perfect score on 50 challenges",
            type=AchievementType.MASTERY,
            tier=AchievementTier.GOLD,
            required_value=50,
            icon="🌟",
            xp_reward=2500,
        ))

        # Speed achievements
        self.register(Achievement(
            id="speedrunner",
            name="Speedrunner",
            description="Complete a challenge in under 30 seconds",
            type=AchievementType.SPEED,
            tier=AchievementTier.BRONZE,
            required_value=30,
            icon="⚡",
            xp_reward=200,
        ))

        self.register(Achievement(
            id="lightning_fast",
            name="Lightning Fast",
            description="Complete 10 challenges in under 1 minute each",
            type=AchievementType.SPEED,
            tier=AchievementTier.SILVER,
            required_value=10,
            icon="⚡",
            xp_reward=750,
        ))

        # Exploration achievements
        self.register(Achievement(
            id="explorer",
            name="Explorer",
            description="Unlock 10 concepts",
            type=AchievementType.EXPLORATION,
            tier=AchievementTier.BRONZE,
            required_value=10,
            icon="🗺️",
            xp_reward=200,
        ))

        self.register(Achievement(
            id="knowledge_seeker",
            name="Knowledge Seeker",
            description="Unlock 50 concepts",
            type=AchievementType.EXPLORATION,
            tier=AchievementTier.GOLD,
            required_value=50,
            icon="📚",
            xp_reward=1000,
        ))

        # Resilience achievements
        self.register(Achievement(
            id="never_give_up",
            name="Never Give Up",
            description="Complete a challenge after 10+ attempts",
            type=AchievementType.RESILIENCE,
            tier=AchievementTier.SILVER,
            required_value=10,
            icon="💪",
            xp_reward=400,
        ))

        self.register(Achievement(
            id="unbreakable",
            name="Unbreakable",
            description="Complete 5 challenges after 10+ attempts each",
            type=AchievementType.RESILIENCE,
            tier=AchievementTier.GOLD,
            required_value=5,
            icon="🛡️",
            xp_reward=1200,
        ))

        # Secret achievements
        self.register(Achievement(
            id="hello_world",
            name="Hello, World!",
            description="Write your first print statement",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.BRONZE,
            required_value=1,
            hidden=True,
            icon="👋",
            xp_reward=10,
        ))

        self.register(Achievement(
            id="bug_hunter",
            name="Bug Hunter",
            description="Fix 100 syntax errors",
            type=AchievementType.MILESTONE,
            tier=AchievementTier.SILVER,
            required_value=100,
            hidden=True,
            icon="🐛",
            xp_reward=500,
        ))

        self.register(Achievement(
            id="night_owl",
            name="Night Owl",
            description="Complete 10 challenges between midnight and 4am",
            type=AchievementType.DEDICATION,
            tier=AchievementTier.BRONZE,
            required_value=10,
            hidden=True,
            icon="🦉",
            xp_reward=300,
        ))

    def register(self, achievement: Achievement):
        """Register an achievement."""
        self.achievements[achievement.id] = achievement
        if achievement.id not in self.player_progress:
            self.player_progress[achievement.id] = AchievementProgress(
                achievement_id=achievement.id
            )

    def update_progress(self, achievement_id: str, increment: int = 1) -> Optional[Achievement]:
        """
        Update progress toward an achievement.

        Returns the achievement if it was just unlocked, None otherwise.
        """
        if achievement_id not in self.achievements:
            return None

        achievement = self.achievements[achievement_id]
        progress = self.player_progress[achievement_id]

        if progress.unlocked:
            return None  # Already unlocked

        progress.current_value += increment

        if progress.current_value >= achievement.required_value:
            progress.unlocked = True
            progress.unlock_date = datetime.now()
            return achievement

        return None

    def check_achievement(self, achievement_id: str, current_value: int) -> Optional[Achievement]:
        """
        Check if achievement should unlock based on current value.

        Returns the achievement if unlocked, None otherwise.
        """
        if achievement_id not in self.achievements:
            return None

        achievement = self.achievements[achievement_id]
        progress = self.player_progress[achievement_id]

        if progress.unlocked:
            return None

        progress.current_value = current_value

        if current_value >= achievement.required_value:
            progress.unlocked = True
            progress.unlock_date = datetime.now()
            return achievement

        return None

    def get_unlocked(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [
            self.achievements[aid]
            for aid, progress in self.player_progress.items()
            if progress.unlocked
        ]

    def get_in_progress(self) -> List[tuple[Achievement, AchievementProgress]]:
        """Get achievements currently in progress."""
        result = []
        for aid, progress in self.player_progress.items():
            if not progress.unlocked and progress.current_value > 0:
                achievement = self.achievements[aid]
                if not achievement.hidden:  # Don't show hidden achievements in progress
                    result.append((achievement, progress))
        return result

    def get_next_achievements(self, limit: int = 5) -> List[tuple[Achievement, AchievementProgress]]:
        """Get next achievements the player should work toward."""
        in_progress = self.get_in_progress()

        # Sort by progress percentage (closest to completion first)
        in_progress.sort(
            key=lambda x: x[1].progress_percent(x[0].required_value),
            reverse=True
        )

        return in_progress[:limit]

    def get_total_xp_earned(self) -> int:
        """Calculate total XP from unlocked achievements."""
        return sum(
            self.achievements[aid].xp_reward
            for aid, progress in self.player_progress.items()
            if progress.unlocked
        )

    def get_achievement_stats(self) -> dict:
        """Get statistics about achievements."""
        total = len(self.achievements)
        unlocked = len([p for p in self.player_progress.values() if p.unlocked])

        by_tier = {}
        for tier in AchievementTier:
            tier_total = len([a for a in self.achievements.values() if a.tier == tier])
            tier_unlocked = len([
                aid for aid, progress in self.player_progress.items()
                if progress.unlocked and self.achievements[aid].tier == tier
            ])
            by_tier[tier.tier_name] = {
                "total": tier_total,
                "unlocked": tier_unlocked,
                "percent": (tier_unlocked / tier_total * 100) if tier_total > 0 else 0
            }

        return {
            "total": total,
            "unlocked": unlocked,
            "percent": (unlocked / total * 100) if total > 0 else 0,
            "by_tier": by_tier,
            "total_xp": self.get_total_xp_earned(),
        }

    def save(self, filepath: str):
        """Save achievement progress to file."""
        data = {
            "progress": {
                aid: {
                    "current_value": p.current_value,
                    "unlocked": p.unlocked,
                    "unlock_date": p.unlock_date.isoformat() if p.unlock_date else None,
                }
                for aid, p in self.player_progress.items()
            }
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str):
        """Load achievement progress from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            for aid, progress_data in data.get("progress", {}).items():
                if aid in self.player_progress:
                    progress = self.player_progress[aid]
                    progress.current_value = progress_data.get("current_value", 0)
                    progress.unlocked = progress_data.get("unlocked", False)

                    unlock_date_str = progress_data.get("unlock_date")
                    if unlock_date_str:
                        progress.unlock_date = datetime.fromisoformat(unlock_date_str)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # No saved progress yet


# ============================================================================
# GORGEOUS CELEBRATION & VISUALIZATION FUNCTIONS
# ============================================================================
# These functions create dopamine-triggering visual celebrations when
# achievements are unlocked. They use Rich to create animated, colorful
# displays that make achievement unlocking FEEL AMAZING.

def _interpolate_color(color1: str, color2: str, progress: float) -> str:
    """Interpolate between two hex colors based on progress (0.0 to 1.0)."""
    # Convert hex to RGB
    r1 = int(color1[1:3], 16)
    g1 = int(color1[3:5], 16)
    b1 = int(color1[5:7], 16)

    r2 = int(color2[1:3], 16)
    g2 = int(color2[3:5], 16)
    b2 = int(color2[5:7], 16)

    # Interpolate
    r = int(r1 + (r2 - r1) * progress)
    g = int(g1 + (g2 - g1) * progress)
    b = int(b1 + (b2 - b1) * progress)

    return f"#{r:02x}{g:02x}{b:02x}"


def _get_tier_color_gradient(tier: AchievementTier) -> List[str]:
    """Get a color gradient for an achievement tier."""
    # Gradients from darker to lighter version of tier color
    gradients = {
        AchievementTier.BRONZE: ["#8B4513", "#CD7F32", "#DEB887"],
        AchievementTier.SILVER: ["#707070", "#C0C0C0", "#E8E8E8"],
        AchievementTier.GOLD: ["#B8860B", "#FFD700", "#FFED4E"],
        AchievementTier.PLATINUM: ["#999999", "#E5E4E2", "#F5F5F0"],
        AchievementTier.DIAMOND: ["#00D9FF", "#B9F2FF", "#E0FFFF"],
    }
    return gradients.get(tier, ["#CCCCCC", "#FFFFFF"])


def _create_sparkle_animation(width: int = 40, height: int = 3) -> List[str]:
    """Create an ASCII sparkle animation."""
    sparkles = [
        "✨ ⭐ ✨ ⭐ ✨ ⭐ ✨ ⭐ ✨ ⭐",
        "⭐ ✨ ⭐ ✨ ⭐ ✨ ⭐ ✨ ⭐ ✨",
        "✨ ⭐ ✨ ⭐ ✨ ⭐ ✨ ⭐ ✨ ⭐",
    ]
    return sparkles


def _create_progress_bar(progress: float, width: int = 30, tier_color: str = "#FFFFFF") -> str:
    """Create a beautiful progress bar with gradient color."""
    from rich.console import Console
    from rich.bar import Bar

    # Clamp progress to 0-1
    progress = max(0.0, min(1.0, progress))

    # Create bar representation
    filled = int(progress * width)
    empty = width - filled

    bar = "█" * filled + "░" * empty
    return f"[{tier_color}]{bar}[/] {progress*100:.1f}%"


def display_achievement_unlocked(
    achievement: Achievement,
    console: Optional[object] = None
) -> None:
    """
    Display a gorgeous celebration when an achievement is unlocked.

    Creates:
    - Animated border with sparkles
    - Tier-colored badge
    - XP reward display
    - Confetti-style animation

    Args:
        achievement: The Achievement that was unlocked
        console: Optional Rich Console for custom output (uses default if None)
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align
        import time

        if console is None:
            console = Console()

        # Get tier information
        tier = achievement.tier
        gradient = _get_tier_color_gradient(tier)
        tier_color = tier.color

        # Create sparkle top
        sparkles = _create_sparkle_animation()

        # Build the celebration panel
        lines = [
            "",
            Align.center(Text(sparkles[0], style=f"bold {tier_color}")),
            Align.center(Text(achievement.icon, style=f"bold {tier_color} on black")),
            Align.center(Text(achievement.name, style=f"bold {tier_color}")),
            Align.center(Text(achievement.description, style="dim white")),
            "",
            Align.center(Text(f"XP: +{achievement.xp_reward}", style=f"bold yellow")),
            Align.center(Text(f"Tier: {tier.tier_name.upper()}", style=f"bold {tier_color}")),
            "",
            Align.center(Text(sparkles[2], style=f"bold {tier_color}")),
            "",
        ]

        # Create panel with tier-colored border
        panel = Panel(
            "\n".join(str(line) for line in lines),
            title=f"🎉 ACHIEVEMENT UNLOCKED 🎉",
            style=f"bold {tier_color} on black",
            expand=False,
        )

        console.print(panel)

    except ImportError:
        # Fallback if Rich is not available
        print(f"\n✓ Achievement Unlocked: {achievement.name}")
        print(f"  {achievement.description}")
        print(f"  XP Earned: {achievement.xp_reward}\n")


def display_progress_bar(
    achievement: Achievement,
    progress: AchievementProgress,
    console: Optional[object] = None,
) -> None:
    """
    Display a progress bar for an in-progress achievement.

    Args:
        achievement: The Achievement being tracked
        progress: Current progress toward the achievement
        console: Optional Rich Console
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text

        if console is None:
            console = Console()

        tier = achievement.tier
        tier_color = tier.color

        # Calculate progress percentage
        percent = progress.progress_percent(achievement.required_value)

        # Create progress representation
        bar_width = 30
        filled = int((percent / 100.0) * bar_width)
        empty = bar_width - filled
        bar = "█" * filled + "░" * empty

        # Create table for nice alignment
        table = Table.grid(padding=(0, 2))

        table.add_row(
            Text(achievement.icon, style=f"{tier_color}"),
            Text(achievement.name, style="bold"),
            Text(f"[{tier_color}]{bar}[/] {percent:.1f}%", justify="right"),
        )

        table.add_row(
            Text("", style=f"{tier_color}"),
            Text(achievement.description, style="dim"),
            Text(f"{progress.current_value}/{achievement.required_value}", justify="right", style="dim"),
        )

        console.print(table)

    except ImportError:
        # Fallback
        percent = progress.progress_percent(achievement.required_value)
        print(f"  {achievement.name}: {progress.current_value}/{achievement.required_value} ({percent:.1f}%)")


def display_achievement_stats(
    stats: dict,
    console: Optional[object] = None,
) -> None:
    """
    Display beautiful achievement statistics.

    Shows:
    - Total unlocked vs total achievements
    - By-tier breakdown with colors
    - Total XP earned

    Args:
        stats: Stats dictionary from AchievementManager.get_achievement_stats()
        console: Optional Rich Console
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text
        from rich.progress import Progress

        if console is None:
            console = Console()

        # Create summary table
        summary = Table(title="Achievement Statistics", show_header=True)
        summary.add_column("Stat", style="bold")
        summary.add_column("Value", justify="right")

        total = stats.get("total", 0)
        unlocked = stats.get("unlocked", 0)
        percent = stats.get("percent", 0.0)

        summary.add_row(
            "Total Achievements",
            Text(f"{total}", style="bold cyan"),
        )
        summary.add_row(
            "Unlocked",
            Text(f"{unlocked}", style="bold green"),
        )
        summary.add_row(
            "Progress",
            Text(f"{percent:.1f}%", style="bold yellow"),
        )
        summary.add_row(
            "Total XP Earned",
            Text(f"{stats.get('total_xp', 0)}", style="bold magenta"),
        )

        console.print(summary)

        # Create tier breakdown table
        by_tier = stats.get("by_tier", {})
        if by_tier:
            console.print()
            tiers_table = Table(title="By Tier", show_header=True)
            tiers_table.add_column("Tier", style="bold")
            tiers_table.add_column("Unlocked", justify="right")
            tiers_table.add_column("Total", justify="right")
            tiers_table.add_column("Progress", justify="right")

            tier_colors = {
                "bronze": "#CD7F32",
                "silver": "#C0C0C0",
                "gold": "#FFD700",
                "platinum": "#E5E4E2",
                "diamond": "#B9F2FF",
            }

            for tier_name in ["bronze", "silver", "gold", "platinum", "diamond"]:
                if tier_name in by_tier:
                    tier_stats = by_tier[tier_name]
                    color = tier_colors.get(tier_name, "white")
                    tiers_table.add_row(
                        Text(tier_name.upper(), style=f"bold {color}"),
                        Text(str(tier_stats.get("unlocked", 0)), style=f"{color}"),
                        Text(str(tier_stats.get("total", 0)), style="dim"),
                        Text(f"{tier_stats.get('percent', 0):.1f}%", style=f"{color}"),
                    )

            console.print(tiers_table)

    except ImportError:
        # Fallback
        total = stats.get("total", 0)
        unlocked = stats.get("unlocked", 0)
        percent = stats.get("percent", 0.0)
        print(f"\nAchievement Stats:")
        print(f"  Total: {unlocked}/{total} ({percent:.1f}%)")
        print(f"  XP: {stats.get('total_xp', 0)}\n")


def display_next_achievements(
    achievements: List[tuple[Achievement, AchievementProgress]],
    limit: int = 5,
    console: Optional[object] = None,
) -> None:
    """
    Display the next achievements to work toward.

    Shows achievements closest to completion first, with progress bars.

    Args:
        achievements: List of (Achievement, Progress) tuples from get_next_achievements
        limit: Maximum number to display
        console: Optional Rich Console
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text

        if console is None:
            console = Console()

        if not achievements:
            console.print("[dim]No achievements in progress yet![/]")
            return

        table = Table(title="Next Achievements", show_header=True)
        table.add_column("", width=3, style="bold")
        table.add_column("Achievement", style="bold")
        table.add_column("Progress", justify="center")
        table.add_column("Remaining", justify="right", style="dim")

        for achievement, progress in achievements[:limit]:
            tier = achievement.tier
            tier_color = tier.color

            percent = progress.progress_percent(achievement.required_value)
            remaining = achievement.required_value - progress.current_value

            # Create visual progress bar
            bar_width = 20
            filled = int((percent / 100.0) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)

            table.add_row(
                achievement.icon,
                Text(achievement.name, style=f"{tier_color}"),
                Text(f"[{tier_color}]{bar}[/] {percent:.0f}%"),
                Text(f"{remaining} left", style="dim"),
            )

        console.print(table)

    except ImportError:
        # Fallback
        for achievement, progress in achievements[:limit]:
            percent = progress.progress_percent(achievement.required_value)
            print(f"  {achievement.icon} {achievement.name}: {percent:.0f}%")


# Global achievement manager instance
achievement_manager = AchievementManager()


# Self-teaching note:
#
# This file demonstrates:
# - Enums for type-safe constants (Achievement types and tiers)
# - Dataclasses for structured data (@dataclass decorator)
# - Type hints for complex types (Dict, List, Optional)
# - JSON serialization for persistence
# - Datetime handling for timestamps
# - Manager pattern for centralized control
#
# The learner will encounter this AFTER mastering:
# - Level 3: Classes and functions
# - Level 4: Collections and comprehensions
# - Level 5: Dataclasses and type hints
# - Level 6: File I/O and JSON
#
# This demonstrates a complete achievement system like in
# games, fitness apps, and learning platforms.
